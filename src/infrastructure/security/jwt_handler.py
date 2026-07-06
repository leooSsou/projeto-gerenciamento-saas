import os
from datetime import datetime, timedelta, timezone
from typing import Any
from jose import jwt, JWTError
from jose.exceptions import ExpiredSignatureError

# Carrega variáveis de ambiente ou utiliza fallbacks para desenvolvimento
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "saas_super_secret_dev_key_12345!")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

def criar_token_acesso(
    sub: str,
    tenant_id: str,
    role: str,
    tempo_expiracao: timedelta | None = None
) -> str:
    """
    Gera um token de acesso JWT tipado contendo sub, tenant_id e role.
    
    Args:
        sub (str): Identificação única do usuário (geralmente e-mail ou UUID).
        tenant_id (str): Identificador do inquilino (tenant) associado.
        role (str): Papel/Função de permissão do usuário.
        tempo_expiracao (timedelta, optional): Tempo customizado para expiração.
        
    Returns:
        str: Token JWT codificado.
    """
    agora = datetime.now(timezone.utc)
    
    if tempo_expiracao:
        expiracao = agora + tempo_expiracao
    else:
        expiracao = agora + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
    payload = {
        "sub": sub,
        "tenant_id": tenant_id,
        "role": role,
        "iat": agora,
        "exp": expiracao
    }
    
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decodificar_token_acesso(token: str) -> dict[str, Any]:
    """
    Decodifica e valida o token JWT de acesso.
    
    Args:
        token (str): O token JWT recebido no header de autorização.
        
    Returns:
        dict[str, Any]: O payload decodificado contendo as claims.
        
    Raises:
        ValueError: Caso o token seja inválido, expirado ou esteja com formato incorreto.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Validação de claims obrigatórias para o SaaS
        if "tenant_id" not in payload:
            raise ValueError("O token não possui a claim obrigatória 'tenant_id'.")
        if "role" not in payload:
            raise ValueError("O token não possui a claim obrigatória 'role'.")
            
        return payload
    except ExpiredSignatureError:
        raise ValueError("O token de acesso expirou.")
    except JWTError as e:
        raise ValueError(f"Token inválido: {str(e)}")
