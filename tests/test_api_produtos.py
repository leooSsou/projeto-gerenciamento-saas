import pytest
from fastapi.testclient import TestClient
from uuid import uuid4

def setup_tenant_autenticado(client: TestClient):
    """
    Registra um tenant e retorna o token de acesso.
    """
    client.post("/auth/register", json={
        "nome_fantasia": "Tech Import",
        "razao_social": "Tech Import Ltda",
        "cnpj": "45.997.418/0001-53",
        "dono_nome": "Proprietario Tech",
        "dono_email": "tech@email.com",
        "dono_senha": "senha_segura_123"
    })
    
    login = client.post("/auth/login", json={"email": "tech@email.com", "senha": "senha_segura_123"})
    return login.json()["access_token"]


def test_crud_produto_fluxo_completo(client: TestClient):
    token = setup_tenant_autenticado(client)
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Criar Produto
    res_criar = client.post("/produtos/", json={
        "nome": "Mouse Gamer Pro",
        "sku": "MOUSE-GAMER-123",
        "preco_custo": 50.0,
        "preco_venda": 99.9,
        "markup": 1.0
    }, headers=headers)
    assert res_criar.status_code == 201
    produto = res_criar.json()
    assert produto["nome"] == "Mouse Gamer Pro"
    assert produto["sku"] == "MOUSE-GAMER-123"
    assert produto["preco_custo"] == 50.0
    assert produto["preco_venda"] == 99.9
    assert produto["markup"] == 1.0
    assert produto["ativo"] is True
    produto_id = produto["id"]

    # 2. Obter Produto
    res_obter = client.get(f"/produtos/{produto_id}", headers=headers)
    assert res_obter.status_code == 200
    assert res_obter.json()["nome"] == "Mouse Gamer Pro"

    # 3. Listar Produtos
    res_listar = client.get("/produtos/", headers=headers)
    assert res_listar.status_code == 200
    lista = res_listar.json()
    assert len(lista) >= 1
    assert any(p["id"] == produto_id for p in lista)

    # 4. Atualizar Produto
    res_atualizar = client.put(f"/produtos/{produto_id}", json={
        "nome": "Mouse Gamer Pro Max",
        "preco_custo": 55.0,
        "preco_venda": 110.0,
        "markup": 1.0,
        "ativo": False
    }, headers=headers)
    assert res_atualizar.status_code == 200
    produto_att = res_atualizar.json()
    assert produto_att["nome"] == "Mouse Gamer Pro Max"
    assert produto_att["preco_custo"] == 55.0
    assert produto_att["ativo"] is False


def test_criar_produto_sku_duplicado(client: TestClient):
    token = setup_tenant_autenticado(client)
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Cria produto pela primeira vez
    res_criar1 = client.post("/produtos/", json={
        "nome": "Teclado Mecanico",
        "sku": "KB-MEC-456",
        "preco_custo": 120.0,
        "preco_venda": 240.0,
        "markup": 1.0
    }, headers=headers)
    assert res_criar1.status_code == 201

    # 2. Tenta criar outro com o mesmo SKU
    res_criar2 = client.post("/produtos/", json={
        "nome": "Teclado RGB",
        "sku": "KB-MEC-456",
        "preco_custo": 130.0,
        "preco_venda": 260.0,
        "markup": 1.0
    }, headers=headers)
    assert res_criar2.status_code == 400
    assert "sku" in res_criar2.json()["detail"].lower()
