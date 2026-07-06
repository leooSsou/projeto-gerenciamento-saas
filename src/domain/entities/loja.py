import re
from dataclasses import dataclass, field
from uuid import UUID, uuid4

@dataclass(frozen=True)
class Loja:
    """
    Entidade de domínio pura que representa uma filial física de um Tenant.
    """
    nome: str
    cnpj: str
    endereco: str
    tenant_id: UUID
    id: UUID = field(default_factory=uuid4)
    ativo: bool = True

    def __post_init__(self) -> None:
        # Validação de tipos iniciais
        if not isinstance(self.nome, str) or not self.nome.strip():
            raise ValueError("O nome da loja deve ser uma string não vazia.")
        object.__setattr__(self, "nome", self.nome.strip())
            
        if not isinstance(self.cnpj, str):
            raise ValueError("O CNPJ deve ser uma string.")
            
        if not isinstance(self.endereco, str) or not self.endereco.strip():
            raise ValueError("O endereço deve ser uma string não vazia.")
        object.__setattr__(self, "endereco", self.endereco.strip())

        if not isinstance(self.tenant_id, UUID):
            raise ValueError("O tenant_id deve ser um UUID válido.")
            
        if not isinstance(self.ativo, bool):
            raise ValueError("O campo ativo deve ser um booleano.")

        # Remove qualquer caractere não numérico do CNPJ
        cnpj_limpo = re.sub(r"\D", "", self.cnpj)
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
