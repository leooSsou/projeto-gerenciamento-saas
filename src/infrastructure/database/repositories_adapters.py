from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session

from src.domain.entities.tenant import Tenant
from src.domain.entities.usuario import Usuario
from src.domain.repositories.tenant_repository import TenantRepository
from src.domain.repositories.usuario_repository import UsuarioRepository
from src.infrastructure.database.models import TenantModel, UsuarioModel

class SQLAlchemyTenantRepository(TenantRepository):
    """
    Adaptador concreto para persistência de Tenant usando SQLAlchemy.
    Implementa o contrato TenantRepository do domínio.
    """
    def __init__(self, db: Session) -> None:
        self.db = db

    def salvar(self, tenant: Tenant) -> Tenant:
        # Busca se o registro já existe no banco
        model = self.db.query(TenantModel).filter(TenantModel.id == tenant.id).first()
        
        if not model:
            # Novo registro
            model = TenantModel(
                id=tenant.id,
                nome_fantasia=tenant.nome_fantasia,
                razao_social=tenant.razao_social,
                cnpj=tenant.cnpj,
                data_cadastro=tenant.data_cadastro
            )
            self.db.add(model)
        else:
            # Atualização
            model.nome_fantasia = tenant.nome_fantasia
            model.razao_social = tenant.razao_social
            model.cnpj = tenant.cnpj
            model.data_cadastro = tenant.data_cadastro
            
        self.db.commit()
        self.db.refresh(model)
        
        return Tenant(
            id=model.id,
            nome_fantasia=model.nome_fantasia,
            razao_social=model.razao_social,
            cnpj=model.cnpj,
            data_cadastro=model.data_cadastro
        )

    def obter_por_cnpj(self, cnpj: str) -> Optional[Tenant]:
        # Remove formatação do CNPJ para buscar no banco
        cnpj_limpo = "".join(filter(str.isdigit, cnpj))
        model = self.db.query(TenantModel).filter(TenantModel.cnpj == cnpj_limpo).first()
        if not model:
            return None
        return Tenant(
            id=model.id,
            nome_fantasia=model.nome_fantasia,
            razao_social=model.razao_social,
            cnpj=model.cnpj,
            data_cadastro=model.data_cadastro
        )

    def obter_por_id(self, id: UUID) -> Optional[Tenant]:
        model = self.db.query(TenantModel).filter(TenantModel.id == id).first()
        if not model:
            return None
        return Tenant(
            id=model.id,
            nome_fantasia=model.nome_fantasia,
            razao_social=model.razao_social,
            cnpj=model.cnpj,
            data_cadastro=model.data_cadastro
        )


class SQLAlchemyUsuarioRepository(UsuarioRepository):
    """
    Adaptador concreto para persistência de Usuario usando SQLAlchemy.
    Implementa o contrato UsuarioRepository do domínio.
    """
    def __init__(self, db: Session) -> None:
        self.db = db

    def salvar(self, usuario: Usuario) -> Usuario:
        # Busca se o registro já existe no banco
        model = self.db.query(UsuarioModel).filter(UsuarioModel.id == usuario.id).first()
        
        if not model:
            # Novo registro
            model = UsuarioModel(
                id=usuario.id,
                nome=usuario.nome,
                email=usuario.email,
                senha_hash=usuario.senha_hash,
                role=usuario.role,
                tenant_id=usuario.tenant_id,
                loja_atribuida_id=usuario.loja_atribuida_id
            )
            self.db.add(model)
        else:
            # Atualização
            model.nome = usuario.nome
            model.email = usuario.email
            model.senha_hash = usuario.senha_hash
            model.role = usuario.role
            model.tenant_id = usuario.tenant_id
            model.loja_atribuida_id = usuario.loja_atribuida_id
            
        self.db.commit()
        self.db.refresh(model)
        
        return Usuario(
            id=model.id,
            nome=model.nome,
            email=model.email,
            senha_hash=model.senha_hash,
            role=model.role,
            tenant_id=model.tenant_id,
            loja_atribuida_id=model.loja_atribuida_id
        )

    def obter_por_email(self, email: str) -> Optional[Usuario]:
        model = self.db.query(UsuarioModel).filter(UsuarioModel.email.ilike(email)).first()
        if not model:
            return None
        return Usuario(
            id=model.id,
            nome=model.nome,
            email=model.email,
            senha_hash=model.senha_hash,
            role=model.role,
            tenant_id=model.tenant_id,
            loja_atribuida_id=model.loja_atribuida_id
        )

    def obter_por_id(self, id: UUID) -> Optional[Usuario]:
        model = self.db.query(UsuarioModel).filter(UsuarioModel.id == id).first()
        if not model:
            return None
        return Usuario(
            id=model.id,
            nome=model.nome,
            email=model.email,
            senha_hash=model.senha_hash,
            role=model.role,
            tenant_id=model.tenant_id,
            loja_atribuida_id=model.loja_atribuida_id
        )
