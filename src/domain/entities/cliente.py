from dataclasses import dataclass, field
from uuid import UUID, uuid4
import re

@dataclass(frozen=True)
class Cliente:
    """
    Entidade de domínio pura que representa um Cliente do inquilino.
    """
    nome: str
    email: str
    documento: str
    tenant_id: UUID
    id: UUID = field(default_factory=uuid4)
    ativo: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.nome, str) or not self.nome.strip():
            raise ValueError("O nome do cliente deve ser uma string não vazia.")
        object.__setattr__(self, "nome", self.nome.strip())

        if not isinstance(self.email, str) or not self.email.strip():
            raise ValueError("O e-mail deve ser uma string não vazia.")
        object.__setattr__(self, "email", self.email.strip())

        # Validação simples de e-mail
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", self.email):
            raise ValueError("E-mail inválido.")

        if not isinstance(self.documento, str):
            raise ValueError("O documento deve ser uma string.")
        
        # Limpa caracteres não numéricos
        doc_limpo = re.sub(r"\D", "", self.documento)
        object.__setattr__(self, "documento", doc_limpo)

        # Valida CPF (11 dígitos) ou CNPJ (14 dígitos)
        if len(doc_limpo) == 11:
            if not self._validar_cpf(doc_limpo):
                raise ValueError("CPF inválido.")
        elif len(doc_limpo) == 14:
            if not self._validar_cnpj(doc_limpo):
                raise ValueError("CNPJ inválido.")
        else:
            raise ValueError("O documento deve ser um CPF (11 dígitos) ou CNPJ (14 dígitos) válido.")

        if not isinstance(self.tenant_id, UUID):
            raise ValueError("O tenant_id deve ser um UUID válido.")

        if not isinstance(self.ativo, bool):
            raise ValueError("O campo ativo deve ser um booleano.")

    @staticmethod
    def _validar_cpf(cpf: str) -> bool:
        if len(cpf) != 11 or len(set(cpf)) == 1:
            return False
        # Validação do primeiro dígito
        soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
        digito1 = (soma * 10) % 11
        if digito1 == 10:
            digito1 = 0
        if int(cpf[9]) != digito1:
            return False
        # Validação do segundo dígito
        soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
        digito2 = (soma * 10) % 11
        if digito2 == 10:
            digito2 = 0
        return int(cpf[10]) == digito2

    @staticmethod
    def _validar_cnpj(cnpj: str) -> bool:
        # Reutiliza o validador matemático existente em Loja
        from src.domain.entities.loja import Loja
        return Loja._validar_cnpj(cnpj)
