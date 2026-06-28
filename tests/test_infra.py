from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session

def test_health_check_endpoint(client: TestClient):
    """
    Testa se o endpoint de health check responde corretamente com HTTP 200 e a mensagem esperada.
    """
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "operacional" in data["message"]

def test_database_connectivity(db_session: Session):
    """
    Testa se a conexão com o banco de dados de teste está ativa e funcional.
    """
    # Executa uma query simples de teste no SQLite/Postgres utilizando text()
    result = db_session.execute(text("SELECT 1")).scalar()
    assert result == 1
