from dataclasses import dataclass
from uuid import UUID

from src.domain.entities.estoque_saldo import EstoqueSaldo
from src.domain.entities.estoque_movimentacao import EstoqueMovimentacao
from src.domain.repositories.estoque_saldo_repository import EstoqueSaldoRepository
from src.domain.repositories.estoque_movimentacao_repository import EstoqueMovimentacaoRepository
from src.domain.repositories.loja_repository import LojaRepository
from src.domain.repositories.produto_repository import ProdutoRepository
from src.domain.exceptions.business import (
    LojaNaoEncontradaException,
    ProdutoNaoEncontradoException,
    EstoqueInsuficienteException,
)

@dataclass(frozen=True)
class RegistrarMovimentacaoEstoqueInput:
    loja_id: UUID
    produto_id: UUID
    tipo: str  # "ENTRADA" ou "SAIDA"
    quantidade: int
    motivo: str
    tenant_id: UUID


@dataclass(frozen=True)
class RegistrarMovimentacaoEstoqueOutput:
    saldo: EstoqueSaldo
    movimentacao: EstoqueMovimentacao


class RegistrarMovimentacaoEstoque:
    """
    Caso de Uso: Registrar movimentações de estoque (ENTRADA/SAIDA)
    com lock pessimista e validações de segurança multi-tenant (BOLA).
    """
    def __init__(
        self,
        saldo_repo: EstoqueSaldoRepository,
        movimentacao_repo: EstoqueMovimentacaoRepository,
        loja_repo: LojaRepository,
        produto_repo: ProdutoRepository,
    ) -> None:
        self.saldo_repo = saldo_repo
        self.movimentacao_repo = movimentacao_repo
        self.loja_repo = loja_repo
        self.produto_repo = produto_repo

    def executar(self, input_data: RegistrarMovimentacaoEstoqueInput) -> RegistrarMovimentacaoEstoqueOutput:
        # 1. Segurança contra BOLA: Verifica se a loja existe e pertence ao tenant
        loja = self.loja_repo.obter_por_id(input_data.loja_id, input_data.tenant_id)
        if not loja:
            raise LojaNaoEncontradaException(str(input_data.loja_id))

        # 2. Segurança contra BOLA: Verifica se o produto existe e pertence ao tenant
        produto = self.produto_repo.obter_por_id(input_data.produto_id, input_data.tenant_id)
        if not produto:
            raise ProdutoNaoEncontradoException(str(input_data.produto_id))

        # 3. Trava Pessimista: Obtém o saldo travando a linha correspondente no banco
        saldo = self.saldo_repo.obter_por_loja_e_produto_com_lock(
            input_data.loja_id, input_data.produto_id, input_data.tenant_id
        )

        # 4. Lógica de cálculo de estoque
        if input_data.tipo == "ENTRADA":
            nova_quantidade = (saldo.quantidade + input_data.quantidade) if saldo else input_data.quantidade
        elif input_data.tipo == "SAIDA":
            quantidade_disponivel = saldo.quantidade if saldo else 0
            if quantidade_disponivel < input_data.quantidade:
                raise EstoqueInsuficienteException(
                    produto_id=str(input_data.produto_id),
                    loja_id=str(input_data.loja_id),
                    disponivel=quantidade_disponivel,
                    solicitado=input_data.quantidade,
                )
            nova_quantidade = quantidade_disponivel - input_data.quantidade
        else:
            raise ValueError("O tipo de movimentação deve ser obrigatoriamente 'ENTRADA' ou 'SAIDA'.")

        # 5. Atualização ou criação do Saldo de Estoque
        if saldo:
            saldo_atualizado = EstoqueSaldo(
                id=saldo.id,
                loja_id=saldo.loja_id,
                produto_id=saldo.produto_id,
                quantidade=nova_quantidade,
                tenant_id=saldo.tenant_id,
            )
        else:
            saldo_atualizado = EstoqueSaldo(
                loja_id=input_data.loja_id,
                produto_id=input_data.produto_id,
                quantidade=nova_quantidade,
                tenant_id=input_data.tenant_id,
            )

        saldo_salvo = self.saldo_repo.salvar(saldo_atualizado)

        # 6. Gravação do Histórico (Ledger) imutável
        mov = EstoqueMovimentacao(
            loja_id=input_data.loja_id,
            produto_id=input_data.produto_id,
            tipo=input_data.tipo,
            quantidade=input_data.quantidade,
            motivo=input_data.motivo,
            tenant_id=input_data.tenant_id,
        )
        mov_salva = self.movimentacao_repo.salvar(mov)

        return RegistrarMovimentacaoEstoqueOutput(saldo=saldo_salvo, movimentacao=mov_salva)
