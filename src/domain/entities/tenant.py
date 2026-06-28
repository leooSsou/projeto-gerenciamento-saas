import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4

@dataclass
class Tenant:
    """
    Entidade de domínio pura que representa uma empresa cliente do SaaS.
    """
    nome_fantasia: str
    razao_social: str
    cnpj: str
    id: UUID = field(default_factory=uuid4)
    data_cadastro: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        # Remove qualquer caractere não numérico do CNPJ
        self.cnpj = re.sub(r"\D", "", self.cnpj)
        
        # Validações de negócio
        if len(self.cnpj) != 14:
            raise ValueError("O CNPJ deve conter exatamente 14 dígitos numéricos.")
            
        if not self.nome_fantasia.strip():
            raise ValueError("O nome fantasia não pode ser vazio.")
            
        if not self.razao_social.strip():
            raise ValueError("A razão social não pode ser vazia.")
