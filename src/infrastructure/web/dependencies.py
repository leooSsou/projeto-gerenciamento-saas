from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from uuid import UUID

from src.infrastructure.database.session import get_db
from src.infrastructure.security.jwt_handler import decodificar_token_acesso
from src.infrastructure.database.repositories_adapters import SQLAlchemyUsuarioRepository
from src.domain.entities.usuario import Usuario

# Configura o fluxo de token Bearer do OAuth2 (aponta para a rota de login)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Usuario:
    """
    Dependência injetável do FastAPI para obter o usuário autenticado atual.
    
    1. Decodifica e valida o token JWT de acesso.
    2. Configura o tenant_id ativo diretamente na sessão do SQLAlchemy para isolamento global.
    3. Recupera o usuário no repositório de banco e o retorna como entidade pura de domínio.
    """
    try:
        payload = decodificar_token_acesso(token)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

    sub = payload.get("sub")
    tenant_id_str = payload.get("tenant_id")
    
    if not sub or not tenant_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido: identificador de usuário ou tenant ausentes.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        tenant_id = UUID(tenant_id_str)
        usuario_id = UUID(sub)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido: formato de identificadores incorreto.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Configura o tenant_id ativo na sessão atual para a query e para futuras operações
    db.info["tenant_id"] = tenant_id

    usuario_repo = SQLAlchemyUsuarioRepository(db)
    usuario = usuario_repo.obter_por_id(usuario_id)

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado ou inativo.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return usuario
