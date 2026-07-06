from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.infrastructure.database.session import get_db
from src.infrastructure.security.password import BcryptServicoCriptografia
from src.infrastructure.security.jwt_handler import criar_token_acesso
from src.infrastructure.database.repositorios_concrete import (
    RepositorioTenantSQLAlchemy,
    RepositorioUsuarioSQLAlchemy,
)
from src.use_cases.autenticacao.criar_tenant import CriarTenant, CriarTenantInput
from src.use_cases.autenticacao.autenticar_usuario import AutenticarUsuario, AutenticarUsuarioInput
from src.domain.exceptions.business import (
    CnpjEmUsoException,
    EmailEmUsoException,
    CredenciaisInvalidasException,
)
from src.domain.entities.usuario import Usuario
from src.infrastructure.web.schemas import (
    RegisterRequest,
    RegisterResponse,
    LoginRequest,
    LoginResponse,
    UserResponse,
)
from src.infrastructure.web.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Autenticação"])

@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest, db: Session = Depends(get_db)) -> RegisterResponse:
    """
    Registra um novo inquilino (Tenant) e cria o respectivo usuário administrador (DONO).
    """
    try:
        # Ignora o filtro de tenant para permitir o cadastro inicial do tenant e seu primeiro usuário
        db.info["ignore_tenant_filter"] = True

        tenant_repo = RepositorioTenantSQLAlchemy(db)
        usuario_repo = RepositorioUsuarioSQLAlchemy(db)
        servico_cripto = BcryptServicoCriptografia()
        use_case = CriarTenant(tenant_repo, usuario_repo, servico_cripto)

        input_data = CriarTenantInput(
            nome_fantasia=request.nome_fantasia,
            razao_social=request.razao_social,
            cnpj=request.cnpj,
            dono_nome=request.dono_nome,
            dono_email=str(request.dono_email),
            dono_senha_plana=request.dono_senha
        )

        try:
            output = use_case.executar(input_data)
            return RegisterResponse(
                tenant_id=output.tenant.id,
                nome_fantasia=output.tenant.nome_fantasia,
                dono_id=output.usuario.id,
                dono_email=output.usuario.email
            )
        except CnpjEmUsoException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"O CNPJ '{e.cnpj}' já está cadastrado no sistema."
            )
        except EmailEmUsoException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"O e-mail '{e.email}' já está em uso por outro usuário."
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(e)
            )
    finally:
        db.info.pop("ignore_tenant_filter", None)


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    """
    Autentica um usuário e retorna um token de acesso JWT.
    """
    try:
        # Ignora o filtro de tenant durante a autenticação para permitir a busca do usuário pelo e-mail
        db.info["ignore_tenant_filter"] = True

        tenant_repo = RepositorioTenantSQLAlchemy(db)
        usuario_repo = RepositorioUsuarioSQLAlchemy(db)
        servico_cripto = BcryptServicoCriptografia()
        use_case = AutenticarUsuario(usuario_repo, tenant_repo, servico_cripto)

        input_data = AutenticarUsuarioInput(
            email=str(request.email),
            senha_plana=request.senha
        )

        try:
            output = use_case.executar(input_data)
            
            # Gera o token de acesso injetando tenant_id e role obrigatórios
            access_token = criar_token_acesso(
                sub=str(output.usuario.id),
                tenant_id=str(output.usuario.tenant_id),
                role=output.usuario.role
            )
            
            return LoginResponse(access_token=access_token)
        except CredenciaisInvalidasException:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="E-mail ou senha incorretos."
            )
    finally:
        db.info.pop("ignore_tenant_filter", None)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: Usuario = Depends(get_current_user)) -> UserResponse:
    """
    Retorna as informações do usuário autenticado no momento.
    """
    return UserResponse(
        id=current_user.id,
        nome=current_user.nome,
        email=current_user.email,
        role=current_user.role,
        tenant_id=current_user.tenant_id,
        loja_atribuida_id=current_user.loja_atribuida_id
    )
