import pytest
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from fastapi.testclient import TestClient
from uuid import uuid4
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.infrastructure.database.models import (
    Base,
    TenantModel,
    LojaModel,
    ProdutoModel,
    EstoqueSaldoModel,
    EstoqueMovimentacaoModel,
)
from src.domain.entities.tenant import Tenant
from src.domain.entities.loja import Loja
from src.domain.entities.produto import Produto
from src.domain.entities.estoque_saldo import EstoqueSaldo
from src.domain.exceptions.business import EstoqueInsuficienteException
from src.use_cases.estoque.registrar_movimentacao import (
    RegistrarMovimentacaoEstoque,
    RegistrarMovimentacaoEstoqueInput,
)
from src.infrastructure.database.repositorios_concrete import (
    RepositorioTenantSQLAlchemy,
    RepositorioLojaSQLAlchemy,
    RepositorioProdutoSQLAlchemy,
    RepositorioEstoqueSaldoSQLAlchemy,
    RepositorioEstoqueMovimentacaoSQLAlchemy,
)

CNPJ_A = "26.762.981/0001-06"
CNPJ_LOJA_A = "02.188.445/0001-72"

# Conexão com o banco de dados PostgreSQL real para suportar locks pessimistas
pg_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres_password@postgres:5432/gerenciador_saas")
pg_engine = create_engine(pg_url)
PgSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=pg_engine)

# Verifica se o PostgreSQL está disponível para pular os testes se não estiver
try:
    with pg_engine.connect() as conn:
        postgres_available = True
except Exception:
    postgres_available = False

pytestmark = pytest.mark.skipif(
    not postgres_available,
    reason="PostgreSQL não está disponível para testar concorrência real (requer contêineres Docker ativos)"
)


@pytest.fixture
def setup_pg_concorrencia():
    """
    Cria tenant, loja e produto no banco de dados real.
    Garante a limpeza de todos os registros criados após o término do teste.
    """
    # Garante que as tabelas existem no Postgres antes de realizar queries nelas
    Base.metadata.create_all(bind=pg_engine)
    
    session = PgSessionLocal()
    session.info["ignore_tenant_filter"] = True

    
    # 1. Limpa qualquer resquício anterior com o mesmo CNPJ
    existing_tenant = session.query(TenantModel).filter(TenantModel.cnpj == "26762981000106").first()
    if existing_tenant:
        tenant_id = existing_tenant.id
        session.query(EstoqueMovimentacaoModel).filter(EstoqueMovimentacaoModel.tenant_id == tenant_id).delete()
        session.query(EstoqueSaldoModel).filter(EstoqueSaldoModel.tenant_id == tenant_id).delete()
        session.query(ProdutoModel).filter(ProdutoModel.tenant_id == tenant_id).delete()
        session.query(LojaModel).filter(LojaModel.tenant_id == tenant_id).delete()
        session.query(TenantModel).filter(TenantModel.id == tenant_id).delete()
        session.commit()
    
    repo_tenant = RepositorioTenantSQLAlchemy(session)
    repo_loja = RepositorioLojaSQLAlchemy(session)
    repo_produto = RepositorioProdutoSQLAlchemy(session)
    
    tenant = repo_tenant.salvar(Tenant(
        nome_fantasia="SaaS Concorrencia Real",
        razao_social="SaaS Concorrencia Real Ltda",
        cnpj=CNPJ_A
    ))
    
    loja = repo_loja.salvar(Loja(
        nome="Filial Concorrencia Real",
        cnpj=CNPJ_LOJA_A,
        endereco="Rua da Concorrencia Real, 123",
        tenant_id=tenant.id
    ))
    
    produto = repo_produto.salvar(Produto(
        nome="Notebook Ultra Concorrente Real",
        sku="NOTE-CONC-REAL-01",
        preco_custo=4000.0,
        preco_venda=6000.0,
        markup=0.5,
        tenant_id=tenant.id
    ))
    
    session.commit()
    session.close()
    
    yield tenant.id, loja.id, produto.id
    
    # Executa a limpeza pós-teste
    clean_session = PgSessionLocal()
    clean_session.info["ignore_tenant_filter"] = True
    clean_session.query(EstoqueMovimentacaoModel).filter(EstoqueMovimentacaoModel.tenant_id == tenant.id).delete()
    clean_session.query(EstoqueSaldoModel).filter(EstoqueSaldoModel.tenant_id == tenant.id).delete()
    clean_session.query(ProdutoModel).filter(ProdutoModel.tenant_id == tenant.id).delete()
    clean_session.query(LojaModel).filter(LojaModel.tenant_id == tenant.id).delete()
    clean_session.query(TenantModel).filter(TenantModel.id == tenant.id).delete()
    clean_session.commit()
    clean_session.close()


def test_concorrencia_debitos_simultaneos(setup_pg_concorrencia) -> None:
    """
    Simula 10 threads debitando estoque simultaneamente no PostgreSQL com locking pessimista.
    Saldo inicial: 100.
    Cada thread debita: 10.
    Saldo final esperado: 0.
    Total de movimentações: 10.
    """
    tenant_id, loja_id, produto_id = setup_pg_concorrencia
    
    # 1. Salva o saldo inicial de 100
    session = PgSessionLocal()
    session.info["tenant_id"] = tenant_id
    repo_saldo = RepositorioEstoqueSaldoSQLAlchemy(session)
    repo_saldo.salvar(EstoqueSaldo(
        loja_id=loja_id,
        produto_id=produto_id,
        quantidade=100,
        tenant_id=tenant_id
    ))
    session.commit()
    session.close()
    
    # Função executada por cada thread
    def executar_debito():
        thread_session = PgSessionLocal()
        thread_session.info["tenant_id"] = tenant_id
        
        try:
            s_repo = RepositorioEstoqueSaldoSQLAlchemy(thread_session)
            m_repo = RepositorioEstoqueMovimentacaoSQLAlchemy(thread_session)
            l_repo = RepositorioLojaSQLAlchemy(thread_session)
            p_repo = RepositorioProdutoSQLAlchemy(thread_session)
            
            use_case = RegistrarMovimentacaoEstoque(s_repo, m_repo, l_repo, p_repo)
            
            input_data = RegistrarMovimentacaoEstoqueInput(
                loja_id=loja_id,
                produto_id=produto_id,
                tipo="SAIDA",
                quantidade=10,
                motivo="Debito concorrente",
                tenant_id=tenant_id
            )
            use_case.executar(input_data)
            thread_session.commit()
            return True
        except Exception as e:
            thread_session.rollback()
            return e
        finally:
            thread_session.close()

    # Dispara as threads concorrentemente
    resultados = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(executar_debito) for _ in range(10)]
        for fut in as_completed(futures):
            resultados.append(fut.result())
            
    # Verifica se alguma thread falhou inesperadamente
    erros = [r for r in resultados if r is not True]
    assert len(erros) == 0, f"Ocorreram erros nas threads: {erros}"

    # Verifica o saldo final
    session = PgSessionLocal()
    session.info["tenant_id"] = tenant_id
    repo_saldo = RepositorioEstoqueSaldoSQLAlchemy(session)
    saldo_final = repo_saldo.obter_por_loja_e_produto(loja_id, produto_id, tenant_id)
    assert saldo_final.quantidade == 0
    
    # Verifica o total de movimentações gravadas
    repo_mov = RepositorioEstoqueMovimentacaoSQLAlchemy(session)
    movs = repo_mov.listar_por_loja_e_produto(loja_id, produto_id, tenant_id)
    assert len(movs) == 10
    session.close()


def test_concorrencia_debitos_excedidos(setup_pg_concorrencia) -> None:
    """
    Simula 10 threads tentando debitar 10 unidades cada.
    Saldo inicial: 50.
    Esperado: 5 transações com sucesso e 5 falhando com EstoqueInsuficienteException.
    Saldo final: 0.
    Total de movimentações de saída no ledger: 5.
    """
    tenant_id, loja_id, produto_id = setup_pg_concorrencia
    
    # 1. Salva o saldo inicial de 50
    session = PgSessionLocal()
    session.info["tenant_id"] = tenant_id
    repo_saldo = RepositorioEstoqueSaldoSQLAlchemy(session)
    repo_saldo.salvar(EstoqueSaldo(
        loja_id=loja_id,
        produto_id=produto_id,
        quantidade=50,
        tenant_id=tenant_id
    ))
    session.commit()
    session.close()

    def executar_debito():
        thread_session = PgSessionLocal()
        thread_session.info["tenant_id"] = tenant_id
        
        try:
            s_repo = RepositorioEstoqueSaldoSQLAlchemy(thread_session)
            m_repo = RepositorioEstoqueMovimentacaoSQLAlchemy(thread_session)
            l_repo = RepositorioLojaSQLAlchemy(thread_session)
            p_repo = RepositorioProdutoSQLAlchemy(thread_session)
            
            use_case = RegistrarMovimentacaoEstoque(s_repo, m_repo, l_repo, p_repo)
            
            input_data = RegistrarMovimentacaoEstoqueInput(
                loja_id=loja_id,
                produto_id=produto_id,
                tipo="SAIDA",
                quantidade=10,
                motivo="Tentativa debito concorrente",
                tenant_id=tenant_id
            )
            use_case.executar(input_data)
            thread_session.commit()
            return "SUCESSO"
        except EstoqueInsuficienteException:
            thread_session.rollback()
            return "INSUFICIENTE"
        except Exception as e:
            thread_session.rollback()
            return f"ERRO: {str(e)}"
        finally:
            thread_session.close()

    resultados = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(executar_debito) for _ in range(10)]
        for fut in as_completed(futures):
            resultados.append(fut.result())
            
    sucessos = [r for r in resultados if r == "SUCESSO"]
    insuficientes = [r for r in resultados if r == "INSUFICIENTE"]
    outros_erros = [r for r in resultados if r not in ("SUCESSO", "INSUFICIENTE")]
    
    assert len(outros_erros) == 0, f"Erros inesperados nas threads: {outros_erros}"
    assert len(sucessos) == 5
    assert len(insuficientes) == 5

    session = PgSessionLocal()
    session.info["tenant_id"] = tenant_id
    repo_saldo = RepositorioEstoqueSaldoSQLAlchemy(session)
    saldo_final = repo_saldo.obter_por_loja_e_produto(loja_id, produto_id, tenant_id)
    assert saldo_final.quantidade == 0
    
    repo_mov = RepositorioEstoqueMovimentacaoSQLAlchemy(session)
    movs = repo_mov.listar_por_loja_e_produto(loja_id, produto_id, tenant_id)
    assert len(movs) == 5
    session.close()


# ==============================================================================
# 🔒 TESTES DE VULNERABILIDADE (OVERFLOW, VALORES E IMUTABILIDADE)
# ==============================================================================

def test_vulnerabilidade_integer_overflow_e_valores_invalidos(client: TestClient) -> None:
    """
    Garante que tentativas de overflow de inteiros (enviar quantidades extremas)
    ou valores negativos/nulos são rejeitadas pelo schema Pydantic antes de atingir o banco.
    """
    client.post("/auth/register", json={
        "nome_fantasia": "Tech Overflow",
        "razao_social": "Tech Overflow Ltda",
        "cnpj": CNPJ_A,
        "dono_nome": "Dono Tech",
        "dono_email": "techoverflow@email.com",
        "dono_senha": "senha_segura_123"
    })
    login = client.post("/auth/login", json={"email": "techoverflow@email.com", "senha": "senha_segura_123"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Quantidade acima do limite do schema Pydantic (limite 1.000.000)
    res_overflow = client.post("/estoque/movimentar", json={
        "loja_id": str(uuid4()),
        "produto_id": str(uuid4()),
        "tipo": "ENTRADA",
        "quantidade": 1000001,  # Acima de 1.000.000
        "motivo": "Ataque overflow"
    }, headers=headers)
    assert res_overflow.status_code == 422

    # 2. Quantidade negativa
    res_negativa = client.post("/estoque/movimentar", json={
        "loja_id": str(uuid4()),
        "produto_id": str(uuid4()),
        "tipo": "ENTRADA",
        "quantidade": -10,
        "motivo": "Ajuste negativo"
    }, headers=headers)
    assert res_negativa.status_code == 422

    # 3. Quantidade zero
    res_zero = client.post("/estoque/movimentar", json={
        "loja_id": str(uuid4()),
        "produto_id": str(uuid4()),
        "tipo": "ENTRADA",
        "quantidade": 0,
        "motivo": "Ajuste zero"
    }, headers=headers)
    assert res_zero.status_code == 422


def test_vulnerabilidade_ledger_imutabilidade(client: TestClient) -> None:
    """
    Garante que não existem rotas expostas para atualizar (PUT/PATCH) ou
    deletar (DELETE) dados do ledger de movimentações de estoque.
    """
    client.post("/auth/register", json={
        "nome_fantasia": "Tech Imutavel",
        "razao_social": "Tech Imutavel Ltda",
        "cnpj": CNPJ_A,
        "dono_nome": "Dono Tech",
        "dono_email": "techimutavel@email.com",
        "dono_senha": "senha_segura_123"
    })
    login = client.post("/auth/login", json={"email": "techimutavel@email.com", "senha": "senha_segura_123"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Tenta apagar histórico (DELETE)
    res_del = client.delete("/estoque/movimentacoes", headers=headers)
    assert res_del.status_code == 405  # Method Not Allowed

    # Tenta atualizar histórico (PUT)
    res_put = client.put("/estoque/movimentacoes", json={}, headers=headers)
    assert res_put.status_code == 405  # Method Not Allowed

    # Tenta apagar saldos (DELETE)
    res_del_saldo = client.delete("/estoque/saldos", headers=headers)
    assert res_del_saldo.status_code == 405  # Method Not Allowed
