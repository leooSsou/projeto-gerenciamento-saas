import pytest
from datetime import timedelta, timezone, datetime
from jose import jwt
from src.infrastructure.security.password import gerar_hash_senha, verificar_senha
from src.infrastructure.security.jwt_handler import (
    criar_token_acesso,
    decodificar_token_acesso,
    SECRET_KEY,
    ALGORITHM
)

def test_hashing_senhas():
    """
    Testa se o hash de senha funciona de forma correta e segura.
    """
    senha = "minha_senha_secreta"
    hash1 = gerar_hash_senha(senha)
    hash2 = gerar_hash_senha(senha)
    
    # Bcrypt deve gerar hashes diferentes para a mesma senha (devido ao salt aleatório)
    assert hash1 != hash2
    
    # A verificação deve passar para a senha correta e falhar para senhas incorretas
    assert verificar_senha(senha, hash1) is True
    assert verificar_senha(senha, hash2) is True
    assert verificar_senha("outra_senha", hash1) is False

def test_criacao_e_decodificacao_jwt_sucesso():
    """
    Testa se a geração do token JWT codifica e decodifica as claims obrigatórias corretamente.
    """
    sub = "user@test.com"
    tenant_id = "f81d4fae-7dec-11d0-a765-00a0c91e6bf6"
    role = "DONO"
    
    token = criar_token_acesso(sub=sub, tenant_id=tenant_id, role=role)
    payload = decodificar_token_acesso(token)
    
    assert payload["sub"] == sub
    assert payload["tenant_id"] == tenant_id
    assert payload["role"] == role
    assert "exp" in payload
    assert "iat" in payload

def test_jwt_token_expirado():
    """
    Testa se o decodificador rejeita tokens com tempo de expiração no passado.
    """
    sub = "expired@test.com"
    tenant_id = "f81d4fae-7dec-11d0-a765-00a0c91e6bf6"
    role = "GERENTE"
    
    # Cria token expirado definindo uma expiração negativa
    token = criar_token_acesso(
        sub=sub,
        tenant_id=tenant_id,
        role=role,
        tempo_expiracao=timedelta(seconds=-10)
    )
    
    with pytest.raises(ValueError) as exc_info:
        decodificar_token_acesso(token)
    
    assert "expirou" in str(exc_info.value)

def test_jwt_token_invalido():
    """
    Testa se o decodificador rejeita tokens inválidos, mal formatados ou alterados.
    """
    token_invalido = "header.payload.signature_errada"
    
    with pytest.raises(ValueError) as exc_info:
        decodificar_token_acesso(token_invalido)
        
    assert "invalid" in str(exc_info.value).lower() or "token inválido" in str(exc_info.value).lower()

def test_jwt_sem_claims_obrigatorias():
    """
    Testa se o decodificador rejeita tokens válidos do ponto de vista do JWT,
    mas que não possuem as claims obrigatórias do SaaS (tenant_id e role).
    """
    # Cria um token manual sem as claims exigidas pelo nosso jwt_handler
    payload_incompleto = {
        "sub": "test@test.com",
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=10)
    }
    
    token_incompleto = jwt.encode(payload_incompleto, SECRET_KEY, algorithm=ALGORITHM)
    
    with pytest.raises(ValueError) as exc_info:
        decodificar_token_acesso(token_incompleto)
        
    assert "claim obrigatória" in str(exc_info.value)
