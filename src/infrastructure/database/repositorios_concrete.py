from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from src.infrastructure.database.models import TenantModel, UsuarioModel

class RepositorioTenantSQLAlchemy:
    """
    Implementação concreta do repositório de Tenant usando SQLAlchemy.
    """
    def __init__(self, db: Session) -> None:
        self.db = db

    def salvar(self, tenant: TenantModel) -> TenantModel:
        self.db.add(tenant)
        self.db.commit()
        self.db.refresh(tenant)
        return tenant

    def buscar_por_cnpj(self, cnpj: str) -> Optional[TenantModel]:
        return self.db.query(TenantModel).filter(TenantModel.cnpj == cnpj).first()

    def buscar_por_id(self, id: UUID) -> Optional[TenantModel]:
        return self.db.query(TenantModel).filter(TenantModel.id == id).first()

class RepositorioUsuarioSQLAlchemy:
    """
    Implementação concreta do repositório de Usuario usando SQLAlchemy.
    """
    def __init__(self, db: Session) -> None:
        self.db = db

    def salvar(self, usuario: UsuarioModel) -> UsuarioModel:
        self.db.add(usuario)
        self.db.commit()
        self.db.refresh(usuario)
        return usuario

    def buscar_por_email(self, email: str) -> Optional[UsuarioModel]:
        return self.db.query(UsuarioModel).filter(UsuarioModel.email == email).first()

    def buscar_por_id(self, id: UUID) -> Optional[UsuarioModel]:
        return self.db.query(UsuarioModel).filter(UsuarioModel.id == id).first()
