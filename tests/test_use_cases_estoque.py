import pytest
from uuid import uuid4
from datetime import datetime
from sqlalchemy.orm import Session

from src.domain.entities.tenant import Tenant
from src.domain.entities.loja import Loja
from src.domain.entities.produto import Produto
from src.domain.entities.estoque_saldo import EstoqueSaldo
from src.domain.entities.estoque_movimentacao import EstoqueMovimentacao
from src.domain.exceptions.business import (
    LojaNaoEncontradaException,
    ProdutoNaoEncontradoException,
    EstoqueInsuficienteException,
)
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

@pytest.fixture
def setup_dados_uc(db_session: Session):
    """
    Fixture para criar tenant, loja e produto no banco de dados.
    """
    db_session.info["ignore_tenant_filter"] = True
    
    repo_tenant = RepositorioTenantSQLAlchemy(db_session)
    repo_loja = RepositorioLojaSQLAlchemy(db_session)
    repo_produto = RepositorioProdutoSQLAlchemy(db_session)
    
    tenant = repo_tenant.salvar(Tenant(
        nome_fantasia="Lojas do Teste UC",
        razao_social="Lojas do Teste UC Ltda",
        cnpj="26.762.981/0001-06"
    ))
    
    loja = repo_loja.salvar(Loja(
        nome="Filial Norte UC",
        cnpj="02.188.445/0001-72",
        endereco="Av Norte, 100",
        tenant_id=tenant.id
    ))
    
    produto = repo_produto.salvar(Produto(
        nome="Notebook Gamer UC",
        sku="NOTE-GAME-UC-01",
        preco_custo=3000.0,
        preco_venda=4500.0,
        markup=0.5,
        tenant_id=tenant.id
    ))
    
    db_session.commit()
    db_session.info["ignore_tenant_filter"] = False
    
    return tenant, loja, produto

def test_registrar_entrada_estoque_novo(db_session: Session, setup_dados_uc) -> None:
    tenant, loja, produto = setup_dados_uc
    db_session.info["tenant_id"] = tenant.id
    
    saldo_repo = RepositorioEstoqueSaldoSQLAlchemy(db_session)
    movimentacao_repo = RepositorioEstoqueMovimentacaoSQLAlchemy(db_session)
    loja_repo = RepositorioLojaSQLAlchemy(db_session)
    produto_repo = RepositorioProdutoSQLAlchemy(db_session)
    
    use_case = RegistrarMovimentacaoEstoque(saldo_repo, movimentacao_repo, loja_repo, produto_repo)
    
    # 1. Registrar Entrada (sem saldo anterior)
    input_data = RegistrarMovimentacaoEstoqueInput(
        loja_id=loja.id,
        produto_id=produto.id,
        tipo="ENTRADA",
        quantidade=10,
        motivo="Compra inicial",
        tenant_id=tenant.id
    )
    
    output = use_case.executar(input_data)
    db_session.commit()
    
    assert output.saldo.quantidade == 10
    assert output.movimentacao.quantidade == 10
    assert output.movimentacao.tipo == "ENTRADA"
    
    # Verificar no banco
    saldo_banco = saldo_repo.obter_por_loja_e_produto(loja.id, produto.id, tenant.id)
    assert saldo_banco.quantidade == 10

def test_registrar_entrada_estoque_existente(db_session: Session, setup_dados_uc) -> None:
    tenant, loja, produto = setup_dados_uc
    db_session.info["tenant_id"] = tenant.id
    
    saldo_repo = RepositorioEstoqueSaldoSQLAlchemy(db_session)
    movimentacao_repo = RepositorioEstoqueMovimentacaoSQLAlchemy(db_session)
    loja_repo = RepositorioLojaSQLAlchemy(db_session)
    produto_repo = RepositorioProdutoSQLAlchemy(db_session)
    
    use_case = RegistrarMovimentacaoEstoque(saldo_repo, movimentacao_repo, loja_repo, produto_repo)
    
    # Criar saldo inicial de 10
    saldo_repo.salvar(EstoqueSaldo(loja_id=loja.id, produto_id=produto.id, quantidade=10, tenant_id=tenant.id))
    db_session.commit()
    
    input_data = RegistrarMovimentacaoEstoqueInput(
        loja_id=loja.id,
        produto_id=produto.id,
        tipo="ENTRADA",
        quantidade=5,
        motivo="Ajuste entrada",
        tenant_id=tenant.id
    )
    
    output = use_case.executar(input_data)
    db_session.commit()
    
    assert output.saldo.quantidade == 15
    assert output.movimentacao.quantidade == 5

def test_registrar_saida_estoque_suficiente(db_session: Session, setup_dados_uc) -> None:
    tenant, loja, produto = setup_dados_uc
    db_session.info["tenant_id"] = tenant.id
    
    saldo_repo = RepositorioEstoqueSaldoSQLAlchemy(db_session)
    movimentacao_repo = RepositorioEstoqueMovimentacaoSQLAlchemy(db_session)
    loja_repo = RepositorioLojaSQLAlchemy(db_session)
    produto_repo = RepositorioProdutoSQLAlchemy(db_session)
    
    use_case = RegistrarMovimentacaoEstoque(saldo_repo, movimentacao_repo, loja_repo, produto_repo)
    
    # Criar saldo inicial de 10
    saldo_repo.salvar(EstoqueSaldo(loja_id=loja.id, produto_id=produto.id, quantidade=10, tenant_id=tenant.id))
    db_session.commit()
    
    input_data = RegistrarMovimentacaoEstoqueInput(
        loja_id=loja.id,
        produto_id=produto.id,
        tipo="SAIDA",
        quantidade=3,
        motivo="Venda balcao",
        tenant_id=tenant.id
    )
    
    output = use_case.executar(input_data)
    db_session.commit()
    
    assert output.saldo.quantidade == 7
    assert output.movimentacao.quantidade == 3
    assert output.movimentacao.tipo == "SAIDA"

def test_registrar_saida_estoque_insuficiente(db_session: Session, setup_dados_uc) -> None:
    tenant, loja, produto = setup_dados_uc
    db_session.info["tenant_id"] = tenant.id
    
    saldo_repo = RepositorioEstoqueSaldoSQLAlchemy(db_session)
    movimentacao_repo = RepositorioEstoqueMovimentacaoSQLAlchemy(db_session)
    loja_repo = RepositorioLojaSQLAlchemy(db_session)
    produto_repo = RepositorioProdutoSQLAlchemy(db_session)
    
    use_case = RegistrarMovimentacaoEstoque(saldo_repo, movimentacao_repo, loja_repo, produto_repo)
    
    # Criar saldo inicial de 5
    saldo_repo.salvar(EstoqueSaldo(loja_id=loja.id, produto_id=produto.id, quantidade=5, tenant_id=tenant.id))
    db_session.commit()
    
    input_data = RegistrarMovimentacaoEstoqueInput(
        loja_id=loja.id,
        produto_id=produto.id,
        tipo="SAIDA",
        quantidade=10,  # Insuficiente
        motivo="Venda grande",
        tenant_id=tenant.id
    )
    
    with pytest.raises(EstoqueInsuficienteException, match="Estoque insuficiente"):
        use_case.executar(input_data)

def test_seguranca_bola_loja_inexistente(db_session: Session, setup_dados_uc) -> None:
    tenant, loja, produto = setup_dados_uc
    db_session.info["tenant_id"] = tenant.id
    
    saldo_repo = RepositorioEstoqueSaldoSQLAlchemy(db_session)
    movimentacao_repo = RepositorioEstoqueMovimentacaoSQLAlchemy(db_session)
    loja_repo = RepositorioLojaSQLAlchemy(db_session)
    produto_repo = RepositorioProdutoSQLAlchemy(db_session)
    
    use_case = RegistrarMovimentacaoEstoque(saldo_repo, movimentacao_repo, loja_repo, produto_repo)
    
    # Tenta usar loja_id aleatório (não pertence ao tenant)
    loja_invalida_id = uuid4()
    input_data = RegistrarMovimentacaoEstoqueInput(
        loja_id=loja_invalida_id,
        produto_id=produto.id,
        tipo="ENTRADA",
        quantidade=10,
        motivo="Entrada teste",
        tenant_id=tenant.id
    )
    
    with pytest.raises(LojaNaoEncontradaException):
        use_case.executar(input_data)

def test_seguranca_bola_produto_inexistente(db_session: Session, setup_dados_uc) -> None:
    tenant, loja, produto = setup_dados_uc
    db_session.info["tenant_id"] = tenant.id
    
    saldo_repo = RepositorioEstoqueSaldoSQLAlchemy(db_session)
    movimentacao_repo = RepositorioEstoqueMovimentacaoSQLAlchemy(db_session)
    loja_repo = RepositorioLojaSQLAlchemy(db_session)
    produto_repo = RepositorioProdutoSQLAlchemy(db_session)
    
    use_case = RegistrarMovimentacaoEstoque(saldo_repo, movimentacao_repo, loja_repo, produto_repo)
    
    # Tenta usar produto_id aleatório (não pertence ao tenant)
    produto_invalido_id = uuid4()
    input_data = RegistrarMovimentacaoEstoqueInput(
        loja_id=loja.id,
        produto_id=produto_invalido_id,
        tipo="ENTRADA",
        quantidade=10,
        motivo="Entrada teste",
        tenant_id=tenant.id
    )
    
    with pytest.raises(ProdutoNaoEncontradoException):
        use_case.executar(input_data)
