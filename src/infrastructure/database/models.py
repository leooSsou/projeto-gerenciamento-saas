from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy import String, DateTime, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src.infrastructure.database.mixins import HasTenant

class Base(DeclarativeBase):
    """
    Classe base declarativa do SQLAlchemy 2.0.
    """
    pass

class TenantModel(Base):
    """
    Representação física da tabela tenants (inquilinos).
    """
    __tablename__ = "tenants"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    nome_fantasia: Mapped[str] = mapped_column(String(150), nullable=False)
    razao_social: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    cnpj: Mapped[str] = mapped_column(String(14), unique=True, nullable=False)
    data_cadastro: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False
    )

class UsuarioModel(HasTenant, Base):
    """
    Representação física da tabela usuarios (colaboradores/acesso).
    """
    __tablename__ = "usuarios"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    
    # Campo opcional para vincular à loja física (será configurado no futuro)
    loja_atribuida_id: Mapped[UUID | None] = mapped_column(nullable=True)
