import os
from typing import Generator
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

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
    Garante que a conexão seja fechada de forma limpa ao final da requisição.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
