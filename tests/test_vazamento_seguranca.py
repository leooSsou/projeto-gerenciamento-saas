import pytest
from uuid import uuid4
from sqlalchemy import select, update, delete, text
from sqlalchemy.orm import Session
from src.infrastructure.database.models import TenantModel, UsuarioModel

def setup_dados_teste(db_session: Session):
    """
    Função auxiliar para criar Tenants e Usuários de teste usando bypass do filtro.
    """
    db_session.info["ignore_tenant_filter"] = True
    
    tenant_a = TenantModel(nome_fantasia="Tenant A", razao_social="Tenant A Ltda", cnpj="11111111000111")
    tenant_b = TenantModel(nome_fantasia="Tenant B", razao_social="Tenant B Ltda", cnpj="22222222000222")
    db_session.add_all([tenant_a, tenant_b])
    db_session.commit()
    
    user_a = UsuarioModel(nome="User A", email="usera@email.com", senha_hash="hash", role="GERENTE", tenant_id=tenant_a.id)
    user_b = UsuarioModel(nome="User B", email="userb@email.com", senha_hash="hash", role="GERENTE", tenant_id=tenant_b.id)
    db_session.add_all([user_a, user_b])
    db_session.commit()
    
    db_session.info["ignore_tenant_filter"] = False
    return tenant_a, tenant_b, user_a, user_b


def test_vulnerabilidade_bulk_update_core(db_session: Session) -> None:
    """
    Caso 1: UPDATE via Core (update(Model))
    Configura a sessão para o Tenant A e executa um UPDATE geral.
    O nome do User B (Tenant B) NÃO deve ser alterado.
    """
    tenant_a, tenant_b, user_a, user_b = setup_dados_teste(db_session)
    
    # Define contexto para o Tenant A
    db_session.info["tenant_id"] = tenant_a.id
    
    # Executa update em massa sem filtro explícito
    stmt = update(UsuarioModel).values(nome="Nome Alterado")
    db_session.execute(stmt)
    db_session.commit()
    
    # Limpa contexto para checar o banco
    db_session.info.pop("tenant_id", None)
    db_session.info["ignore_tenant_filter"] = True
    
    user_b_atualizado = db_session.get(UsuarioModel, user_b.id)
    assert user_b_atualizado is not None
    # ESPERADO: O nome do User B continua "User B" (não foi afetado pelo update do Tenant A)
    # FALHA ATUAL: O nome do User B será alterado para "Nome Alterado"
    assert user_b_atualizado.nome == "User B"


def test_vulnerabilidade_bulk_delete_core(db_session: Session) -> None:
    """
    Caso 2: DELETE via Core (delete(Model))
    Configura a sessão para o Tenant A e executa um DELETE.
    O User B (Tenant B) NÃO deve ser deletado.
    """
    tenant_a, tenant_b, user_a, user_b = setup_dados_teste(db_session)
    
    # Define contexto para o Tenant A
    db_session.info["tenant_id"] = tenant_a.id
    
    # Executa delete em massa sem filtro explícito
    stmt = delete(UsuarioModel)
    db_session.execute(stmt)
    db_session.commit()
    
    # Limpa contexto para checar o banco
    db_session.info.pop("tenant_id", None)
    db_session.info["ignore_tenant_filter"] = True
    
    user_b_existente = db_session.get(UsuarioModel, user_b.id)
    # ESPERADO: User B continua existindo no banco de dados
    # FALHA ATUAL: User B será deletado do banco de dados
    assert user_b_existente is not None


def test_vulnerabilidade_query_update_orm(db_session: Session) -> None:
    """
    Caso 3: UPDATE via Query ORM (query.update())
    Configura a sessão para o Tenant A e executa query(Model).update().
    O nome do User B (Tenant B) NÃO deve ser alterado.
    """
    tenant_a, tenant_b, user_a, user_b = setup_dados_teste(db_session)
    
    # Define contexto para o Tenant A
    db_session.info["tenant_id"] = tenant_a.id
    
    # Executa update via query ORM
    db_session.query(UsuarioModel).update({"nome": "Invasao"})
    db_session.commit()
    
    # Limpa contexto para checar o banco
    db_session.info.pop("tenant_id", None)
    db_session.info["ignore_tenant_filter"] = True
    
    user_b_atualizado = db_session.get(UsuarioModel, user_b.id)
    assert user_b_atualizado is not None
    # ESPERADO: O nome do User B continua "User B"
    # FALHA ATUAL: O nome do User B será alterado para "Invasao"
    assert user_b_atualizado.nome == "User B"


def test_vulnerabilidade_query_delete_orm(db_session: Session) -> None:
    """
    Caso 4: DELETE via Query ORM (query.delete())
    Configura a sessão para o Tenant A e executa query(Model).delete().
    O User B (Tenant B) NÃO deve ser deletado.
    """
    tenant_a, tenant_b, user_a, user_b = setup_dados_teste(db_session)
    
    # Define contexto para o Tenant A
    db_session.info["tenant_id"] = tenant_a.id
    
    # Executa delete via query ORM
    db_session.query(UsuarioModel).delete()
    db_session.commit()
    
    # Limpa contexto para checar o banco
    db_session.info.pop("tenant_id", None)
    db_session.info["ignore_tenant_filter"] = True
    
    user_b_existente = db_session.get(UsuarioModel, user_b.id)
    # ESPERADO: User B continua existindo no banco de dados
    # FALHA ATUAL: User B será deletado
    assert user_b_existente is not None


def test_vulnerabilidade_raw_sql(db_session: Session) -> None:
    """
    Caso 5: UPDATE via Raw SQL String (db.execute(text(...)))
    Configura a sessão para o Tenant A e executa uma SQL crua direta.
    Queremos garantir que a execução de texto puro sem flag de ignore seja BLOQUEADA para segurança.
    """
    tenant_a, tenant_b, user_a, user_b = setup_dados_teste(db_session)
    
    # Define contexto para o Tenant A
    db_session.info["tenant_id"] = tenant_a.id
    
    # Tentativa de rodar um SQL cru de update
    # ESPERADO: Deve disparar ValueError ou bloquear a execução
    # FALHA ATUAL: Passa direto e altera os dados do User B
    with pytest.raises(ValueError, match="Execucao de SQL bruto bloqueada em sessoes com tenant ativo"):
        db_session.execute(text("UPDATE usuarios SET nome = 'Hack'"))
        db_session.commit()
