from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID
from src.domain.entities.tenant import Tenant

class TenantRepository(ABC):
    """
    Interface/Contrato abstrato para persistência de Tenants.
    """
    
    @abstractmethod
    def salvar(self, tenant: Tenant) -> Tenant:
        """
        Salva ou atualiza um Tenant na persistência.
        Retorna a entidade salva (com ID e timestamps se aplicável).
        """
        pass

    @abstractmethod
    def obter_por_cnpj(self, cnpj: str) -> Optional[Tenant]:
        """
        Busca um Tenant cadastrado pelo CNPJ.
        """
        pass

    @abstractmethod
    def obter_por_id(self, id: UUID) -> Optional[Tenant]:
        """
        Busca um Tenant cadastrado pelo ID.
        """
        pass
