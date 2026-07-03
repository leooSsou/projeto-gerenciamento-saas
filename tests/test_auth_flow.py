from fastapi.testclient import TestClient

def test_fluxo_autenticacao_completo(client: TestClient):
    """
    Testa o ciclo completo de registro, login e obtenção de dados do usuário logado.
    """
    # 1. Cadastro de um novo Tenant + Usuário Dono
    payload_registro = {
        "nome_fantasia": "Lojas Express",
        "razao_social": "Lojas Express S/A",
        "cnpj": "99.999.999/0001-99",
        "dono_nome": "Julio Cesar",
        "dono_email": "julio@express.com",
        "dono_senha": "senha_segura_123"
    }
    
    response = client.post("/auth/register", json=payload_registro)
    assert response.status_code == 201
    data = response.json()
    assert data["nome_fantasia"] == "Lojas Express"
    assert data["dono_email"] == "julio@express.com"
    assert "tenant_id" in data
    assert "dono_id" in data
    
    tenant_id = data["tenant_id"]
    dono_id = data["dono_id"]
    
    # 2. Cadastro duplicado de CNPJ deve falhar (HTTP 400)
    response_cnpj_duplicado = client.post("/auth/register", json={
        "nome_fantasia": "Outra Loja",
        "razao_social": "Outra Razao S/A",
        "cnpj": "99.999.999/0001-99", # CNPJ idêntico
        "dono_nome": "Carlos",
        "dono_email": "carlos@express.com",
        "dono_senha": "senha_segura_123"
    })
    assert response_cnpj_duplicado.status_code == 400
    assert "CNPJ" in response_cnpj_duplicado.json()["detail"]
    
    # 3. Cadastro duplicado de Email deve falhar (HTTP 400)
    response_email_duplicado = client.post("/auth/register", json={
        "nome_fantasia": "Outra Loja",
        "razao_social": "Outra Razao S/A",
        "cnpj": "11.222.333/0001-44",
        "dono_nome": "Julio Repetido",
        "dono_email": "julio@express.com", # E-mail idêntico
        "dono_senha": "senha_segura_123"
    })
    assert response_email_duplicado.status_code == 400
    assert "e-mail" in response_email_duplicado.json()["detail"].lower()
    
    # 4. Login com sucesso (HTTP 200)
    payload_login = {
        "email": "julio@express.com",
        "senha": "senha_segura_123"
    }
    response_login = client.post("/auth/login", json=payload_login)
    assert response_login.status_code == 200
    token_data = response_login.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
    
    token = token_data["access_token"]
    
    # 5. Login com senha incorreta deve falhar (HTTP 401)
    response_login_falho = client.post("/auth/login", json={
        "email": "julio@express.com",
        "senha": "senha_errada"
    })
    assert response_login_falho.status_code == 401
    
    # 6. Acesso à rota protegida /auth/me com token válido (HTTP 200)
    headers = {"Authorization": f"Bearer {token}"}
    response_me = client.get("/auth/me", headers=headers)
    assert response_me.status_code == 200
    user_data = response_me.json()
    assert user_data["id"] == dono_id
    assert user_data["email"] == "julio@express.com"
    assert user_data["role"] == "DONO"
    assert user_data["tenant_id"] == tenant_id
    
    # 7. Acesso à rota protegida com token inválido deve falhar (HTTP 401)
    headers_invalidos = {"Authorization": "Bearer token_completamente_errado"}
    response_me_falha = client.get("/auth/me", headers=headers_invalidos)
    assert response_me_falha.status_code == 401
    assert "token inválido" in response_me_falha.json()["detail"].lower()
