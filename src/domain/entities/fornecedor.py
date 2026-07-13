from dataclasses import dataclass, field
from uuid import UUID, uuid4
import re

@dataclass(frozen=True)
class Fornecedor:
    """
    Entidade de domínio pura que representa um Fornecedor do inquilino.
    """
    nome_fantasia: str
    razao_social: str
    cnpj: str
    tenant_id: UUID
    id: UUID = field(default_factory=uuid4)
    ativo: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.nome_fantasia, str) or not self.nome_fantasia.strip():
            raise ValueError("O nome fantasia deve ser uma string não vazia.")
        object.__setattr__(self, "nome_fantasia", self.nome_fantasia.strip())

        if not isinstance(self.razao_social, str) or not self.razao_social.strip():
            raise ValueError("A razão social deve ser uma string não vazia.")
        object.__setattr__(self, "razao_social", self.razao_social.strip())

        if not isinstance(self.cnpj, str):
            raise ValueError("O CNPJ deve ser uma string.")
        
        cnpj_limpo = re.sub(r"\D", "", self.cnpj)
        object.__setattr__(self, "cnpj", cnpj_limpo)

        # Validações matemáticas do CNPJ
        from src.domain.entities.loja import Loja
        if not Loja._validar_cnpj(cnpj_limpo):
            raise ValueError("CNPJ inválido.")

        if not isinstance(self.tenant_id, UUID):
            raise ValueError("O tenant_id deve ser um UUID válido.")

        if not isinstance(self.ativo, bool):
            raise ValueError("O campo ativo deve ser um booleano.")
