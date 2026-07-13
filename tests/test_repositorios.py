import pytest
from sqlalchemy.orm import Session
from src.domain.entities.tenant import Tenant
from src.domain.entities.usuario import Usuario
from src.domain.entities.loja import Loja
from src.infrastructure.database.models import UsuarioModel
from src.infrastructure.database.repositorios_concrete import (
    RepositorioTenantSQLAlchemy,
    RepositorioUsuarioSQLAlchemy,
    RepositorioLojaSQLAlchemy,
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
    
    # Criando o Tenant (Entidade pura do Domínio)
    tenant = Tenant(
        nome_fantasia="Lojas do Leo",
        razao_social="Leonardo de Souza Lojas Ltda",
        cnpj="12.345.678/0001-95"  # CNPJ Válido matematicamente
    )
    tenant_salvo = repo_tenant.salvar(tenant)
    assert tenant_salvo.id is not None
    assert tenant_salvo.cnpj == "12345678000195"
    
    # Criando o Usuário associado ao Tenant (Entidade pura do Domínio)
    usuario = Usuario(
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
    
    tenant_a = repo_tenant.salvar(Tenant(nome_fantasia="Tenant A", razao_social="Tenant A Ltda", cnpj="12.345.678/0001-95"))
    tenant_b = repo_tenant.salvar(Tenant(nome_fantasia="Tenant B", razao_social="Tenant B Ltda", cnpj="45.997.418/0001-53"))
    
    user_a = repo_usuario.salvar(Usuario(nome="User A", email="usera@email.com", senha_hash="hash", role="DONO", tenant_id=tenant_a.id))
    user_b = repo_usuario.salvar(Usuario(nome="User B", email="userb@email.com", senha_hash="hash", role="DONO", tenant_id=tenant_b.id))
    
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


def test_persistir_e_filtrar_loja(db_session: Session) -> None:
    """
    Testa se conseguimos salvar, obter e listar lojas usando o repositório concreto com isolamento de tenant.
    """
    db_session.info["ignore_tenant_filter"] = True
    repo_tenant = RepositorioTenantSQLAlchemy(db_session)
    
    tenant_a = repo_tenant.salvar(Tenant(nome_fantasia="Empresa A", razao_social="Empresa A S/A", cnpj="26.762.981/0001-06"))
    tenant_b = repo_tenant.salvar(Tenant(nome_fantasia="Empresa B", razao_social="Empresa B S/A", cnpj="96.453.427/0001-14"))
    
    db_session.commit()
    db_session.info["ignore_tenant_filter"] = False
    
    repo_loja = RepositorioLojaSQLAlchemy(db_session)
    
    # 1. Cria duas lojas para Tenant A
    loja_a1 = Loja(nome="Loja A1", cnpj="02.188.445/0001-72", endereco="Av. A, 1", tenant_id=tenant_a.id)
    loja_a2 = Loja(nome="Loja A2", cnpj="44.997.002/0001-72", endereco="Av. A, 2", tenant_id=tenant_a.id)
    repo_loja.salvar(loja_a1)
    repo_loja.salvar(loja_a2)
    
    # 2. Cria uma loja para Tenant B
    loja_b1 = Loja(nome="Loja B1", cnpj="76.764.269/0001-06", endereco="Av. B, 1", tenant_id=tenant_b.id)
    repo_loja.salvar(loja_b1)
    
    db_session.commit()
    
    # 3. Listagem sob contexto do Tenant A
    db_session.info["tenant_id"] = tenant_a.id
    lojas_a = repo_loja.listar_todas(tenant_a.id)
    assert len(lojas_a) == 2
    assert any(loja.nome == "Loja A1" for loja in lojas_a)
    assert any(loja.nome == "Loja A2" for loja in lojas_a)
    
    # 4. Listagem sob contexto do Tenant B
    db_session.info["tenant_id"] = tenant_b.id
    lojas_b = repo_loja.listar_todas(tenant_b.id)
    assert len(lojas_b) == 1
    assert lojas_b[0].nome == "Loja B1"
    
    # 5. Obter loja individualmente respeitando tenant
    loja_a1_obtida = repo_loja.obter_por_id(loja_a1.id, tenant_a.id)
    assert loja_a1_obtida is not None
    assert loja_a1_obtida.nome == "Loja A1"
    
    # Tentar obter loja do Tenant A com contexto do Tenant B deve retornar None devido ao filtro de tenant
    loja_a1_com_b = repo_loja.obter_por_id(loja_a1.id, tenant_b.id)
    assert loja_a1_com_b is None

