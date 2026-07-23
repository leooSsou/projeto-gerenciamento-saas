from dataclasses import dataclass, field
from uuid import UUID, uuid4
from typing import Optional

@dataclass(frozen=True)
class Produto:
    """
    Entidade de domínio pura que representa um Produto no catálogo.
    """
    nome: str
    sku: str
    preco_custo: float
    preco_venda: float
    markup: float
    tenant_id: UUID
    codigo_barras: Optional[str] = None
    fornecedor_id: Optional[UUID] = None
    id: UUID = field(default_factory=uuid4)
    ativo: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.nome, str) or not self.nome.strip():
            raise ValueError("O nome do produto deve ser uma string não vazia.")
        object.__setattr__(self, "nome", self.nome.strip())

        if not isinstance(self.sku, str) or not self.sku.strip():
            raise ValueError("O SKU do produto deve ser uma string não vazia.")
        object.__setattr__(self, "sku", self.sku.strip())

        if not isinstance(self.preco_custo, (int, float)) or self.preco_custo < 0:
            raise ValueError("O preço de custo do produto deve ser maior ou igual a zero.")

        if not isinstance(self.preco_venda, (int, float)) or self.preco_venda < 0:
            raise ValueError("O preço de venda do produto deve ser maior ou igual a zero.")

        if not isinstance(self.markup, (int, float)):
            raise ValueError("O markup deve ser um número real.")

        if not isinstance(self.tenant_id, UUID):
            raise ValueError("O tenant_id deve ser um UUID válido.")

        if self.codigo_barras is not None:
            if not isinstance(self.codigo_barras, str):
                raise ValueError("O código de barras deve ser uma string.")
            object.__setattr__(self, "codigo_barras", self.codigo_barras.strip())

        if self.fornecedor_id is not None and not isinstance(self.fornecedor_id, UUID):
            raise ValueError("O fornecedor_id deve ser um UUID válido.")

        if not isinstance(self.ativo, bool):
            raise ValueError("O campo ativo deve ser um booleano.")


    @staticmethod
    def calcular_preco_venda(preco_custo: float, markup: float) -> float:
        """
        Calcula o preço de venda sugerido com base no preço de custo e markup.
        Preço de Venda = Preço de Custo * (1 + Markup)
        """
        if preco_custo < 0:
            raise ValueError("Preço de custo não pode ser negativo.")
        return round(preco_custo * (1 + markup), 2)
