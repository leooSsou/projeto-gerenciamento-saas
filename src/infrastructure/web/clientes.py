from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from src.infrastructure.database.session import get_db
from src.infrastructure.web.dependencies import get_current_user
from src.domain.entities.usuario import Usuario
from src.infrastructure.database.repositorios_concrete import RepositorioClienteSQLAlchemy
from src.use_cases.catalogo.gerenciar_cliente import (
    CriarCliente,
    CriarClienteInput,
    ObterCliente,
    ListarClientes,
    AtualizarCliente,
    AtualizarClienteInput,
)
from src.infrastructure.web.schemas import (
    ClienteCreateRequest,
    ClienteUpdateRequest,
    ClienteResponse,
)
from src.domain.exceptions.business import (
    ClienteNaoEncontradoException,
    DocumentoClienteEmUsoException,
)

router = APIRouter(prefix="/clientes", tags=["Clientes"])

@router.post("/", response_model=ClienteResponse, status_code=status.HTTP_201_CREATED)
def criar_cliente(
    request: ClienteCreateRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
) -> ClienteResponse:
    """
    Cadastra um novo Cliente vinculado ao Tenant do usuário logado.
    """
    repo = RepositorioClienteSQLAlchemy(db)
    use_case = CriarCliente(repo)
    
    input_data = CriarClienteInput(
        nome=request.nome,
        email=request.email,
        documento=request.documento,
        tenant_id=current_user.tenant_id
    )
    
    try:
        output = use_case.executar(input_data)
        return ClienteResponse.model_validate(output.cliente)
    except DocumentoClienteEmUsoException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )


@router.get("/", response_model=List[ClienteResponse])
def listar_clientes(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
) -> List[ClienteResponse]:
    """
    Retorna a lista de clientes cadastrados para o Tenant ativo.
    """
    repo = RepositorioClienteSQLAlchemy(db)
    use_case = ListarClientes(repo)
    
    output = use_case.executar(tenant_id=current_user.tenant_id)
    return [ClienteResponse.model_validate(c) for c in output.clientes]


@router.get("/{cliente_id}", response_model=ClienteResponse)
def obter_cliente(
    cliente_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
) -> ClienteResponse:
    """
    Busca um cliente específico pelo ID respeitando o isolamento do Tenant.
    """
    repo = RepositorioClienteSQLAlchemy(db)
    use_case = ObterCliente(repo)
    
    try:
        output = use_case.executar(cliente_id=cliente_id, tenant_id=current_user.tenant_id)
        return ClienteResponse.model_validate(output.cliente)
    except ClienteNaoEncontradoException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.put("/{cliente_id}", response_model=ClienteResponse)
def atualizar_cliente(
    cliente_id: UUID,
    request: ClienteUpdateRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
) -> ClienteResponse:
    """
    Atualiza dados de um cliente existente (documento e tenant imutáveis).
    """
    repo = RepositorioClienteSQLAlchemy(db)
    use_case = AtualizarCliente(repo)
    
    input_data = AtualizarClienteInput(
        id=cliente_id,
        nome=request.nome,
        email=request.email,
        ativo=request.ativo,
        tenant_id=current_user.tenant_id
    )
    
    try:
        output = use_case.executar(input_data)
        return ClienteResponse.model_validate(output.cliente)
    except ClienteNaoEncontradoException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
