import pytest
from fastapi.testclient import TestClient
from src.infrastructure.web.limiter import limiter

def test_rate_limiting_login_endpoint(client: TestClient):
    """
    Simula uma inundação de requisições (DDoS/Brute Force) no endpoint de login
    para verificar se o limitador de requisições bloqueia com HTTP 429.
    """
    # Ativa temporariamente o rate limiter para este teste específico
    limiter.enabled = True
    
    try:
        # Dispara 6 requisições de login rapidamente
        responses = []
        for _ in range(6):
            res = client.post("/auth/login", json={
                "email": "teste_rate_limit@email.com",
                "senha": "senha_incorreta"
            })
            responses.append(res)

        # As primeiras 5 devem retornar 401 (Credenciais Inválidas, pois o e-mail não existe)
        for i in range(5):
            assert responses[i].status_code == 401
            
        # A 6ª requisição deve estourar o limite de 5 por minuto e retornar 429 Too Many Requests
        assert responses[5].status_code == 429
        assert "Rate limit exceeded" in responses[5].text
        
    finally:
        # Garante que desativa o limiter para os outros testes da suíte
        limiter.enabled = False
