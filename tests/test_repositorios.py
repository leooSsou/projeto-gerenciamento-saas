import pytest
from sqlalchemy.orm import Session

# Importações dos modelos e repositórios (que falharão inicialmente no TDD)
from src.infrastructure.database.models import TenantModel, UsuarioModel
from src.infrastructure.database.repositorios_concrete import (
    RepositorioTenantSQLAlchemy,
    RepositorioUsuarioSQLAlchemy,
)

def test_persistir_tenant_e_usuario(db_session: Session) -> None:
    """
    Testa se conseguimos salvar um tenant e um usuário usando os repositórios.
    """
    # Como as tabelas usam tenant_id, e a sessão exige o tenant_id configurado,
    # precisamos habilitar o ignore_tenant_filter para criar o tenant inicial e o usuário
    db_session.info["ignore_tenant_filter"] = True
    
    repo_tenant = RepositorioTenantSQLAlchemy(db_session)
    repo_usuario = RepositorioUsuarioSQLAlchemy(db_session)
    
    # Criando o Tenant
    tenant = TenantModel(
        nome_fantasia="Lojas do Leo",
        razao_social="Leonardo de Souza Lojas Ltda",
        cnpj="12345678000195"
    )
    tenant_salvo = repo_tenant.salvar(tenant)
    assert tenant_salvo.id is not None
    assert tenant_salvo.cnpj == "12345678000195"
    
    # Criando o Usuário associado ao Tenant
    usuario = UsuarioModel(
        nome="Leonardo Souza",
        email="leo@email.com",
        senha_hash="hashed_password",
        role="DONO",
        tenant_id=tenant_salvo.id
    )
    usuario_salvo = repo_usuario.salvar(usuario)
    assert usuario_salvo.id is not None
    assert usuario_salvo.tenant_id == tenant_salvo.id
    assert usuario_salvo.email == "leo@email.com"


def test_filtro_global_tenant_id(db_session: Session) -> None:
    """
    Garante que as consultas a tabelas tenant-aware filtrem automaticamente os registros pelo tenant_id ativo na sessão.
    """
    # 1. Criar dados de dois inquilinos diferentes usando bypass do filtro
    db_session.info["ignore_tenant_filter"] = True
    
    repo_tenant = RepositorioTenantSQLAlchemy(db_session)
    repo_usuario = RepositorioUsuarioSQLAlchemy(db_session)
    
    tenant_a = repo_tenant.salvar(TenantModel(nome_fantasia="Tenant A", razao_social="Tenant A Ltda", cnpj="11111111000111"))
    tenant_b = repo_tenant.salvar(TenantModel(nome_fantasia="Tenant B", razao_social="Tenant B Ltda", cnpj="22222222000222"))
    
    user_a = repo_usuario.salvar(UsuarioModel(nome="User A", email="usera@email.com", senha_hash="hash", role="GERENTE", tenant_id=tenant_a.id))
    user_b = repo_usuario.salvar(UsuarioModel(nome="User B", email="userb@email.com", senha_hash="hash", role="GERENTE", tenant_id=tenant_b.id))
    
    db_session.commit()
    
    # Desativa o bypass
    db_session.info["ignore_tenant_filter"] = False
    
    # 2. Configura a sessão para o Tenant A e realiza a query
    db_session.info["tenant_id"] = tenant_a.id
    
    usuarios_filtrados = db_session.query(UsuarioModel).all()
    assert len(usuarios_filtrados) == 1
    assert usuarios_filtrados[0].id == user_a.id
    
    # 3. Configura a sessão para o Tenant B e realiza a query
    db_session.info["tenant_id"] = tenant_b.id
    
    usuarios_filtrados = db_session.query(UsuarioModel).all()
    assert len(usuarios_filtrados) == 1
    assert usuarios_filtrados[0].id == user_b.id


def test_bloqueio_de_vazamento_sem_tenant_id(db_session: Session) -> None:
    """
    Garante que, se uma consulta a um modelo tenant-aware for feita sem o tenant_id
    configurado na sessão e sem ignore_tenant_filter, um erro seja disparado.
    """
    # Limpa qualquer configuração da sessão
    db_session.info.pop("tenant_id", None)
    db_session.info.pop("ignore_tenant_filter", None)
    
    # Tenta fazer uma consulta a UsuarioModel (que herda de HasTenant)
    with pytest.raises(ValueError, match="Acesso ao banco de dados bloqueado: tenant_id não configurado na sessão."):
        db_session.query(UsuarioModel).all()
