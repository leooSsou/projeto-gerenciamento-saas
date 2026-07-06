import os
from typing import Generator
from dotenv import load_dotenv
from sqlalchemy import create_engine, event, TextClause
from sqlalchemy.orm import sessionmaker, Session, ORMExecuteState, with_loader_criteria

from src.infrastructure.database.mixins import HasTenant

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("A variável de ambiente DATABASE_URL não foi configurada.")

# Configuração do engine do SQLAlchemy (PostgreSQL/SQLite)
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verifica a conexão antes de usar do pool
    connect_args=connect_args,
)

# Fabrica de sessões do banco de dados
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

def get_db() -> Generator[Session, None, None]:
    """
    Dependency do FastAPI para obter a sessão do banco de dados.
    Garante que a transação seja comitada se a requisição ocorrer sem erros,
    ou desfeita (rollback) em caso de exceções, fechando a conexão limpa ao final.
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


@event.listens_for(Session, "do_orm_execute")
def aplicar_filtro_tenant_global(execute_state: ORMExecuteState) -> None:
    """
    Interceptor do SQLAlchemy para aplicar e validar o isolamento por tenant.
    Garante que qualquer query executada que envolva um modelo com o mixin HasTenant
    receba automaticamente o filtro de tenant_id, tanto em SELECTs quanto em DMLs
    (UPDATE e DELETE).
    
    Além disso, bloqueia execuções de SQL bruto (text()) caso um tenant esteja ativo,
    forçando o desenvolvedor a usar o ORM ou a declarar explicitamente o bypass
    via 'ignore_tenant_filter'.
    """
    session = execute_state.session
    
    # 1. Verifica se a query deve ignorar o filtro
    if session.info.get("ignore_tenant_filter"):
        return
        
    # 2. Bloqueio de SQL Bruto (TextClause) caso exista um tenant_id ativo na sessão
    tenant_id = session.info.get("tenant_id")
    if tenant_id and isinstance(execute_state.statement, TextClause):
        raise ValueError("Execucao de SQL bruto bloqueada em sessoes com tenant ativo. Use a API ORM ou utilize 'ignore_tenant_filter'.")

    # 3. Identifica as classes de domínio envolvidas na query
    contem_has_tenant = False
    classes_tenant_aware = []
    for mapper in execute_state.all_mappers:
        if issubclass(mapper.class_, HasTenant):
            contem_has_tenant = True
            classes_tenant_aware.append(mapper.class_)
            
    if contem_has_tenant:
        if not tenant_id:
            raise ValueError("Acesso ao banco de dados bloqueado: tenant_id não configurado na sessão.")
            
        # Tratamento para consultas de Leitura (SELECT)
        if execute_state.is_select:
            execute_state.statement = execute_state.statement.options(
                with_loader_criteria(
                    HasTenant,
                    lambda cls: cls.tenant_id == tenant_id,
                    include_aliases=True
                )
            )
            
        # Tratamento para Alterações e Exclusões em massa (UPDATE / DELETE)
        elif execute_state.is_update or execute_state.is_delete:
            for cls in classes_tenant_aware:
                # Injeta a cláusula WHERE tenant_id = current_tenant_id diretamente na DML
                execute_state.statement = execute_state.statement.where(cls.tenant_id == tenant_id)
