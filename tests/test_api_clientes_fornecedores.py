import pytest
from fastapi.testclient import TestClient
from uuid import uuid4

def setup_tenant_autenticado(client: TestClient):
    """
    Registra um tenant e retorna o token de acesso.
    """
    # Usando CNPJ diferente para não conflitar com outros testes na mesma sessão
    client.post("/auth/register", json={
        "nome_fantasia": "Distribuidora Vendas",
        "razao_social": "Distribuidora Vendas Ltda",
        "cnpj": "26.762.981/0001-06",
        "dono_nome": "Dono Distribuidora",
        "dono_email": "distribuidora@email.com",
        "dono_senha": "senha_segura_123"
    })
    
    login = client.post("/auth/login", json={"email": "distribuidora@email.com", "senha": "senha_segura_123"})
    return login.json()["access_token"]


def test_crud_cliente_fluxo_completo(client: TestClient):
    token = setup_tenant_autenticado(client)
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Criar Cliente (Usando CPF válido)
    res_criar = client.post("/clientes/", json={
        "nome": "João da Silva",
        "email": "joaosilva@email.com",
        "documento": "12345678909"
    }, headers=headers)
    assert res_criar.status_code == 201
    cliente = res_criar.json()
    assert cliente["nome"] == "João da Silva"
    assert cliente["email"] == "joaosilva@email.com"
    assert cliente["documento"] == "12345678909"
    assert cliente["ativo"] is True
    cliente_id = cliente["id"]

    # 2. Obter Cliente
    res_obter = client.get(f"/clientes/{cliente_id}", headers=headers)
    assert res_obter.status_code == 200
    assert res_obter.json()["nome"] == "João da Silva"

    # 3. Listar Clientes
    res_listar = client.get("/clientes/", headers=headers)
    assert res_listar.status_code == 200
    lista = res_listar.json()
    assert len(lista) >= 1
    assert any(c["id"] == cliente_id for c in lista)

    # 4. Atualizar Cliente
    res_atualizar = client.put(f"/clientes/{cliente_id}", json={
        "nome": "João da Silva Neto",
        "email": "joaosilvaneto@email.com",
        "ativo": False
    }, headers=headers)
    assert res_atualizar.status_code == 200
    cliente_att = res_atualizar.json()
    assert cliente_att["nome"] == "João da Silva Neto"
    assert cliente_att["email"] == "joaosilvaneto@email.com"
    assert cliente_att["ativo"] is False


def test_criar_cliente_documento_duplicado(client: TestClient):
    token = setup_tenant_autenticado(client)
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Cria cliente pela primeira vez (CPF válido)
    res_criar1 = client.post("/clientes/", json={
        "nome": "Maria de Souza",
        "email": "maria@email.com",
        "documento": "98765432100"
    }, headers=headers)
    assert res_criar1.status_code == 201

    # 2. Tenta criar outro com o mesmo documento
    res_criar2 = client.post("/clientes/", json={
        "nome": "Maria Souza Lima",
        "email": "mariasouza@email.com",
        "documento": "98765432100"
    }, headers=headers)
    assert res_criar2.status_code == 400
    assert "documento" in res_criar2.json()["detail"].lower()


def test_crud_fornecedor_fluxo_completo(client: TestClient):
    token = setup_tenant_autenticado(client)
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Criar Fornecedor (CNPJ válido)
    res_criar = client.post("/fornecedores/", json={
        "nome_fantasia": "Atacado Sul",
        "razao_social": "Atacado Sul Distribuidora S/A",
        "cnpj": "96.453.427/0001-14"
    }, headers=headers)
    assert res_criar.status_code == 201
    fornecedor = res_criar.json()
    assert fornecedor["nome_fantasia"] == "Atacado Sul"
    assert fornecedor["razao_social"] == "Atacado Sul Distribuidora S/A"
    assert fornecedor["cnpj"] == "96453427000114"
    assert fornecedor["ativo"] is True
    fornecedor_id = fornecedor["id"]

    # 2. Obter Fornecedor
    res_obter = client.get(f"/fornecedores/{fornecedor_id}", headers=headers)
    assert res_obter.status_code == 200
    assert res_obter.json()["nome_fantasia"] == "Atacado Sul"

    # 3. Listar Fornecedores
    res_listar = client.get("/fornecedores/", headers=headers)
    assert res_listar.status_code == 200
    lista = res_listar.json()
    assert len(lista) >= 1
    assert any(f["id"] == fornecedor_id for f in lista)

    # 4. Atualizar Fornecedor
    res_atualizar = client.put(f"/fornecedores/{fornecedor_id}", json={
        "nome_fantasia": "Atacado Sul Novo",
        "razao_social": "Atacado Sul Distribuidora S/A",
        "ativo": False
    }, headers=headers)
    assert res_atualizar.status_code == 200
    fornecedor_att = res_atualizar.json()
    assert fornecedor_att["nome_fantasia"] == "Atacado Sul Novo"
    assert fornecedor_att["ativo"] is False


def test_criar_fornecedor_cnpj_duplicado(client: TestClient):
    token = setup_tenant_autenticado(client)
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Cria fornecedor pela primeira vez (CNPJ válido)
    res_criar1 = client.post("/fornecedores/", json={
        "nome_fantasia": "Fornecedor Alfa",
        "razao_social": "Fornecedor Alfa Ltda",
        "cnpj": "02.188.445/0001-72"
    }, headers=headers)
    assert res_criar1.status_code == 201

    # 2. Tenta criar outro com o mesmo CNPJ
    res_criar2 = client.post("/fornecedores/", json={
        "nome_fantasia": "Fornecedor Alfa Bis",
        "razao_social": "Fornecedor Alfa Bis Ltda",
        "cnpj": "02.188.445/0001-72"
    }, headers=headers)
    assert res_criar2.status_code == 400
    assert "cnpj" in res_criar2.json()["detail"].lower()
