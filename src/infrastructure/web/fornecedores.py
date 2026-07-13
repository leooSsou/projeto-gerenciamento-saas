from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from src.infrastructure.database.session import get_db
from src.infrastructure.web.dependencies import get_current_user
from src.domain.entities.usuario import Usuario
from src.infrastructure.database.repositorios_concrete import RepositorioFornecedorSQLAlchemy
from src.use_cases.catalogo.gerenciar_fornecedor import (
    CriarFornecedor,
    CriarFornecedorInput,
    ObterFornecedor,
    ListarFornecedores,
    AtualizarFornecedor,
    AtualizarFornecedorInput,
)
from src.infrastructure.web.schemas import (
    FornecedorCreateRequest,
    FornecedorUpdateRequest,
    FornecedorResponse,
)
from src.domain.exceptions.business import (
    FornecedorNaoEncontradoException,
    CnpjFornecedorEmUsoException,
)

router = APIRouter(prefix="/fornecedores", tags=["Fornecedores"])

@router.post("/", response_model=FornecedorResponse, status_code=status.HTTP_201_CREATED)
def criar_fornecedor(
    request: FornecedorCreateRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
) -> FornecedorResponse:
    """
    Cadastra um novo Fornecedor vinculado ao Tenant do usuário logado.
    """
    repo = RepositorioFornecedorSQLAlchemy(db)
    use_case = CriarFornecedor(repo)
    
    input_data = CriarFornecedorInput(
        nome_fantasia=request.nome_fantasia,
        razao_social=request.razao_social,
        cnpj=request.cnpj,
        tenant_id=current_user.tenant_id
    )
    
    try:
        output = use_case.executar(input_data)
        return FornecedorResponse.model_validate(output.fornecedor)
    except CnpjFornecedorEmUsoException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )


@router.get("/", response_model=List[FornecedorResponse])
def listar_fornecedores(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
) -> List[FornecedorResponse]:
    """
    Retorna a lista de fornecedores cadastrados para o Tenant ativo.
    """
    repo = RepositorioFornecedorSQLAlchemy(db)
    use_case = ListarFornecedores(repo)
    
    output = use_case.executar(tenant_id=current_user.tenant_id)
    return [FornecedorResponse.model_validate(f) for f in output.fornecedores]


@router.get("/{fornecedor_id}", response_model=FornecedorResponse)
def obter_fornecedor(
    fornecedor_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
) -> FornecedorResponse:
    """
    Busca um fornecedor específico pelo ID respeitando o isolamento do Tenant.
    """
    repo = RepositorioFornecedorSQLAlchemy(db)
    use_case = ObterFornecedor(repo)
    
    try:
        output = use_case.executar(fornecedor_id=fornecedor_id, tenant_id=current_user.tenant_id)
        return FornecedorResponse.model_validate(output.fornecedor)
    except FornecedorNaoEncontradoException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.put("/{fornecedor_id}", response_model=FornecedorResponse)
def atualizar_fornecedor(
    fornecedor_id: UUID,
    request: FornecedorUpdateRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
) -> FornecedorResponse:
    """
    Atualiza dados de um fornecedor existente (cnpj e tenant imutáveis).
    """
    repo = RepositorioFornecedorSQLAlchemy(db)
    use_case = AtualizarFornecedor(repo)
    
    input_data = AtualizarFornecedorInput(
        id=fornecedor_id,
        nome_fantasia=request.nome_fantasia,
        razao_social=request.razao_social,
        ativo=request.ativo,
        tenant_id=current_user.tenant_id
    )
    
    try:
        output = use_case.executar(input_data)
        return FornecedorResponse.model_validate(output.fornecedor)
    except FornecedorNaoEncontradoException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
