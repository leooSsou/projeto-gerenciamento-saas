from dataclasses import dataclass, field
from uuid import UUID, uuid4

@dataclass(frozen=True)
class EstoqueSaldo:
    """
    Entidade de domínio pura que representa o saldo consolidado de um produto em uma loja.
    """
    loja_id: UUID
    produto_id: UUID
    quantidade: int
    tenant_id: UUID
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if not isinstance(self.loja_id, UUID):
            raise ValueError("O loja_id deve ser um UUID válido.")
        if not isinstance(self.produto_id, UUID):
            raise ValueError("O produto_id deve ser um UUID válido.")
        if not isinstance(self.quantidade, int) or self.quantidade < 0:
            raise ValueError("A quantidade de estoque deve ser um número inteiro maior ou igual a zero.")
        if self.quantidade > 1000000000:
            raise ValueError("A quantidade de estoque não pode exceder 1.000.000.000 unidades.")
        if not isinstance(self.tenant_id, UUID):
            raise ValueError("O tenant_id deve ser um UUID válido.")
        if not isinstance(self.id, UUID):
            raise ValueError("O id deve ser um UUID válido.")
