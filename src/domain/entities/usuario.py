import re
from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID, uuid4

# Roles/Perfis válidos no escopo do sistema
PERFIS_PERMITIDOS = {"ADMIN_SAAS", "DONO", "GERENTE"}

@dataclass
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
        # Validação do nome
        if not self.nome.strip():
            raise ValueError("O nome do usuário não pode ser vazio.")
            
        # Validação do formato de email simples
        if not re.match(r"^[^@]+@[^@]+\.[^@]+$", self.email):
            raise ValueError(f"O formato do e-mail '{self.email}' é inválido.")
            
        # Validação do perfil (Role)
        if self.role not in PERFIS_PERMITIDOS:
            raise ValueError(f"Perfil '{self.role}' inválido. Deve ser um dos seguintes: {', '.join(PERFIS_PERMITIDOS)}")
            
        # Validação de hash da senha
        if not self.senha_hash:
            raise ValueError("O hash da senha não pode ser vazio.")
