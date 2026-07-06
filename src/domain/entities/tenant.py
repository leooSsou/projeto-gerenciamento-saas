import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4

@dataclass(frozen=True)
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
        # Validação de tipos iniciais
        if not isinstance(self.nome_fantasia, str) or not self.nome_fantasia.strip():
            raise ValueError("O nome fantasia deve ser uma string não vazia.")
            
        if not isinstance(self.razao_social, str) or not self.razao_social.strip():
            raise ValueError("A razão social deve ser uma string não vazia.")

        if not isinstance(self.cnpj, str):
            raise ValueError("O CNPJ deve ser uma string.")

        # Remove qualquer caractere não numérico do CNPJ
        cnpj_limpo = re.sub(r"\D", "", self.cnpj)
        
        # Como o dataclass é frozen, usamos object.__setattr__ para mutar o campo após inicialização
        object.__setattr__(self, "cnpj", cnpj_limpo)
        
        # Validações matemáticas do CNPJ
        if not self._validar_cnpj(cnpj_limpo):
            raise ValueError("CNPJ inválido.")

    @staticmethod
    def _validar_cnpj(cnpj: str) -> bool:
        if len(cnpj) != 14 or not cnpj.isdigit():
            return False

        # Bloqueia sequências de dígitos idênticos (ex: 11111111111111)
        if len(set(cnpj)) == 1:
            return False

        # Primeiro dígito verificador
        pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        soma1 = sum(int(cnpj[i]) * pesos1[i] for i in range(12))
        resto1 = soma1 % 11
        digito1 = 0 if resto1 < 2 else 11 - resto1

        # Segundo dígito verificador
        pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        soma2 = sum(int(cnpj[i]) * pesos2[i] for i in range(13))
        resto2 = soma2 % 11
        digito2 = 0 if resto2 < 2 else 11 - resto2

        return int(cnpj[12]) == digito1 and int(cnpj[13]) == digito2

