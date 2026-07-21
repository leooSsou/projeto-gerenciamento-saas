import pytest
from uuid import uuid4
from datetime import datetime

from src.domain.entities.estoque_saldo import EstoqueSaldo
from src.domain.entities.estoque_movimentacao import EstoqueMovimentacao
from src.domain.exceptions.business import EstoqueInsuficienteException

def test_criar_estoque_saldo_valido() -> None:
    loja_id = uuid4()
    produto_id = uuid4()
    tenant_id = uuid4()
    
    saldo = EstoqueSaldo(
        loja_id=loja_id,
        produto_id=produto_id,
        quantidade=10,
        tenant_id=tenant_id
    )
    
    assert saldo.loja_id == loja_id
    assert saldo.produto_id == produto_id
    assert saldo.quantidade == 10
    assert saldo.tenant_id == tenant_id
    assert saldo.id is not None

def test_criar_estoque_saldo_quantidade_zero() -> None:
    saldo = EstoqueSaldo(
        loja_id=uuid4(),
        produto_id=uuid4(),
        quantidade=0,
        tenant_id=uuid4()
    )
    assert saldo.quantidade == 0

def test_criar_estoque_saldo_quantidade_negativa_deve_falhar() -> None:
    with pytest.raises(ValueError, match="A quantidade de estoque deve ser um número inteiro maior ou igual a zero."):
        EstoqueSaldo(
            loja_id=uuid4(),
            produto_id=uuid4(),
            quantidade=-1,
            tenant_id=uuid4()
        )

def test_criar_estoque_saldo_tipos_invalidos_deve_falhar() -> None:
    # loja_id inválido
    with pytest.raises(ValueError, match="O loja_id deve ser um UUID válido."):
        EstoqueSaldo(loja_id="invalido", produto_id=uuid4(), quantidade=10, tenant_id=uuid4())
        
    # produto_id inválido
    with pytest.raises(ValueError, match="O produto_id deve ser um UUID válido."):
        EstoqueSaldo(loja_id=uuid4(), produto_id="invalido", quantidade=10, tenant_id=uuid4())
        
    # quantidade inválida (não int)
    with pytest.raises(ValueError, match="A quantidade de estoque deve ser um número inteiro maior ou igual a zero."):
        EstoqueSaldo(loja_id=uuid4(), produto_id=uuid4(), quantidade="10", tenant_id=uuid4())

    # tenant_id inválido
    with pytest.raises(ValueError, match="O tenant_id deve ser um UUID válido."):
        EstoqueSaldo(loja_id=uuid4(), produto_id=uuid4(), quantidade=10, tenant_id="invalido")

def test_criar_estoque_movimentacao_valida() -> None:
    loja_id = uuid4()
    produto_id = uuid4()
    tenant_id = uuid4()
    data = datetime.now()
    
    mov = EstoqueMovimentacao(
        loja_id=loja_id,
        produto_id=produto_id,
        tipo="ENTRADA",
        quantidade=5,
        motivo="Compra de fornecedor",
        tenant_id=tenant_id,
        data_movimentacao=data
    )
    
    assert mov.loja_id == loja_id
    assert mov.produto_id == produto_id
    assert mov.tipo == "ENTRADA"
    assert mov.quantidade == 5
    assert mov.motivo == "Compra de fornecedor"
    assert mov.tenant_id == tenant_id
    assert mov.data_movimentacao == data

def test_criar_estoque_movimentacao_saida_valida() -> None:
    mov = EstoqueMovimentacao(
        loja_id=uuid4(),
        produto_id=uuid4(),
        tipo="SAIDA",
        quantidade=1,
        motivo="  venda efetuada  ",
        tenant_id=uuid4()
    )
    assert mov.tipo == "SAIDA"
    assert mov.motivo == "venda efetuada"  # Deve fazer strip do motivo

def test_criar_estoque_movimentacao_invalidas_deve_falhar() -> None:
    # Tipo inválido
    with pytest.raises(ValueError, match="O tipo de movimentação deve ser obrigatoriamente 'ENTRADA' ou 'SAIDA'."):
        EstoqueMovimentacao(loja_id=uuid4(), produto_id=uuid4(), tipo="AJUSTE", quantidade=5, motivo="Ajuste", tenant_id=uuid4())
        
    # Quantidade zero ou menor
    with pytest.raises(ValueError, match="A quantidade de movimentação deve ser um número inteiro maior que zero."):
        EstoqueMovimentacao(loja_id=uuid4(), produto_id=uuid4(), tipo="ENTRADA", quantidade=0, motivo="Erro", tenant_id=uuid4())
        
    with pytest.raises(ValueError, match="A quantidade de movimentação deve ser um número inteiro maior que zero."):
        EstoqueMovimentacao(loja_id=uuid4(), produto_id=uuid4(), tipo="ENTRADA", quantidade=-5, motivo="Erro", tenant_id=uuid4())
        
    # Motivo vazio
    with pytest.raises(ValueError, match="O motivo da movimentação deve ser uma string não vazia."):
        EstoqueMovimentacao(loja_id=uuid4(), produto_id=uuid4(), tipo="ENTRADA", quantidade=5, motivo="   ", tenant_id=uuid4())

    # Quantidade acima do limite
    with pytest.raises(ValueError, match="A quantidade de movimentação por operação não pode exceder 1.000.000 unidades."):
        EstoqueMovimentacao(loja_id=uuid4(), produto_id=uuid4(), tipo="ENTRADA", quantidade=1000001, motivo="Abuso", tenant_id=uuid4())

def test_criar_estoque_saldo_quantidade_acima_do_limite_deve_falhar() -> None:
    with pytest.raises(ValueError, match="A quantidade de estoque não pode exceder 1.000.000.000 unidades."):
        EstoqueSaldo(
            loja_id=uuid4(),
            produto_id=uuid4(),
            quantidade=1000000001,
            tenant_id=uuid4()
        )

def test_estoque_insuficiente_exception() -> None:
    prod_id = str(uuid4())
    loja_id = str(uuid4())
    
    exc = EstoqueInsuficienteException(produto_id=prod_id, loja_id=loja_id, disponivel=2, solicitado=5)
    
    assert exc.produto_id == prod_id
    assert exc.loja_id == loja_id
    assert exc.disponivel == 2
    assert exc.solicitado == 5
    assert "Estoque insuficiente" in str(exc)
