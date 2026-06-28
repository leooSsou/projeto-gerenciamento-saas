import pytest
from uuid import uuid4
from src.domain.entities.tenant import Tenant
from src.domain.entities.usuario import Usuario

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
    Garante que criar um Tenant com CNPJ com tamanho incorreto levante ValueError.
    """
    with pytest.raises(ValueError, match="O CNPJ deve conter exatamente 14 dígitos"):
        Tenant(
            nome_fantasia="Lojas Girardi",
            razao_social="Girardi e Cia Ltda",
            cnpj="12345" # Inválido
        )

def test_criar_tenant_nome_vazio():
    """
    Garante que criar um Tenant com nome fantasia vazio levante ValueError.
    """
    with pytest.raises(ValueError, match="O nome fantasia não pode ser vazio"):
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
        email="jonathas@email.com",
        senha_hash="$2b$12$Kj9x...",
        role="DONO",
        tenant_id=tenant_id
    )
    assert usuario.nome == "Jonathas Girardi"
    assert usuario.email == "jonathas@email.com"
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
