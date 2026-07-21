from abc import ABC, abstractmethod
from typing import List
from uuid import UUID
from src.domain.entities.estoque_movimentacao import EstoqueMovimentacao

class EstoqueMovimentacaoRepository(ABC):
    """
    Interface/Contrato abstrato para persistência do histórico (ledger) de movimentações de estoque.
    """

    @abstractmethod
    def salvar(self, movimentacao: EstoqueMovimentacao) -> EstoqueMovimentacao:
        """
        Registra uma movimentação no ledger de estoque.
        """
        pass

    @abstractmethod
    def listar_por_loja_e_produto(
        self, loja_id: UUID, produto_id: UUID, tenant_id: UUID
    ) -> List[EstoqueMovimentacao]:
        """
        Recupera o histórico de movimentações de um produto em uma loja específica.
        """
        pass

    @abstractmethod
    def listar_todas(self, tenant_id: UUID) -> List[EstoqueMovimentacao]:
        """
        Recupera todas as movimentações do tenant.
        """
        pass
