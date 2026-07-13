from fastapi.testclient import TestClient

def test_crud_lojas_fluxo_completo(client: TestClient):
    """
    Testa o fluxo completo de cadastro, listagem, busca e edição de Lojas por uma API autenticada.
    """
    # 1. Registra um Tenant + Usuário Dono para obter as credenciais
    res_reg = client.post("/auth/register", json={
        "nome_fantasia": "Rede Centro",
        "razao_social": "Rede Centro Lojas Ltda",
        "cnpj": "69.199.034/0001-53",
        "dono_nome": "Marcos",
        "dono_email": "marcos@centro.com",
        "dono_senha": "senha_segura_123"
    })
    assert res_reg.status_code == 201
    
    # 2. Login para obter token
    res_login = client.post("/auth/login", json={
        "email": "marcos@centro.com",
        "senha": "senha_segura_123"
    })
    assert res_login.status_code == 200
    token = res_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Listagem inicial de lojas deve ser vazia
    res_list = client.get("/lojas/", headers=headers)
    assert res_list.status_code == 200
    assert len(res_list.json()) == 0

    # 4. Cadastro de nova Loja (HTTP 201)
    payload_loja = {
        "nome": "Filial Shopping",
        "cnpj": "70.237.989/0001-37",
        "endereco": "Av. Principal, 1000 - Loja 15"
    }
    res_create = client.post("/lojas/", json=payload_loja, headers=headers)
    assert res_create.status_code == 201
    data_created = res_create.json()
    assert data_created["nome"] == "Filial Shopping"
    assert data_created["cnpj"] == "70237989000137"  # Deve estar limpo no retorno
    assert data_created["endereco"] == "Av. Principal, 1000 - Loja 15"
    assert data_created["ativo"] is True
    assert "id" in data_created
    loja_id = data_created["id"]

    # 5. Tentativa de cadastrar a mesma Loja com CNPJ duplicado (HTTP 400)
    res_dup = client.post("/lojas/", json={
        "nome": "Filial Shopping Duplicada",
        "cnpj": "70.237.989/0001-37",
        "endereco": "Av. Outro, 50"
    }, headers=headers)
    assert res_dup.status_code == 400
    assert "CNPJ" in res_dup.json()["detail"]

    # 6. Obter Loja por ID (HTTP 200)
    res_get = client.get(f"/lojas/{loja_id}", headers=headers)
    assert res_get.status_code == 200
    assert res_get.json()["nome"] == "Filial Shopping"

    # 7. Atualização dos dados da Loja (HTTP 200)
    payload_update = {
        "nome": "Filial Shopping (Reformada)",
        "endereco": "Av. Principal, 1000 - Lojas 15 e 16",
        "ativo": False
    }
    res_update = client.put(f"/lojas/{loja_id}", json=payload_update, headers=headers)
    assert res_update.status_code == 200
    data_updated = res_update.json()
    assert data_updated["nome"] == "Filial Shopping (Reformada)"
    assert data_updated["endereco"] == "Av. Principal, 1000 - Lojas 15 e 16"
    assert data_updated["ativo"] is False
    assert data_updated["cnpj"] == "70237989000137"  # CNPJ imutável


def test_isolamento_lojas_multi_tenant(client: TestClient):
    """
    Testa a restrição rígida de tenant nas rotas de lojas, prevenindo vazamentos de dados (SaaS Leakage).
    """
    # 1. Registra Tenant A e obtém token
    client.post("/auth/register", json={
        "nome_fantasia": "Tenant A",
        "razao_social": "Empresa A S/A",
        "cnpj": "70.230.856/0001-39",
        "dono_nome": "Admin A",
        "dono_email": "admina@email.com",
        "dono_senha": "senha_segura"
    })
    token_a = client.post("/auth/login", json={"email": "admina@email.com", "senha": "senha_segura"}).json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # 2. Registra Tenant B e obtém token
    client.post("/auth/register", json={
        "nome_fantasia": "Tenant B",
        "razao_social": "Empresa B S/A",
        "cnpj": "31.257.913/0001-11",
        "dono_nome": "Admin B",
        "dono_email": "adminb@email.com",
        "dono_senha": "senha_segura"
    })
    token_b = client.post("/auth/login", json={"email": "adminb@email.com", "senha": "senha_segura"}).json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # 3. Tenant A cria uma loja
    res_loja_a = client.post("/lojas/", json={
        "nome": "Loja do Tenant A",
        "cnpj": "43.269.349/0001-36",
        "endereco": "Rua do Tenant A, 123"
    }, headers=headers_a)
    assert res_loja_a.status_code == 201
    loja_a_id = res_loja_a.json()["id"]

    # 4. Tenant B tenta listar as lojas. Não deve vir a loja do Tenant A.
    res_list_b = client.get("/lojas/", headers=headers_b)
    assert res_list_b.status_code == 200
    assert len(res_list_b.json()) == 0

    # 5. Tenant B tenta buscar a loja do Tenant A pelo ID direto. Deve retornar HTTP 404 (Não Encontrado).
    res_get_b = client.get(f"/lojas/{loja_a_id}", headers=headers_b)
    assert res_get_b.status_code == 404

    # 6. Tenant B tenta editar a loja do Tenant A. Deve retornar HTTP 404 (Não Encontrado) e impedir qualquer alteração.
    res_put_b = client.put(f"/lojas/{loja_a_id}", json={
        "nome": "Loja Roubada",
        "endereco": "Rua Hacker, 0",
        "ativo": False
    }, headers=headers_b)
    assert res_put_b.status_code == 404

    # Confirmar que os dados da loja A continuam inalterados acessando com o token do Tenant A
    res_get_a = client.get(f"/lojas/{loja_a_id}", headers=headers_a)
    assert res_get_a.status_code == 200
    assert res_get_a.json()["nome"] == "Loja do Tenant A"
