import pytest
from uuid import uuid4
from src.domain.entities.tenant import Tenant
from src.domain.entities.usuario import Usuario
from src.domain.entities.loja import Loja

def test_criar_tenant_valido():
    """
    Garante que um Tenant com dados corretos seja instanciado com sucesso.
    """
    tenant = Tenant(
        nome_fantasia="Lojas Girardi",
        razao_social="Girardi e Cia Ltda",
        cnpj="12.345.678/0001-95"
    )
    assert tenant.nome_fantasia == "Lojas Girardi"
    assert tenant.razao_social == "Girardi e Cia Ltda"
    # O CNPJ deve ser limpo e conter apenas dígitos
    assert tenant.cnpj == "12345678000195"
    assert len(tenant.cnpj) == 14
    assert tenant.id is not None

def test_criar_tenant_cnpj_invalido():
    """
    Garante que criar um Tenant com CNPJ inválido matematicamente ou incorreto levante ValueError.
    """
    with pytest.raises(ValueError, match="CNPJ inválido"):
        Tenant(
            nome_fantasia="Lojas Girardi",
            razao_social="Girardi e Cia Ltda",
            cnpj="12345" # Inválido por tamanho
        )
        
    with pytest.raises(ValueError, match="CNPJ inválido"):
        Tenant(
            nome_fantasia="Lojas Girardi",
            razao_social="Girardi e Cia Ltda",
            cnpj="11111111111111" # Inválido matematicamente (dígitos idênticos)
        )

def test_criar_tenant_nome_vazio():
    """
    Garante que criar um Tenant com nome fantasia vazio levante ValueError.
    """
    with pytest.raises(ValueError, match="O nome fantasia deve ser uma string não vazia"):
        Tenant(
            nome_fantasia="   ",
            razao_social="Girardi e Cia Ltda",
            cnpj="12.345.678/0001-95"
        )

def test_criar_usuario_valido():
    """
    Garante que um Usuario com dados válidos seja instanciado com sucesso.
    """
    tenant_id = uuid4()
    usuario = Usuario(
        nome="Jonathas Girardi",
        email="Jonathas@Email.Com  ",  # Será normalizado
        senha_hash="$2b$12$Kj9x...",
        role="DONO",
        tenant_id=tenant_id
    )
    assert usuario.nome == "Jonathas Girardi"
    assert usuario.email == "jonathas@email.com"  # Normalizado (lower e strip)
    assert usuario.role == "DONO"
    assert usuario.tenant_id == tenant_id
    assert usuario.id is not None
    assert usuario.loja_atribuida_id is None

def test_criar_usuario_email_invalido():
    """
    Garante que criar um Usuario com e-mail inválido levante ValueError.
    """
    with pytest.raises(ValueError, match="formato do e-mail .* é inválido"):
        Usuario(
            nome="Jonathas Girardi",
            email="email_invalido",
            senha_hash="$2b$12$Kj9x...",
            role="DONO",
            tenant_id=uuid4()
        )
        
    with pytest.raises(ValueError, match="formato do e-mail .* é inválido"):
        Usuario(
            nome="Jonathas Girardi",
            email="email@dominio..com", # Ponto duplo inválido
            senha_hash="$2b$12$Kj9x...",
            role="DONO",
            tenant_id=uuid4()
        )

def test_criar_usuario_role_invalida():
    """
    Garante que criar um Usuario com perfil (role) não listado levante ValueError.
    """
    with pytest.raises(ValueError, match="Perfil .* inválido"):
        Usuario(
            nome="Jonathas Girardi",
            email="jonathas@email.com",
            senha_hash="$2b$12$Kj9x...",
            role="GERENTE_LOJA", # Inválida, deve ser GERENTE ou DONO ou ADMIN_SAAS
            tenant_id=uuid4()
        )

def test_criar_usuario_gerente_sem_loja():
    """
    Garante que criar um GERENTE sem associar loja levante ValueError.
    """
    with pytest.raises(ValueError, match="perfil de GERENTE devem estar associados a uma loja"):
        Usuario(
            nome="Gerente Silva",
            email="gerente@email.com",
            senha_hash="$2b$12$Kj9x...",
            role="GERENTE",
            tenant_id=uuid4(),
            loja_atribuida_id=None
        )

def test_criar_usuario_dono_com_loja():
    """
    Garante que criar um DONO associado a uma loja específica levante ValueError.
    """
    with pytest.raises(ValueError, match="não devem ter uma loja específica atribuída"):
        Usuario(
            nome="Dono Carlos",
            email="dono@email.com",
            senha_hash="$2b$12$Kj9x...",
            role="DONO",
            tenant_id=uuid4(),
            loja_atribuida_id=uuid4()  # DONO deve gerenciar o tenant todo, sem loja específica
        )

def test_criar_loja_valida():
    """
    Garante que uma Loja com dados corretos seja instanciada com sucesso.
    """
    tenant_id = uuid4()
    loja = Loja(
        nome="Filial Centro",
        cnpj="12.345.678/0001-95",
        endereco="Av. Central, 100",
        tenant_id=tenant_id
    )
    assert loja.nome == "Filial Centro"
    assert loja.cnpj == "12345678000195"
    assert loja.endereco == "Av. Central, 100"
    assert loja.tenant_id == tenant_id
    assert loja.id is not None
    assert loja.ativo is True

def test_criar_loja_cnpj_invalido():
    """
    Garante que criar uma Loja com CNPJ inválido levante ValueError.
    """
    with pytest.raises(ValueError, match="CNPJ inválido"):
        Loja(
            nome="Filial Centro",
            cnpj="123",
            endereco="Av. Central, 100",
            tenant_id=uuid4()
        )

def test_criar_loja_nome_vazio():
    """
    Garante que criar uma Loja com nome vazio ou nulo levante ValueError.
    """
    with pytest.raises(ValueError, match="O nome da loja deve ser uma string não vazia"):
        Loja(
            nome="   ",
            cnpj="12.345.678/0001-95",
            endereco="Av. Central, 100",
            tenant_id=uuid4()
        )

def test_criar_loja_endereco_vazio():
    """
    Garante que criar uma Loja com endereço vazio levante ValueError.
    """
    with pytest.raises(ValueError, match="O endereço deve ser uma string não vazia"):
        Loja(
            nome="Filial Centro",
            cnpj="12.345.678/0001-95",
            endereco="  ",
            tenant_id=uuid4()
        )


