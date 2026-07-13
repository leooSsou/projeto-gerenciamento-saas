from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID
from src.domain.entities.loja import Loja

class LojaRepository(ABC):
    """
    Interface/Contrato abstrato para persistência de Lojas.
    """
    
    @abstractmethod
    def salvar(self, loja: Loja) -> Loja:
        """
        Salva ou atualiza uma Loja na persistência.
        Retorna a entidade salva.
        """
        pass

    @abstractmethod
    def obter_por_id(self, id: UUID, tenant_id: UUID) -> Optional[Loja]:
        """
        Busca uma Loja cadastrada pelo ID e tenant_id.
        """
        pass

    @abstractmethod
    def obter_por_cnpj(self, cnpj: str, tenant_id: UUID) -> Optional[Loja]:
        """
        Busca uma Loja cadastrada pelo CNPJ e tenant_id.
        """
        pass

    @abstractmethod
    def listar_todas(self, tenant_id: UUID) -> List[Loja]:
        """
        Lista todas as lojas cadastradas para um determinado Tenant.
        """
        pass
