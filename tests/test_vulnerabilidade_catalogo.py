import pytest
from fastapi.testclient import TestClient
from uuid import uuid4

def setup_dois_tenants(client: TestClient):
    """
    Função auxiliar para registrar e logar dois tenants diferentes.
    Retorna os tokens de acesso e os IDs de tenant correspondentes.
    """
    # Registrar Tenant A
    res_a = client.post("/auth/register", json={
        "nome_fantasia": "Rede Alfa",
        "razao_social": "Rede Alfa Lojas S/A",
        "cnpj": "81.477.811/0001-80",
        "dono_nome": "Dono Alfa",
        "dono_email": "alfa_dono@email.com",
        "dono_senha": "senha_dono_alfa"
    })
    assert res_a.status_code == 201
    tenant_a_id = res_a.json()["tenant_id"]

    # Logar Tenant A
    login_a = client.post("/auth/login", json={"email": "alfa_dono@email.com", "senha": "senha_dono_alfa"})
    assert login_a.status_code == 200
    token_a = login_a.json()["access_token"]

    # Registrar Tenant B
    res_b = client.post("/auth/register", json={
        "nome_fantasia": "Rede Beta",
        "razao_social": "Rede Beta Lojas S/A",
        "cnpj": "94.686.599/0001-02",
        "dono_nome": "Dono Beta",
        "dono_email": "beta_dono@email.com",
        "dono_senha": "senha_dono_beta"
    })
    assert res_b.status_code == 201
    tenant_b_id = res_b.json()["tenant_id"]

    # Logar Tenant B
    login_b = client.post("/auth/login", json={"email": "beta_dono@email.com", "senha": "senha_dono_beta"})
    assert login_b.status_code == 200
    token_b = login_b.json()["access_token"]

    return token_a, tenant_a_id, token_b, tenant_b_id


def test_produto_vulnerabilidade_tenant_isolation(client: TestClient):
    """
    Teste 1 (Vulnerabilidade): Garante que um Tenant A não consiga obter
    ou listar produtos cadastrados pelo Tenant B.
    """
    token_a, tenant_a_id, token_b, tenant_b_id = setup_dois_tenants(client)

    # 1. Tenant B cadastra um produto
    res_criar = client.post("/produtos/", json={
        "nome": "Smartphone Top B",
        "sku": "PHONE-B-123",
        "preco_custo": 1000.0,
        "preco_venda": 1500.0,
        "markup": 0.5
    }, headers={"Authorization": f"Bearer {token_b}"})
    assert res_criar.status_code == 201
    produto_b = res_criar.json()
    produto_b_id = produto_b["id"]

    # 2. Tenant A tenta obter o produto do Tenant B diretamente por ID
    res_obter = client.get(f"/produtos/{produto_b_id}", headers={"Authorization": f"Bearer {token_a}"})
    # Deve retornar 404 Not Found devido ao isolamento de tenant
    assert res_obter.status_code == 404

    # 3. Tenant A tenta listar todos os produtos
    res_listar = client.get("/produtos/", headers={"Authorization": f"Bearer {token_a}"})
    assert res_listar.status_code == 200
    produtos_alfa = res_listar.json()
    # A lista de produtos do Tenant A não deve conter o produto do Tenant B
    assert not any(p["id"] == produto_b_id for p in produtos_alfa)


def test_cliente_vulnerabilidade_tenant_isolation(client: TestClient):
    """
    Teste 2 (Vulnerabilidade): Garante que um Tenant A não consiga atualizar
    ou deletar informações de um cliente pertencente ao Tenant B.
    """
    token_a, tenant_a_id, token_b, tenant_b_id = setup_dois_tenants(client)

    # 1. Tenant B cadastra um cliente
    res_criar = client.post("/clientes/", json={
        "nome": "Cliente do Tenant B",
        "email": "clienteb@email.com",
        "documento": "12345678909"
    }, headers={"Authorization": f"Bearer {token_b}"})
    assert res_criar.status_code == 201
    cliente_b_id = res_criar.json()["id"]

    # 2. Tenant A tenta atualizar o cliente do Tenant B
    res_atualizar = client.put(f"/clientes/{cliente_b_id}", json={
        "nome": "Nome Modificado por Invasor",
        "email": "invasor@email.com",
        "ativo": False
    }, headers={"Authorization": f"Bearer {token_a}"})
    # Deve retornar 404 Not Found para indicar que o recurso não existe no tenant de A
    assert res_atualizar.status_code == 404


def test_fornecedor_vulnerabilidade_tenant_isolation(client: TestClient):
    """
    Teste 3 (Vulnerabilidade/Bypass): Garante que uma tentativa do Tenant A
    de cadastrar um fornecedor forçando o tenant_id do Tenant B no corpo
    ou em cabeçalhos extras seja totalmente ignorada, salvando o recurso no Tenant A.
    """
    token_a, tenant_a_id, token_b, tenant_b_id = setup_dois_tenants(client)

    # Tenant A tenta criar um fornecedor, injetando o tenant_id de B no JSON
    res_criar = client.post("/fornecedores/", json={
        "nome_fantasia": "Distribuidora A",
        "razao_social": "Distribuidora A Ltda",
        "cnpj": "11222333000181",
        "tenant_id": str(tenant_b_id)  # Tentativa de injeção maliciosa de tenant
    }, headers={"Authorization": f"Bearer {token_a}"})
    
    assert res_criar.status_code == 201
    fornecedor_salvo = res_criar.json()
    
    # O tenant_id no retorno deve ser o do Tenant A (autenticado), ignorando a tentativa de injeção
    assert fornecedor_salvo["tenant_id"] == str(tenant_a_id)


def test_produto_falha_validacao_campos(client: TestClient):
    """
    Teste 4 (Falha): Verifica se a validação impede a criação de produtos com
    dados incorretos ou em formatos inválidos (como preços negativos ou campos vazios).
    """
    token_a, tenant_a_id, _, _ = setup_dois_tenants(client)

    # Tentativa 1: Preço de custo negativo
    res_custo_negativo = client.post("/produtos/", json={
        "nome": "Produto Invalido",
        "sku": "SKU-FAIL-1",
        "preco_custo": -10.0,
        "preco_venda": 15.0,
        "markup": 0.5
    }, headers={"Authorization": f"Bearer {token_a}"})
    assert res_custo_negativo.status_code == 422

    # Tentativa 2: Preço de venda negativo
    res_venda_negativo = client.post("/produtos/", json={
        "nome": "Produto Invalido 2",
        "sku": "SKU-FAIL-2",
        "preco_custo": 10.0,
        "preco_venda": -5.0,
        "markup": 0.5
    }, headers={"Authorization": f"Bearer {token_a}"})
    assert res_venda_negativo.status_code == 422

    # Tentativa 3: Nome vazio
    res_nome_vazio = client.post("/produtos/", json={
        "nome": "   ",
        "sku": "SKU-FAIL-3",
        "preco_custo": 10.0,
        "preco_venda": 15.0,
        "markup": 0.5
    }, headers={"Authorization": f"Bearer {token_a}"})
    assert res_nome_vazio.status_code == 422 or res_nome_vazio.status_code == 400


def test_fornecedor_falha_cnpj_invalido(client: TestClient):
    """
    Teste 5 (Falha): Garante que a API recuse cadastrar fornecedores
    com CNPJs matematicamente inválidos.
    """
    token_a, tenant_a_id, _, _ = setup_dois_tenants(client)

    # Envia CNPJ com dígitos verificadores incorretos (ex: 11.222.333/0001-00)
    res_criar = client.post("/fornecedores/", json={
        "nome_fantasia": "Fornecedor Invalido",
        "razao_social": "Fornecedor Invalido S/A",
        "cnpj": "11.222.333/0001-00"
    }, headers={"Authorization": f"Bearer {token_a}"})
    
    # Deve falhar com 400 Bad Request ou 422 Unprocessable Entity
    assert res_criar.status_code in (400, 422)
