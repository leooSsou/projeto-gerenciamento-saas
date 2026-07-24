from dataclasses import dataclass
from uuid import UUID
from typing import List, Optional

from src.domain.entities.fornecedor import Fornecedor
from src.domain.entities.produto import Produto
from src.domain.repositories.fornecedor_repository import FornecedorRepository
from src.domain.repositories.produto_repository import ProdutoRepository
from src.domain.repositories.estoque_saldo_repository import EstoqueSaldoRepository
from src.domain.services.nfe_parser import NFeParserService, NFeDados, ItemNFe

@dataclass(frozen=True)
class ImportarNFeInput:
    xml_content: bytes | str
    tenant_id: UUID
    markup_padrao: float = 0.5  # 50% de markup por padrão para novos produtos


@dataclass(frozen=True)
class ItemImportadoOutput:
    produto: Produto
    quantidade_importada: float
    valor_unitario_nfe: float
    novo_produto_cadastrado: bool


@dataclass(frozen=True)
class ImportarNFeOutput:
    fornecedor: Fornecedor
    itens_processados: List[ItemImportadoOutput]


class ImportarEstoqueNFe:
    """
    Caso de Uso: Processar o XML de NF-e, auto-cadastrar/atualizar fornecedor e produtos,
    recalcular custo médio ponderado e preços de venda sugeridos por Markup.
    """
    def __init__(
        self,
        fornecedor_repo: FornecedorRepository,
        produto_repo: ProdutoRepository,
        saldo_repo: EstoqueSaldoRepository
    ) -> None:
        self.fornecedor_repo = fornecedor_repo
        self.produto_repo = produto_repo
        self.saldo_repo = saldo_repo

    def executar(self, input_data: ImportarNFeInput) -> ImportarNFeOutput:
        # 1. Faz o parsing do XML da NF-e
        nfe_dados: NFeDados = NFeParserService.parse_xml(input_data.xml_content)

        # 2. Recupera ou cadastra o Fornecedor (Emitente da NF-e)
        fornecedor = self.fornecedor_repo.obter_por_cnpj(
            cnpj=nfe_dados.emitente.cnpj,
            tenant_id=input_data.tenant_id
        )

        if not fornecedor:
            novo_fornecedor = Fornecedor(
                nome_fantasia=nfe_dados.emitente.nome_fantasia or nfe_dados.emitente.razao_social,
                razao_social=nfe_dados.emitente.razao_social,
                cnpj=nfe_dados.emitente.cnpj,
                tenant_id=input_data.tenant_id
            )
            fornecedor = self.fornecedor_repo.salvar(novo_fornecedor)

        # 3. Processa cada item da NF-e
        itens_output: List[ItemImportadoOutput] = []

        for item in nfe_dados.itens:
            produto_existente: Optional[Produto] = None

            # Tenta encontrar produto existente por código de barras primeiro
            if item.codigo_barras:
                produto_existente = self.produto_repo.obter_por_codigo_barras(
                    codigo_barras=item.codigo_barras,
                    tenant_id=input_data.tenant_id
                )

            # Se não encontrou por código de barras, busca por SKU (cProd)
            if not produto_existente:
                produto_existente = self.produto_repo.obter_por_sku(
                    sku=item.codigo_produto,
                    tenant_id=input_data.tenant_id
                )

            if produto_existente:
                # Produto já existe: recalcula Custo Médio Ponderado real baseado nas quantidades em todas as lojas
                saldos = self.saldo_repo.listar_todos(input_data.tenant_id)
                qtd_atual = sum(s.quantidade for s in saldos if s.produto_id == produto_existente.id)
                
                denominador = qtd_atual + item.quantidade
                if denominador > 0:
                    novo_custo_medio = round(
                        ((qtd_atual * produto_existente.preco_custo) + (item.quantidade * item.valor_unitario))
                        / denominador,
                        2
                    )
                else:
                    novo_custo_medio = round(item.valor_unitario, 2)

                novo_preco_venda = Produto.calcular_preco_venda(
                    preco_custo=novo_custo_medio,
                    markup=produto_existente.markup
                )

                produto_atualizado = Produto(
                    id=produto_existente.id,
                    nome=produto_existente.nome,
                    sku=produto_existente.sku,
                    preco_custo=novo_custo_medio,
                    preco_venda=novo_preco_venda,
                    markup=produto_existente.markup,
                    tenant_id=input_data.tenant_id,
                    codigo_barras=item.codigo_barras or produto_existente.codigo_barras,
                    fornecedor_id=fornecedor.id,
                    ativo=produto_existente.ativo
                )
                produto_salvo = self.produto_repo.salvar(produto_atualizado)
                is_novo = False
            else:
                # Produto novo: cadastra no catálogo
                custo_unitario = round(item.valor_unitario, 2)
                preco_venda_sugerido = Produto.calcular_preco_venda(
                    preco_custo=custo_unitario,
                    markup=input_data.markup_padrao
                )

                novo_produto = Produto(
                    nome=item.nome,
                    sku=item.codigo_produto,
                    preco_custo=custo_unitario,
                    preco_venda=preco_venda_sugerido,
                    markup=input_data.markup_padrao,
                    tenant_id=input_data.tenant_id,
                    codigo_barras=item.codigo_barras,
                    fornecedor_id=fornecedor.id
                )
                produto_salvo = self.produto_repo.salvar(novo_produto)
                is_novo = True

            itens_output.append(ItemImportadoOutput(
                produto=produto_salvo,
                quantidade_importada=item.quantidade,
                valor_unitario_nfe=item.valor_unitario,
                novo_produto_cadastrado=is_novo
            ))

        return ImportarNFeOutput(
            fornecedor=fornecedor,
            itens_processados=itens_output
        )
