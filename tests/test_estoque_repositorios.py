import pytest
from uuid import uuid4
from datetime import datetime
from sqlalchemy.orm import Session

from src.domain.entities.tenant import Tenant
from src.domain.entities.loja import Loja
from src.domain.entities.produto import Produto
from src.domain.entities.estoque_saldo import EstoqueSaldo
from src.domain.entities.estoque_movimentacao import EstoqueMovimentacao
from src.infrastructure.database.repositorios_concrete import (
    RepositorioTenantSQLAlchemy,
    RepositorioLojaSQLAlchemy,
    RepositorioProdutoSQLAlchemy,
    RepositorioEstoqueSaldoSQLAlchemy,
    RepositorioEstoqueMovimentacaoSQLAlchemy,
)

@pytest.fixture
def setup_dados(db_session: Session):
    """
    Fixture para criar tenant, loja e produto no banco de dados.
    """
    db_session.info["ignore_tenant_filter"] = True
    
    repo_tenant = RepositorioTenantSQLAlchemy(db_session)
    repo_loja = RepositorioLojaSQLAlchemy(db_session)
    repo_produto = RepositorioProdutoSQLAlchemy(db_session)
    
    tenant = repo_tenant.salvar(Tenant(
        nome_fantasia="Lojas do Teste",
        razao_social="Lojas do Teste Ltda",
        cnpj="26.762.981/0001-06"
    ))
    
    loja = repo_loja.salvar(Loja(
        nome="Filial Norte",
        cnpj="02.188.445/0001-72",
        endereco="Av Norte, 100",
        tenant_id=tenant.id
    ))
    
    produto = repo_produto.salvar(Produto(
        nome="Notebook Gamer",
        sku="NOTE-GAME-01",
        preco_custo=3000.0,
        preco_venda=4500.0,
        markup=0.5,
        tenant_id=tenant.id
    ))
    
    db_session.commit()
    db_session.info["ignore_tenant_filter"] = False
    
    return tenant, loja, produto

def test_persistir_e_obter_estoque_saldo(db_session: Session, setup_dados) -> None:
    tenant, loja, produto = setup_dados
    db_session.info["tenant_id"] = tenant.id
    
    repo_saldo = RepositorioEstoqueSaldoSQLAlchemy(db_session)
    
    # 1. Salvar novo saldo
    saldo = EstoqueSaldo(
        loja_id=loja.id,
        produto_id=produto.id,
        quantidade=50,
        tenant_id=tenant.id
    )
    saldo_salvo = repo_saldo.salvar(saldo)
    assert saldo_salvo.id is not None
    assert saldo_salvo.quantidade == 50
    
    # 2. Obter saldo (sem lock)
    saldo_obtido = repo_saldo.obter_por_loja_e_produto(loja.id, produto.id, tenant.id)
    assert saldo_obtido is not None
    assert saldo_obtido.quantidade == 50
    assert saldo_obtido.id == saldo_salvo.id

    # 3. Obter saldo com lock
    saldo_com_lock = repo_saldo.obter_por_loja_e_produto_com_lock(loja.id, produto.id, tenant.id)
    assert saldo_com_lock is not None
    assert saldo_com_lock.quantidade == 50
    
    # 4. Atualizar saldo
    saldo_atualizado = EstoqueSaldo(
        id=saldo_salvo.id,
        loja_id=loja.id,
        produto_id=produto.id,
        quantidade=100,
        tenant_id=tenant.id
    )
    repo_saldo.salvar(saldo_atualizado)
    db_session.commit()
    
    saldo_final = repo_saldo.obter_por_loja_e_produto(loja.id, produto.id, tenant.id)
    assert saldo_final.quantidade == 100

def test_persistir_e_listar_movimentacoes(db_session: Session, setup_dados) -> None:
    tenant, loja, produto = setup_dados
    db_session.info["tenant_id"] = tenant.id
    
    repo_mov = RepositorioEstoqueMovimentacaoSQLAlchemy(db_session)
    
    mov1 = EstoqueMovimentacao(
        loja_id=loja.id,
        produto_id=produto.id,
        tipo="ENTRADA",
        quantidade=10,
        motivo="Compra",
        tenant_id=tenant.id,
        data_movimentacao=datetime.now()
    )
    
    mov2 = EstoqueMovimentacao(
        loja_id=loja.id,
        produto_id=produto.id,
        tipo="SAIDA",
        quantidade=2,
        motivo="Venda",
        tenant_id=tenant.id,
        data_movimentacao=datetime.now()
    )
    
    repo_mov.salvar(mov1)
    repo_mov.salvar(mov2)
    db_session.commit()
    
    # Listar por loja e produto
    movs = repo_mov.listar_por_loja_e_produto(loja.id, produto.id, tenant.id)
    assert len(movs) == 2
    assert movs[0].tipo == "ENTRADA"
    assert movs[1].tipo == "SAIDA"
    
    # Listar todas
    todas = repo_mov.listar_todas(tenant.id)
    assert len(todas) == 2

def test_isolamento_tenant_estoque(db_session: Session, setup_dados) -> None:
    tenant_a, loja_a, produto_a = setup_dados
    
    # Criar tenant B e seus dados
    db_session.info["ignore_tenant_filter"] = True
    repo_tenant = RepositorioTenantSQLAlchemy(db_session)
    repo_loja = RepositorioLojaSQLAlchemy(db_session)
    repo_produto = RepositorioProdutoSQLAlchemy(db_session)
    repo_saldo = RepositorioEstoqueSaldoSQLAlchemy(db_session)
    
    tenant_b = repo_tenant.salvar(Tenant(
        nome_fantasia="Lojas do Teste B",
        razao_social="Lojas do Teste B Ltda",
        cnpj="96.453.427/0001-14"
    ))
    loja_b = repo_loja.salvar(Loja(
        nome="Filial Sul",
        cnpj="44.997.002/0001-72",
        endereco="Av Sul, 100",
        tenant_id=tenant_b.id
    ))
    produto_b = repo_produto.salvar(Produto(
        nome="Mesa de Escritorio",
        sku="MESA-ESC-02",
        preco_custo=200.0,
        preco_venda=350.0,
        markup=0.75,
        tenant_id=tenant_b.id
    ))
    
    # Salvar saldo para Tenant A e Tenant B
    repo_saldo.salvar(EstoqueSaldo(loja_id=loja_a.id, produto_id=produto_a.id, quantidade=10, tenant_id=tenant_a.id))
    repo_saldo.salvar(EstoqueSaldo(loja_id=loja_b.id, produto_id=produto_b.id, quantidade=20, tenant_id=tenant_b.id))
    db_session.commit()
    
    # Desativa bypass
    db_session.info["ignore_tenant_filter"] = False
    
    # Testar busca com tenant A ativo
    db_session.info["tenant_id"] = tenant_a.id
    saldos_a = repo_saldo.listar_todos(tenant_a.id)
    assert len(saldos_a) == 1
    assert saldos_a[0].quantidade == 10
    
    # Testar busca com tenant B ativo
    db_session.info["tenant_id"] = tenant_b.id
    saldos_b = repo_saldo.listar_todos(tenant_b.id)
    assert len(saldos_b) == 1
    assert saldos_b[0].quantidade == 20
