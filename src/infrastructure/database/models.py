from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy import String, DateTime, text, Float, Boolean, UniqueConstraint, ForeignKey
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


class LojaModel(HasTenant, Base):
    """
    Representação física da tabela lojas (filiais do tenant).
    """
    __tablename__ = "lojas"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    cnpj: Mapped[str] = mapped_column(String(14), unique=True, nullable=False)
    endereco: Mapped[str] = mapped_column(String(255), nullable=False)
    ativo: Mapped[bool] = mapped_column(default=True, nullable=False)


class ProdutoModel(HasTenant, Base):
    """
    Representação física da tabela produtos (catálogo de produtos).
    """
    __tablename__ = "produtos"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    sku: Mapped[str] = mapped_column(String(50), nullable=False)
    preco_custo: Mapped[float] = mapped_column(Float, nullable=False)
    preco_venda: Mapped[float] = mapped_column(Float, nullable=False)
    markup: Mapped[float] = mapped_column(Float, nullable=False)
    codigo_barras: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    fornecedor_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("fornecedores.id"), nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    __table_args__ = (
        UniqueConstraint("sku", "tenant_id", name="uq_produtos_sku_tenant"),
    )



class ClienteModel(HasTenant, Base):
    """
    Representação física da tabela clientes.
    """
    __tablename__ = "clientes"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    documento: Mapped[str] = mapped_column(String(14), nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    __table_args__ = (
        UniqueConstraint("documento", "tenant_id", name="uq_clientes_documento_tenant"),
    )


class FornecedorModel(HasTenant, Base):
    """
    Representação física da tabela fornecedores.
    """
    __tablename__ = "fornecedores"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    nome_fantasia: Mapped[str] = mapped_column(String(100), nullable=False)
    razao_social: Mapped[str] = mapped_column(String(100), nullable=False)
    cnpj: Mapped[str] = mapped_column(String(14), nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    __table_args__ = (
        UniqueConstraint("cnpj", "tenant_id", name="uq_fornecedores_cnpj_tenant"),
    )

