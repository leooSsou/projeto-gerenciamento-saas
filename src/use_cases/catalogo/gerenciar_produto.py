from dataclasses import dataclass
from uuid import UUID
from typing import List

from src.domain.entities.produto import Produto
from src.domain.repositories.produto_repository import ProdutoRepository
from src.domain.exceptions.business import (
    ProdutoNaoEncontradoException,
    SkuProdutoEmUsoException,
)

@dataclass(frozen=True)
class CriarProdutoInput:
    nome: str
    sku: str
    preco_custo: float
    preco_venda: float
    markup: float
    tenant_id: UUID


@dataclass(frozen=True)
class CriarProdutoOutput:
    produto: Produto


class CriarProduto:
    """
    Caso de Uso: Criar um novo Produto no catálogo.
    """
    def __init__(self, produto_repo: ProdutoRepository) -> None:
        self.produto_repo = produto_repo

    def executar(self, input_data: CriarProdutoInput) -> CriarProdutoOutput:
        # 1. Verifica se já existe outro produto com o mesmo SKU para o tenant
        produto_existente = self.produto_repo.obter_por_sku(input_data.sku, input_data.tenant_id)
        if produto_existente:
            raise SkuProdutoEmUsoException(input_data.sku)

        # 2. Instancia a entidade de domínio Produto
        produto = Produto(
            nome=input_data.nome,
            sku=input_data.sku,
            preco_custo=input_data.preco_custo,
            preco_venda=input_data.preco_venda,
            markup=input_data.markup,
            tenant_id=input_data.tenant_id
        )

        # 3. Salva no banco
        produto_salvo = self.produto_repo.salvar(produto)

        return CriarProdutoOutput(produto=produto_salvo)


@dataclass(frozen=True)
class ObterProdutoOutput:
    produto: Produto


class ObterProduto:
    """
    Caso de Uso: Obter detalhes de um Produto pelo ID.
    """
    def __init__(self, produto_repo: ProdutoRepository) -> None:
        self.produto_repo = produto_repo

    def executar(self, produto_id: UUID, tenant_id: UUID) -> ObterProdutoOutput:
        produto = self.produto_repo.obter_por_id(produto_id, tenant_id)
        if not produto:
            raise ProdutoNaoEncontradoException(str(produto_id))

        return ObterProdutoOutput(produto=produto)


@dataclass(frozen=True)
class ListarProdutosOutput:
    produtos: List[Produto]


class ListarProdutos:
    """
    Caso de Uso: Listar todos os Produtos de um Tenant.
    """
    def __init__(self, produto_repo: ProdutoRepository) -> None:
        self.produto_repo = produto_repo

    def executar(self, tenant_id: UUID) -> ListarProdutosOutput:
        produtos = self.produto_repo.listar_todos(tenant_id)
        return ListarProdutosOutput(produtos=produtos)


@dataclass(frozen=True)
class AtualizarProdutoInput:
    id: UUID
    nome: str
    preco_custo: float
    preco_venda: float
    markup: float
    ativo: bool
    tenant_id: UUID


@dataclass(frozen=True)
class AtualizarProdutoOutput:
    produto: Produto


class AtualizarProduto:
    """
    Caso de Uso: Atualizar dados de um Produto.
    """
    def __init__(self, produto_repo: ProdutoRepository) -> None:
        self.produto_repo = produto_repo

    def executar(self, input_data: AtualizarProdutoInput) -> AtualizarProdutoOutput:
        # 1. Recupera o produto existente
        produto = self.produto_repo.obter_por_id(input_data.id, input_data.tenant_id)
        if not produto:
            raise ProdutoNaoEncontradoException(str(input_data.id))

        # 2. Cria nova instância (SKU e Tenant permanecem imutáveis)
        produto_atualizado = Produto(
            nome=input_data.nome,
            sku=produto.sku,
            preco_custo=input_data.preco_custo,
            preco_venda=input_data.preco_venda,
            markup=input_data.markup,
            tenant_id=produto.tenant_id,
            id=produto.id,
            ativo=input_data.ativo
        )

        # 3. Salva no banco
        produto_salvo = self.produto_repo.salvar(produto_atualizado)

        return AtualizarProdutoOutput(produto=produto_salvo)
