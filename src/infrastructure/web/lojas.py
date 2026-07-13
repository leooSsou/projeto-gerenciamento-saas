from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from src.infrastructure.database.session import get_db
from src.infrastructure.web.dependencies import get_current_user
from src.domain.entities.usuario import Usuario
from src.infrastructure.database.repositorios_concrete import RepositorioLojaSQLAlchemy
from src.use_cases.catalogo.gerenciar_loja import (
    CriarLoja,
    CriarLojaInput,
    ObterLoja,
    ListarLojas,
    AtualizarLoja,
    AtualizarLojaInput,
)
from src.infrastructure.web.schemas import (
    LojaCreateRequest,
    LojaUpdateRequest,
    LojaResponse,
)
from src.domain.exceptions.business import (
    LojaNaoEncontradaException,
    CnpjLojaEmUsoException,
)

router = APIRouter(prefix="/lojas", tags=["Lojas"])

@router.post("/", response_model=LojaResponse, status_code=status.HTTP_201_CREATED)
def criar_loja(
    request: LojaCreateRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
) -> LojaResponse:
    """
    Cadastra uma nova filial (Loja) vinculada ao Tenant do usuário autenticado.
    """
    repo = RepositorioLojaSQLAlchemy(db)
    use_case = CriarLoja(repo)
    
    input_data = CriarLojaInput(
        nome=request.nome,
        cnpj=request.cnpj,
        endereco=request.endereco,
        tenant_id=current_user.tenant_id
    )
    
    try:
        output = use_case.executar(input_data)
        return LojaResponse.model_validate(output.loja)
    except CnpjLojaEmUsoException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )


@router.get("/", response_model=List[LojaResponse])
def listar_lojas(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
) -> List[LojaResponse]:
    """
    Retorna a lista de todas as lojas vinculadas ao Tenant do usuário autenticado.
    """
    repo = RepositorioLojaSQLAlchemy(db)
    use_case = ListarLojas(repo)
    
    output = use_case.executar(tenant_id=current_user.tenant_id)
    return [LojaResponse.model_validate(loja) for loja in output.lojas]


@router.get("/{loja_id}", response_model=LojaResponse)
def obter_loja(
    loja_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
) -> LojaResponse:
    """
    Busca os detalhes de uma loja específica pelo ID.
    Garante o escopo de segurança do Tenant.
    """
    repo = RepositorioLojaSQLAlchemy(db)
    use_case = ObterLoja(repo)
    
    try:
        output = use_case.executar(loja_id=loja_id, tenant_id=current_user.tenant_id)
        return LojaResponse.model_validate(output.loja)
    except LojaNaoEncontradaException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.put("/{loja_id}", response_model=LojaResponse)
def atualizar_loja(
    loja_id: UUID,
    request: LojaUpdateRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
) -> LojaResponse:
    """
    Atualiza os dados de uma loja existente.
    O CNPJ e o Tenant permanecem imutáveis.
    """
    repo = RepositorioLojaSQLAlchemy(db)
    use_case = AtualizarLoja(repo)
    
    input_data = AtualizarLojaInput(
        id=loja_id,
        nome=request.nome,
        endereco=request.endereco,
        ativo=request.ativo,
        tenant_id=current_user.tenant_id
    )
    
    try:
        output = use_case.executar(input_data)
        return LojaResponse.model_validate(output.loja)
    except LojaNaoEncontradaException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
