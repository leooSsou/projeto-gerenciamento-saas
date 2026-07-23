from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID
from src.domain.entities.estoque_saldo import EstoqueSaldo

class EstoqueSaldoRepository(ABC):
    """
    Interface/Contrato abstrato para persistência de saldos de estoque.
    """
    
    @abstractmethod
    def salvar(self, saldo: EstoqueSaldo) -> EstoqueSaldo:
        """
        Salva ou atualiza um saldo de estoque.
        """
        pass

    @abstractmethod
    def obter_por_loja_e_produto(
        self, loja_id: UUID, produto_id: UUID, tenant_id: UUID
    ) -> Optional[EstoqueSaldo]:
        """
        Busca o saldo consolidado de um produto em uma loja específica sem aplicar locks.
        """
        pass

    @abstractmethod
    def obter_por_loja_e_produto_com_lock(
        self, loja_id: UUID, produto_id: UUID, tenant_id: UUID
    ) -> Optional[EstoqueSaldo]:
        """
        Busca o saldo consolidado de um produto em uma loja específica aplicando lock pessimista (SELECT FOR UPDATE).
        """
        pass

    @abstractmethod
    def listar_todos(self, tenant_id: UUID) -> List[EstoqueSaldo]:
        """
        Lista todos os saldos consolidados do tenant.
        """
        pass
