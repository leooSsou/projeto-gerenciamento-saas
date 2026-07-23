from dataclasses import dataclass, field
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional

@dataclass(frozen=True)
class EstoqueMovimentacao:
    """
    Entidade de domínio pura que representa um registro individual (ledger) de movimentação de estoque.
    """
    loja_id: UUID
    produto_id: UUID
    tipo: str
    quantidade: int
    motivo: str
    tenant_id: UUID
    id: UUID = field(default_factory=uuid4)
    data_movimentacao: Optional[datetime] = None

    def __post_init__(self) -> None:
        if not isinstance(self.loja_id, UUID):
            raise ValueError("O loja_id deve ser um UUID válido.")
        if not isinstance(self.produto_id, UUID):
            raise ValueError("O produto_id deve ser um UUID válido.")
        if not isinstance(self.tipo, str) or self.tipo not in ["ENTRADA", "SAIDA"]:
            raise ValueError("O tipo de movimentação deve ser obrigatoriamente 'ENTRADA' ou 'SAIDA'.")
        if not isinstance(self.quantidade, int) or self.quantidade <= 0:
            raise ValueError("A quantidade de movimentação deve ser um número inteiro maior que zero.")
        if self.quantidade > 1000000:
            raise ValueError("A quantidade de movimentação por operação não pode exceder 1.000.000 unidades.")
        if not isinstance(self.motivo, str) or not self.motivo.strip():
            raise ValueError("O motivo da movimentação deve ser uma string não vazia.")
        object.__setattr__(self, "motivo", self.motivo.strip())
        if not isinstance(self.tenant_id, UUID):
            raise ValueError("O tenant_id deve ser um UUID válido.")
        if not isinstance(self.id, UUID):
            raise ValueError("O id deve ser um UUID válido.")
        if self.data_movimentacao is not None and not isinstance(self.data_movimentacao, datetime):
            raise ValueError("A data_movimentacao deve ser um objeto datetime válido.")
