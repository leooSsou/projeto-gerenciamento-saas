from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID
from src.domain.entities.usuario import Usuario

class UsuarioRepository(ABC):
    """
    Interface/Contrato abstrato para persistência de Usuários.
    """
    
    @abstractmethod
    def salvar(self, usuario: Usuario) -> Usuario:
        """
        Salva ou atualiza um Usuário na persistência.
        Retorna a entidade salva (com ID se aplicável).
        """
        pass

    @abstractmethod
    def obter_por_email(self, email: str) -> Optional[Usuario]:
        """
        Busca um Usuário cadastrado pelo e-mail.
        """
        pass

    @abstractmethod
    def obter_por_id(self, id: UUID) -> Optional[Usuario]:
        """
        Busca um Usuário cadastrado pelo ID.
        """
        pass
