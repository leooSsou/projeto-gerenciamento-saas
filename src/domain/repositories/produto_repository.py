from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID
from src.domain.entities.produto import Produto

class ProdutoRepository(ABC):
    """
    Interface/Contrato abstrato para persistência de Produtos.
    """
    
    @abstractmethod
    def salvar(self, produto: Produto) -> Produto:
        """
        Salva ou atualiza um Produto na persistência.
        Retorna a entidade salva.
        """
        pass

    @abstractmethod
    def obter_por_id(self, id: UUID, tenant_id: UUID) -> Optional[Produto]:
        """
        Busca um Produto cadastrado pelo ID e tenant_id.
        """
        pass

    @abstractmethod
    def obter_por_sku(self, sku: str, tenant_id: UUID) -> Optional[Produto]:
        """
        Busca um Produto cadastrado pelo SKU e tenant_id.
        """
        pass

    @abstractmethod
    def listar_todos(self, tenant_id: UUID) -> List[Produto]:
        """
        Lista todos os produtos cadastrados para um determinado Tenant.
        """
        pass
