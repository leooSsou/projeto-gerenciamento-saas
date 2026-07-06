from uuid import UUID
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

class HasTenant:
    """
    Mixin do SQLAlchemy 2.0 para adicionar a coluna tenant_id e garantir
    o isolamento lógico multi-tenant nas tabelas de dados.
    """
    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
