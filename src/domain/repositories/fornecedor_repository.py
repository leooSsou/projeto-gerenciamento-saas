from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID
from src.domain.entities.fornecedor import Fornecedor

class FornecedorRepository(ABC):
    """
    Interface/Contrato abstrato para persistência de Fornecedores.
    """
    
    @abstractmethod
    def salvar(self, fornecedor: Fornecedor) -> Fornecedor:
        """
        Salva ou atualiza um Fornecedor na persistência.
        Retorna a entidade salva.
        """
        pass

    @abstractmethod
    def obter_por_id(self, id: UUID, tenant_id: UUID) -> Optional[Fornecedor]:
        """
        Busca um Fornecedor cadastrado pelo ID e tenant_id.
        """
        pass

    @abstractmethod
    def obter_por_cnpj(self, cnpj: str, tenant_id: UUID) -> Optional[Fornecedor]:
        """
        Busca um Fornecedor cadastrado pelo CNPJ e tenant_id.
        """
        pass

    @abstractmethod
    def listar_todos(self, tenant_id: UUID) -> List[Fornecedor]:
        """
        Lista todos os fornecedores cadastrados para um determinado Tenant.
        """
        pass
