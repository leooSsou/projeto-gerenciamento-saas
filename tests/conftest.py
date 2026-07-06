import os
from typing import Generator
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv

from src.infrastructure.web.main import app
from src.infrastructure.database.session import get_db
from src.infrastructure.database.models import Base

# Carrega variáveis de ambiente
load_dotenv()

# Utiliza DATABASE_TEST_URL para testes
DATABASE_TEST_URL = os.getenv("DATABASE_TEST_URL", "sqlite:///./gerenciador_saas_test.db")

# Configuração do Engine do banco de dados de testes
connect_args = {"check_same_thread": False} if DATABASE_TEST_URL.startswith("sqlite") else {}
test_engine = create_engine(DATABASE_TEST_URL, connect_args=connect_args)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_database() -> Generator[None, None, None]:
    """
    Cria a estrutura de tabelas do banco de dados de teste antes de iniciar os testes
    e limpa tudo após o término da sessão.
    """
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)
    
    # Remove o arquivo físico se for SQLite local
    if DATABASE_TEST_URL.startswith("sqlite:///./"):
        sqlite_file = DATABASE_TEST_URL.replace("sqlite:///./", "")
        if os.path.exists(sqlite_file):
            try:
                os.remove(sqlite_file)
            except OSError:
                pass

@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    """
    Fornece uma sessão de banco de dados isolada para cada teste.
    Realiza rollback ao final para não sujar o banco de testes.
    """
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """
    Fornece um cliente HTTP de testes para o FastAPI com a injeção do banco sobreposta.
    """
    def _get_test_db():
        try:
            yield db_session
        finally:
            pass
            
    app.dependency_overrides[get_db] = _get_test_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
