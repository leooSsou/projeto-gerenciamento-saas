from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from src.infrastructure.database.session import get_db
from src.infrastructure.web.dependencies import get_current_user
from src.domain.entities.usuario import Usuario
from src.infrastructure.database.repositorios_concrete import RepositorioProdutoSQLAlchemy
from src.use_cases.catalogo.gerenciar_produto import (
    CriarProduto,
    CriarProdutoInput,
    ObterProduto,
    ListarProdutos,
    AtualizarProduto,
    AtualizarProdutoInput,
)
from src.infrastructure.web.schemas import (
    ProdutoCreateRequest,
    ProdutoUpdateRequest,
    ProdutoResponse,
)
from src.domain.exceptions.business import (
    ProdutoNaoEncontradoException,
    SkuProdutoEmUsoException,
)

router = APIRouter(prefix="/produtos", tags=["Produtos"])

@router.post("/", response_model=ProdutoResponse, status_code=status.HTTP_201_CREATED)
def criar_produto(
    request: ProdutoCreateRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
) -> ProdutoResponse:
    """
    Cadastra um novo Produto vinculado ao Tenant do usuário logado.
    """
    repo = RepositorioProdutoSQLAlchemy(db)
    use_case = CriarProduto(repo)
    
    input_data = CriarProdutoInput(
        nome=request.nome,
        sku=request.sku,
        preco_custo=request.preco_custo,
        preco_venda=request.preco_venda,
        markup=request.markup,
        tenant_id=current_user.tenant_id
    )
    
    try:
        output = use_case.executar(input_data)
        return ProdutoResponse.model_validate(output.produto)
    except SkuProdutoEmUsoException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )


@router.get("/", response_model=List[ProdutoResponse])
def listar_produtos(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
) -> List[ProdutoResponse]:
    """
    Retorna a lista de produtos cadastrados para o Tenant ativo.
    """
    repo = RepositorioProdutoSQLAlchemy(db)
    use_case = ListarProdutos(repo)
    
    output = use_case.executar(tenant_id=current_user.tenant_id)
    return [ProdutoResponse.model_validate(p) for p in output.produtos]


@router.get("/{produto_id}", response_model=ProdutoResponse)
def obter_produto(
    produto_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
) -> ProdutoResponse:
    """
    Busca um produto específico pelo ID respeitando o isolamento do Tenant.
    """
    repo = RepositorioProdutoSQLAlchemy(db)
    use_case = ObterProduto(repo)
    
    try:
        output = use_case.executar(produto_id=produto_id, tenant_id=current_user.tenant_id)
        return ProdutoResponse.model_validate(output.produto)
    except ProdutoNaoEncontradoException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.put("/{produto_id}", response_model=ProdutoResponse)
def atualizar_produto(
    produto_id: UUID,
    request: ProdutoUpdateRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
) -> ProdutoResponse:
    """
    Atualiza dados de um produto existente (SKU e Tenant imutáveis).
    """
    repo = RepositorioProdutoSQLAlchemy(db)
    use_case = AtualizarProduto(repo)
    
    input_data = AtualizarProdutoInput(
        id=produto_id,
        nome=request.nome,
        preco_custo=request.preco_custo,
        preco_venda=request.preco_venda,
        markup=request.markup,
        ativo=request.ativo,
        tenant_id=current_user.tenant_id
    )
    
    try:
        output = use_case.executar(input_data)
        return ProdutoResponse.model_validate(output.produto)
    except ProdutoNaoEncontradoException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
