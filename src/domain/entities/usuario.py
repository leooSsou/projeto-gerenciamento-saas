import re
from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID, uuid4

# Roles/Perfis válidos no escopo do sistema
PERFIS_PERMITIDOS = {"ADMIN_SAAS", "DONO", "GERENTE"}

@dataclass(frozen=True)
class Usuario:
    """
    Entidade de domínio pura que representa um usuário/colaborador do sistema.
    """
    nome: str
    email: str
    senha_hash: str
    role: str
    tenant_id: UUID
    id: UUID = field(default_factory=uuid4)
    loja_atribuida_id: Optional[UUID] = None

    def __post_init__(self) -> None:
        # Validações de tipo
        if not isinstance(self.nome, str) or not self.nome.strip():
            raise ValueError("O nome do usuário deve ser uma string não vazia.")
        object.__setattr__(self, "nome", self.nome.strip())
            
        if not isinstance(self.email, str):
            raise ValueError("O e-mail deve ser uma string.")
            
        # Normalização do e-mail (remove espaços e transforma em minúsculo)
        email_normalizado = self.email.strip().lower()
        object.__setattr__(self, "email", email_normalizado)
            
        # Validação do formato de email com regex aprimorada
        # Evita e-mails com pontos seguidos ou formatos simplistas demais
        regex_email = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(regex_email, email_normalizado) or ".." in email_normalizado:
            raise ValueError(f"O formato do e-mail '{self.email}' é inválido.")
            
        # Validação do perfil (Role)
        if not isinstance(self.role, str) or self.role not in PERFIS_PERMITIDOS:
            raise ValueError(f"Perfil '{self.role}' inválido. Deve ser um dos seguintes: {', '.join(PERFIS_PERMITIDOS)}")
            
        # Validação de hash da senha
        if not isinstance(self.senha_hash, str) or not self.senha_hash.strip():
            raise ValueError("O hash da senha deve ser uma string não vazia.")

        # Validação cruzada: perfil de GERENTE exige vínculo com loja física
        if self.role == "GERENTE" and self.loja_atribuida_id is None:
            raise ValueError("Usuários com perfil de GERENTE devem estar associados a uma loja.")
            
        # Perfis DONO ou ADMIN_SAAS gerenciam o tenant como um todo e não podem estar restritos a uma única loja
        if self.role in {"DONO", "ADMIN_SAAS"} and self.loja_atribuida_id is not None:
            raise ValueError(f"Usuários com perfil de {self.role} não devem ter uma loja específica atribuída.")

