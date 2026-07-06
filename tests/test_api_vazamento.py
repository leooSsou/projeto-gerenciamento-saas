import pytest
from fastapi.testclient import TestClient
from datetime import timedelta
from src.infrastructure.security.jwt_handler import criar_token_acesso

def test_isolamento_leitura_api_multi_tenant(client: TestClient):
    """
    Cenário 1: Garante que os dados retornados de /auth/me pertencem estritamente
    ao Tenant do usuário autenticado no token, sem expor nada de outros Tenants.
    """
    # 1. Registra o Tenant A
    res_a = client.post("/auth/register", json={
        "nome_fantasia": "Tenant A",
        "razao_social": "Tenant A Ltda",
        "cnpj": "25.923.825/0001-09",
        "dono_nome": "Dono A",
        "dono_email": "donoa@email.com",
        "dono_senha": "senha_segura_a"
    })
    assert res_a.status_code == 201
    dono_a_id = res_a.json()["dono_id"]
    tenant_a_id = res_a.json()["tenant_id"]

    # 2. Registra o Tenant B
    res_b = client.post("/auth/register", json={
        "nome_fantasia": "Tenant B",
        "razao_social": "Tenant B Ltda",
        "cnpj": "05.292.609/0001-03",
        "dono_nome": "Dono B",
        "dono_email": "donob@email.com",
        "dono_senha": "senha_segura_b"
    })
    assert res_b.status_code == 201
    dono_b_id = res_b.json()["dono_id"]
    tenant_b_id = res_b.json()["tenant_id"]

    # 3. Faz login no Tenant A para obter token_a
    login_a = client.post("/auth/login", json={"email": "donoa@email.com", "senha": "senha_segura_a"})
    assert login_a.status_code == 200
    token_a = login_a.json()["access_token"]

    # 4. Faz login no Tenant B para obter token_b
    login_b = client.post("/auth/login", json={"email": "donob@email.com", "senha": "senha_segura_b"})
    assert login_b.status_code == 200
    token_b = login_b.json()["access_token"]

    # 5. Valida que o token_a dá acesso exclusivo aos dados de A
    res_me_a = client.get("/auth/me", headers={"Authorization": f"Bearer {token_a}"})
    assert res_me_a.status_code == 200
    data_a = res_me_a.json()
    assert data_a["id"] == dono_a_id
    assert data_a["tenant_id"] == tenant_a_id
    assert data_a["email"] == "donoa@email.com"

    # 6. Valida que o token_b dá acesso exclusivo aos dados de B
    res_me_b = client.get("/auth/me", headers={"Authorization": f"Bearer {token_b}"})
    assert res_me_b.status_code == 200
    data_b = res_me_b.json()
    assert data_b["id"] == dono_b_id
    assert data_b["tenant_id"] == tenant_b_id
    assert data_b["email"] == "donob@email.com"


def test_isolamento_de_sessao_concorrente(client: TestClient):
    """
    Cenário 2: Garante que as sessões de banco de dados geradas para requisições sequenciais
    mantenham seu isolamento de tenant_id, não deixando resquícios de estado no banco.
    """
    # 1. Cria dois inquilinos
    res_a = client.post("/auth/register", json={
        "nome_fantasia": "Empresa A",
        "razao_social": "Empresa A S/A",
        "cnpj": "67.827.595/0001-24",
        "dono_nome": "Admin A",
        "dono_email": "admina@email.com",
        "dono_senha": "senha_segura"
    })
    tenant_a_id = res_a.json()["tenant_id"]
    
    res_b = client.post("/auth/register", json={
        "nome_fantasia": "Empresa B",
        "razao_social": "Empresa B S/A",
        "cnpj": "19.808.022/0001-00",
        "dono_nome": "Admin B",
        "dono_email": "adminb@email.com",
        "dono_senha": "senha_segura"
    })
    tenant_b_id = res_b.json()["tenant_id"]

    # 2. Logins
    token_a = client.post("/auth/login", json={"email": "admina@email.com", "senha": "senha_segura"}).json()["access_token"]
    token_b = client.post("/auth/login", json={"email": "adminb@email.com", "senha": "senha_segura"}).json()["access_token"]

    # 3. Executa requisições intercaladas simulando acesso alternado
    for _ in range(5):
        # Acessa A
        res_me_a = client.get("/auth/me", headers={"Authorization": f"Bearer {token_a}"})
        assert res_me_a.json()["tenant_id"] == tenant_a_id
        
        # Acessa B
        res_me_b = client.get("/auth/me", headers={"Authorization": f"Bearer {token_b}"})
        assert res_me_b.json()["tenant_id"] == tenant_b_id


def test_tentativa_de_bypass_tenant_id(client: TestClient):
    """
    Cenário 3: Garante que qualquer tentativa de forçar um tenant_id diferente no corpo da requisição,
    cabeçalho customizado ou query params seja ignorada, utilizando apenas o tenant_id do JWT.
    """
    # 1. Cria inquilinos
    res_a = client.post("/auth/register", json={
        "nome_fantasia": "Loja Alfa",
        "razao_social": "Loja Alfa Ltda",
        "cnpj": "81.477.811/0001-80",
        "dono_nome": "Gerente Alfa",
        "dono_email": "alfa@email.com",
        "dono_senha": "senha_alfa"
    })
    tenant_a_id = res_a.json()["tenant_id"]
    
    res_b = client.post("/auth/register", json={
        "nome_fantasia": "Loja Beta",
        "razao_social": "Loja Beta Ltda",
        "cnpj": "94.686.599/0001-02",
        "dono_nome": "Gerente Beta",
        "dono_email": "beta@email.com",
        "dono_senha": "senha_beta"
    })
    tenant_b_id = res_b.json()["tenant_id"]

    token_a = client.post("/auth/login", json={"email": "alfa@email.com", "senha": "senha_alfa"}).json()["access_token"]

    # 2. Tenta fazer requisição para /auth/me usando token_a, mas injetando tenant_id_b via query ou headers maliciosos
    # Como o endpoint utiliza estritamente a dependência get_current_user (que lê do token),
    # o tenant retornado deve ser o de A, nunca o de B.
    headers = {
        "Authorization": f"Bearer {token_a}",
        "X-Tenant-ID": tenant_b_id, # Injeção de cabeçalho malicioso
        "tenant_id": tenant_b_id
    }
    
    response = client.get(f"/auth/me?tenant_id={tenant_b_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["tenant_id"] == tenant_a_id  # Deve ignorar B e retornar A


def test_token_expirado_rejeitado_na_api(client: TestClient):
    """
    Cenário 4: Garante que um token JWT expirado seja rejeitado com HTTP 401 Unauthorized pela API.
    """
    # Cria um token expirado manualmente (com tempo de expiração no passado)
    token_expirado = criar_token_acesso(
        sub="00000000-0000-0000-0000-000000000000",
        tenant_id="00000000-0000-0000-0000-000000000000",
        role="GERENTE",
        tempo_expiracao=timedelta(seconds=-10)
    )

    headers = {"Authorization": f"Bearer {token_expirado}"}
    response = client.get("/auth/me", headers=headers)
    
    assert response.status_code == 401
    assert "expirou" in response.json()["detail"].lower()
