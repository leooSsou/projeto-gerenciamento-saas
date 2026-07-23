import pytest
from fastapi.testclient import TestClient
from uuid import uuid4

# CNPJs matematicamente válidos para evitar erros de validação
CNPJ_A = "26.762.981/0001-06"
CNPJ_B = "96.453.427/0001-14"
CNPJ_LOJA_A = "02.188.445/0001-72"
CNPJ_LOJA_B = "44.997.002/0001-72"

def registrar_e_autenticar(client: TestClient, prefix: str, cnpj: str) -> str:
    """
    Auxiliar para registrar um tenant e retornar o token de acesso JWT.
    """
    client.post("/auth/register", json={
        "nome_fantasia": f"{prefix} Rede",
        "razao_social": f"{prefix} Razao Social S/A",
        "cnpj": cnpj,
        "dono_nome": f"Dono {prefix}",
        "dono_email": f"{prefix.lower()}@email.com",
        "dono_senha": "senha_segura_123"
    })
    
    login = client.post("/auth/login", json={
        "email": f"{prefix.lower()}@email.com",
        "senha": "senha_segura_123"
    })
    return login.json()["access_token"]


def test_fluxo_movimentacao_estoque_sucesso(client: TestClient) -> None:
    # 1. Registrar e autenticar Tenant A
    token_a = registrar_e_autenticar(client, "TenantA", CNPJ_A)
    headers_a = {"Authorization": f"Bearer {token_a}"}
    
    # 2. Criar Loja A
    res_loja = client.post("/lojas/", json={
        "nome": "Loja A1",
        "cnpj": CNPJ_LOJA_A,
        "endereco": "Rua A, 100"
    }, headers=headers_a)
    loja_id = res_loja.json()["id"]
    
    # 3. Criar Produto A
    res_prod = client.post("/produtos/", json={
        "nome": "Smartphone",
        "sku": "SMART-01",
        "preco_custo": 1000.0,
        "preco_venda": 1500.0,
        "markup": 0.5
    }, headers=headers_a)
    produto_id = res_prod.json()["id"]
    
    # 4. Registrar Entrada de Estoque
    res_mov1 = client.post("/estoque/movimentar", json={
        "loja_id": loja_id,
        "produto_id": produto_id,
        "tipo": "ENTRADA",
        "quantidade": 10,
        "motivo": "Compra inicial"
    }, headers=headers_a)
    
    assert res_mov1.status_code == 200
    res_data1 = res_mov1.json()
    assert res_data1["saldo"]["quantidade"] == 10
    assert res_data1["movimentacao"]["quantidade"] == 10
    assert res_data1["movimentacao"]["tipo"] == "ENTRADA"
    
    # 5. Registrar Saída de Estoque (Parcial)
    res_mov2 = client.post("/estoque/movimentar", json={
        "loja_id": loja_id,
        "produto_id": produto_id,
        "tipo": "SAIDA",
        "quantidade": 3,
        "motivo": "Venda cliente"
    }, headers=headers_a)
    
    assert res_mov2.status_code == 200
    res_data2 = res_mov2.json()
    assert res_data2["saldo"]["quantidade"] == 7
    assert res_data2["movimentacao"]["quantidade"] == 3
    assert res_data2["movimentacao"]["tipo"] == "SAIDA"


def test_movimentacao_estoque_insuficiente_retorna_400(client: TestClient) -> None:
    token_a = registrar_e_autenticar(client, "TenantA_Insuficiente", CNPJ_A)
    headers_a = {"Authorization": f"Bearer {token_a}"}
    
    res_loja = client.post("/lojas/", json={"nome": "Loja A1", "cnpj": CNPJ_LOJA_A, "endereco": "Rua A"}, headers=headers_a)
    loja_id = res_loja.json()["id"]
    
    res_prod = client.post("/produtos/", json={"nome": "Notebook", "sku": "NOTE-01", "preco_custo": 2000.0, "preco_venda": 3000.0, "markup": 0.5}, headers=headers_a)
    produto_id = res_prod.json()["id"]
    
    # Tentativa de saída sem estoque prévio (saldo = 0)
    res_mov = client.post("/estoque/movimentar", json={
        "loja_id": loja_id,
        "produto_id": produto_id,
        "tipo": "SAIDA",
        "quantidade": 1,
        "motivo": "Retirada teste"
    }, headers=headers_a)
    
    assert res_mov.status_code == 400
    assert "Estoque insuficiente" in res_mov.json()["detail"]


# ==============================================================================
# 🔒 TESTES EXTRAS DE SEGURANÇA E VULNERABILIDADE
# ==============================================================================

def test_seguranca_bola_acesso_cruzado_deve_retornar_404(client: TestClient) -> None:
    """
    BOLA (Broken Object Level Authorization): Um usuário do Tenant A tenta movimentar
    estoque de uma loja ou produto pertencente ao Tenant B.
    """
    # Setup Tenant A
    token_a = registrar_e_autenticar(client, "UserA", CNPJ_A)
    headers_a = {"Authorization": f"Bearer {token_a}"}
    res_loja_a = client.post("/lojas/", json={"nome": "Loja A", "cnpj": CNPJ_LOJA_A, "endereco": "Rua A"}, headers=headers_a)
    loja_a_id = res_loja_a.json()["id"]
    res_prod_a = client.post("/produtos/", json={"nome": "Prod A", "sku": "PROD-A", "preco_custo": 10.0, "preco_venda": 15.0, "markup": 0.5}, headers=headers_a)
    prod_a_id = res_prod_a.json()["id"]
    
    # Setup Tenant B
    token_b = registrar_e_autenticar(client, "UserB", CNPJ_B)
    headers_b = {"Authorization": f"Bearer {token_b}"}
    res_loja_b = client.post("/lojas/", json={"nome": "Loja B", "cnpj": CNPJ_LOJA_B, "endereco": "Rua B"}, headers=headers_b)
    loja_b_id = res_loja_b.json()["id"]
    res_prod_b = client.post("/produtos/", json={"nome": "Prod B", "sku": "PROD-B", "preco_custo": 20.0, "preco_venda": 30.0, "markup": 0.5}, headers=headers_b)
    prod_b_id = res_prod_b.json()["id"]

    # 1. Tenant A tenta movimentar estoque usando a Loja do Tenant B (BOLA)
    res_bola_loja = client.post("/estoque/movimentar", json={
        "loja_id": loja_b_id, # Loja do Tenant B
        "produto_id": prod_a_id,
        "tipo": "ENTRADA",
        "quantidade": 10,
        "motivo": "Invasao"
    }, headers=headers_a)
    
    # Deve retornar 404 (a loja não existe no contexto do Tenant A)
    assert res_bola_loja.status_code == 404
    assert "Loja com identificador" in res_bola_loja.json()["detail"]

    # 2. Tenant A tenta movimentar estoque usando o Produto do Tenant B (BOLA)
    res_bola_prod = client.post("/estoque/movimentar", json={
        "loja_id": loja_a_id,
        "produto_id": prod_b_id, # Produto do Tenant B
        "tipo": "ENTRADA",
        "quantidade": 10,
        "motivo": "Invasao"
    }, headers=headers_a)
    
    # Deve retornar 404 (o produto não existe no contexto do Tenant A)
    assert res_bola_prod.status_code == 404
    assert "Produto com identificador" in res_bola_prod.json()["detail"]


def test_seguranca_vazamento_tenant_saldos_e_movimentacoes(client: TestClient) -> None:
    """
    Tenant Leakage (SaaS Leakage): Garante que consultas de saldos e movimentações
    de estoque nunca vazem dados entre tenants diferentes.
    """
    # Tenant A
    token_a = registrar_e_autenticar(client, "TenantA_Leak", CNPJ_A)
    headers_a = {"Authorization": f"Bearer {token_a}"}
    res_loja_a = client.post("/lojas/", json={"nome": "Loja A", "cnpj": CNPJ_LOJA_A, "endereco": "Rua A"}, headers=headers_a)
    loja_a_id = res_loja_a.json()["id"]
    res_prod_a = client.post("/produtos/", json={"nome": "Prod A", "sku": "P-A", "preco_custo": 10.0, "preco_venda": 15.0, "markup": 0.5}, headers=headers_a)
    prod_a_id = res_prod_a.json()["id"]
    client.post("/estoque/movimentar", json={"loja_id": loja_a_id, "produto_id": prod_a_id, "tipo": "ENTRADA", "quantidade": 5, "motivo": "Carga A"}, headers=headers_a)

    # Tenant B
    token_b = registrar_e_autenticar(client, "TenantB_Leak", CNPJ_B)
    headers_b = {"Authorization": f"Bearer {token_b}"}
    res_loja_b = client.post("/lojas/", json={"nome": "Loja B", "cnpj": CNPJ_LOJA_B, "endereco": "Rua B"}, headers=headers_b)
    loja_b_id = res_loja_b.json()["id"]
    res_prod_b = client.post("/produtos/", json={"nome": "Prod B", "sku": "P-B", "preco_custo": 20.0, "preco_venda": 30.0, "markup": 0.5}, headers=headers_b)
    prod_b_id = res_prod_b.json()["id"]
    client.post("/estoque/movimentar", json={"loja_id": loja_b_id, "produto_id": prod_b_id, "tipo": "ENTRADA", "quantidade": 8, "motivo": "Carga B"}, headers=headers_b)

    # Chamar rotas como Tenant A e garantir que só vê o estoque do Tenant A
    res_saldos = client.get("/estoque/saldos", headers=headers_a)
    saldos_json = res_saldos.json()
    assert len(saldos_json) == 1
    assert saldos_json[0]["quantidade"] == 5
    assert saldos_json[0]["loja_id"] == loja_a_id

    res_movs = client.get("/estoque/movimentacoes", headers=headers_a)
    movs_json = res_movs.json()
    assert len(movs_json) == 1
    assert movs_json[0]["motivo"] == "Carga A"


def test_seguranca_sql_injection_motivo_deve_ser_tratado_com_seguranca(client: TestClient) -> None:
    """
    SQL Injection: Tenta passar comandos SQL no campo 'motivo'.
    Como usamos SQLAlchemy ORM, o binding de parâmetros é automático
    e o SQL Injection deve falhar, salvando a string de forma literal.
    """
    token_a = registrar_e_autenticar(client, "TenantSQLI", CNPJ_A)
    headers_a = {"Authorization": f"Bearer {token_a}"}
    
    res_loja = client.post("/lojas/", json={"nome": "Loja A", "cnpj": CNPJ_LOJA_A, "endereco": "Rua A"}, headers=headers_a)
    loja_id = res_loja.json()["id"]
    res_prod = client.post("/produtos/", json={"nome": "Prod A", "sku": "P-SQL", "preco_custo": 10.0, "preco_venda": 15.0, "markup": 0.5}, headers=headers_a)
    prod_id = res_prod.json()["id"]

    payload_sqli = "'; DROP TABLE estoque_saldos; --"
    res_mov = client.post("/estoque/movimentar", json={
        "loja_id": loja_id,
        "produto_id": prod_id,
        "tipo": "ENTRADA",
        "quantidade": 10,
        "motivo": payload_sqli
    }, headers=headers_a)

    assert res_mov.status_code == 200
    assert res_mov.json()["movimentacao"]["motivo"] == payload_sqli

    # Garante que a tabela não foi dropada e a consulta de saldos continua ativa
    res_saldos = client.get("/estoque/saldos", headers=headers_a)
    assert res_saldos.status_code == 200
    assert len(res_saldos.json()) == 1


def test_seguranca_autenticacao_rotas_estoque_devem_exigir_jwt(client: TestClient) -> None:
    """
    Auth Security: Tenta acessar endpoints sem autenticação válida.
    """
    # 1. Sem token
    res1 = client.post("/estoque/movimentar", json={})
    assert res1.status_code == 401
    
    res2 = client.get("/estoque/saldos")
    assert res2.status_code == 401

    res3 = client.get("/estoque/movimentacoes")
    assert res3.status_code == 401

    # 2. Token inválido/falso
    headers_invalido = {"Authorization": "Bearer token_falso_e_invalido"}
    res4 = client.get("/estoque/saldos", headers=headers_invalido)
    assert res4.status_code == 401
