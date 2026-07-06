from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from src.domain.repositories.tenant_repository import TenantRepository
from src.domain.repositories.usuario_repository import UsuarioRepository
from src.domain.repositories.loja_repository import LojaRepository
from src.domain.entities.tenant import Tenant
from src.domain.entities.usuario import Usuario
from src.domain.entities.loja import Loja
from src.infrastructure.database.models import TenantModel, UsuarioModel, LojaModel

class RepositorioTenantSQLAlchemy(TenantRepository):
    """
    Implementação concreta do repositório de Tenant usando SQLAlchemy.
    """
    def __init__(self, db: Session) -> None:
        self.db = db

    def salvar(self, tenant: Tenant) -> Tenant:
        model = self.db.query(TenantModel).filter(TenantModel.id == tenant.id).first()
        if not model:
            model = TenantModel(
                id=tenant.id,
                nome_fantasia=tenant.nome_fantasia,
                razao_social=tenant.razao_social,
                cnpj=tenant.cnpj,
                data_cadastro=tenant.data_cadastro
            )
            self.db.add(model)
        else:
            model.nome_fantasia = tenant.nome_fantasia
            model.razao_social = tenant.razao_social
            model.cnpj = tenant.cnpj
            model.data_cadastro = tenant.data_cadastro
            
        # O commit agora é delegado para a transação geral da rota/caso de uso.
        # Apenas damos flush para carregar possíveis IDs e gerados pelo banco.
        self.db.flush()
        
        return Tenant(
            id=model.id,
            nome_fantasia=model.nome_fantasia,
            razao_social=model.razao_social,
            cnpj=model.cnpj,
            data_cadastro=model.data_cadastro
        )

    def obter_por_cnpj(self, cnpj: str) -> Optional[Tenant]:
        model = self.db.query(TenantModel).filter(TenantModel.cnpj == cnpj).first()
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


class RepositorioUsuarioSQLAlchemy(UsuarioRepository):
    """
    Implementação concreta do repositório de Usuario usando SQLAlchemy.
    """
    def __init__(self, db: Session) -> None:
        self.db = db

    def salvar(self, usuario: Usuario) -> Usuario:
        model = self.db.query(UsuarioModel).filter(UsuarioModel.id == usuario.id).first()
        if not model:
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
            model.nome = usuario.nome
            model.email = usuario.email
            model.senha_hash = usuario.senha_hash
            model.role = usuario.role
            model.loja_atribuida_id = usuario.loja_atribuida_id
            model.tenant_id = usuario.tenant_id
            
        self.db.flush()
        
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
        model = self.db.query(UsuarioModel).filter(UsuarioModel.email == email).first()
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


class RepositorioLojaSQLAlchemy(LojaRepository):
    """
    Implementação concreta do repositório de Loja usando SQLAlchemy.
    """
    def __init__(self, db: Session) -> None:
        self.db = db

    def salvar(self, loja: Loja) -> Loja:
        self.db.info["tenant_id"] = loja.tenant_id
        model = self.db.query(LojaModel).filter(LojaModel.id == loja.id).first()
        
        if not model:
            model = LojaModel(
                id=loja.id,
                nome=loja.nome,
                cnpj=loja.cnpj,
                endereco=loja.endereco,
                tenant_id=loja.tenant_id,
                ativo=loja.ativo
            )
            self.db.add(model)
        else:
            model.nome = loja.nome
            model.cnpj = loja.cnpj
            model.endereco = loja.endereco
            model.ativo = loja.ativo
            
        self.db.flush()
        
        return Loja(
            id=model.id,
            nome=model.nome,
            cnpj=model.cnpj,
            endereco=model.endereco,
            tenant_id=model.tenant_id,
            ativo=model.ativo
        )

    def obter_por_id(self, id: UUID, tenant_id: UUID) -> Optional[Loja]:
        self.db.info["tenant_id"] = tenant_id
        model = self.db.query(LojaModel).filter(LojaModel.id == id).first()
        if not model:
            return None
        return Loja(
            id=model.id,
            nome=model.nome,
            cnpj=model.cnpj,
            endereco=model.endereco,
            tenant_id=model.tenant_id,
            ativo=model.ativo
        )

    def obter_por_cnpj(self, cnpj: str, tenant_id: UUID) -> Optional[Loja]:
        self.db.info["tenant_id"] = tenant_id
        cnpj_limpo = "".join(filter(str.isdigit, cnpj))
        model = self.db.query(LojaModel).filter(LojaModel.cnpj == cnpj_limpo).first()
        if not model:
            return None
        return Loja(
            id=model.id,
            nome=model.nome,
            cnpj=model.cnpj,
            endereco=model.endereco,
            tenant_id=model.tenant_id,
            ativo=model.ativo
        )

    def listar_todas(self, tenant_id: UUID) -> List[Loja]:
        self.db.info["tenant_id"] = tenant_id
        models = self.db.query(LojaModel).all()
        return [
            Loja(
                id=m.id,
                nome=m.nome,
                cnpj=m.cnpj,
                endereco=m.endereco,
                tenant_id=m.tenant_id,
                ativo=m.ativo
            )
            for m in models
        ]

