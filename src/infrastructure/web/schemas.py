from typing import Optional, List

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from uuid import UUID
from datetime import datetime


class RegisterRequest(BaseModel):
    """
    Schema para requisição de criação de Tenant e seu Usuário proprietário inicial.
    """
    nome_fantasia: str = Field(..., min_length=1, max_length=150, description="Nome comercial da rede de lojas.")
    razao_social: str = Field(..., min_length=1, max_length=150, description="Razão social jurídica oficial.")
    cnpj: str = Field(..., min_length=14, max_length=18, description="CNPJ (com ou sem pontuação).")
    dono_nome: str = Field(..., min_length=1, max_length=100, description="Nome completo do dono da conta.")
    dono_email: EmailStr = Field(..., description="E-mail de acesso do dono.")
    dono_senha: str = Field(..., min_length=6, max_length=100, description="Senha de acesso do dono (mínimo 6 caracteres).")

class RegisterResponse(BaseModel):
    """
    Schema para retorno do cadastro realizado com sucesso.
    """
    tenant_id: UUID
    nome_fantasia: str
    dono_id: UUID
    dono_email: str

    model_config = ConfigDict(from_attributes=True)

class LoginRequest(BaseModel):
    """
    Schema para requisição de autenticação de usuário.
    """
    email: EmailStr = Field(..., description="E-mail do usuário.")
    senha: str = Field(..., min_length=1, description="Senha do usuário.")

class LoginResponse(BaseModel):
    """
    Schema para retorno de autenticação bem-sucedida com token JWT.
    """
    access_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    """
    Schema para retorno de dados do usuário autenticado.
    """
    id: UUID
    nome: str
    email: str
    role: str
    tenant_id: UUID
    loja_atribuida_id: UUID | None = None

    model_config = ConfigDict(from_attributes=True)


class LojaCreateRequest(BaseModel):
    """
    Schema para requisição de criação de uma nova Loja.
    """
    nome: str = Field(..., min_length=1, max_length=100, description="Nome da filial/loja.")
    cnpj: str = Field(..., min_length=14, max_length=18, description="CNPJ da filial/loja.")
    endereco: str = Field(..., min_length=1, max_length=255, description="Endereço físico completo.")


class LojaUpdateRequest(BaseModel):
    """
    Schema para requisição de atualização dos dados da Loja.
    """
    nome: str = Field(..., min_length=1, max_length=100, description="Nome da filial/loja.")
    endereco: str = Field(..., min_length=1, max_length=255, description="Endereço físico completo.")
    ativo: bool = Field(..., description="Status de atividade da loja.")


class LojaResponse(BaseModel):
    """
    Schema para retorno das informações de uma Loja.
    """
    id: UUID
    nome: str
    cnpj: str
    endereco: str
    tenant_id: UUID
    ativo: bool

    model_config = ConfigDict(from_attributes=True)


class ProdutoCreateRequest(BaseModel):
    """
    Schema para requisição de criação de um novo Produto.
    """
    nome: str = Field(..., min_length=1, max_length=150, description="Nome do produto.")
    sku: str = Field(..., min_length=1, max_length=50, description="SKU de identificação.")
    preco_custo: float = Field(..., ge=0.0, description="Preço de custo.")
    preco_venda: float = Field(..., ge=0.0, description="Preço de venda.")
    markup: float = Field(..., description="Markup do produto.")
    codigo_barras: Optional[str] = Field(None, max_length=50, description="Código de barras do produto.")
    fornecedor_id: Optional[UUID] = Field(None, description="ID do fornecedor associado.")


class ProdutoUpdateRequest(BaseModel):
    """
    Schema para requisição de atualização dos dados de um Produto.
    """
    nome: str = Field(..., min_length=1, max_length=150, description="Nome do produto.")
    preco_custo: float = Field(..., ge=0.0, description="Preço de custo.")
    preco_venda: float = Field(..., ge=0.0, description="Preço de venda.")
    markup: float = Field(..., description="Markup do produto.")
    codigo_barras: Optional[str] = Field(None, max_length=50, description="Código de barras do produto.")
    fornecedor_id: Optional[UUID] = Field(None, description="ID do fornecedor associado.")
    ativo: bool = Field(..., description="Status de atividade do produto.")


class ProdutoResponse(BaseModel):
    """
    Schema para retorno das informações de um Produto.
    """
    id: UUID
    nome: str
    sku: str
    preco_custo: float
    preco_venda: float
    markup: float
    tenant_id: UUID
    codigo_barras: Optional[str] = None
    fornecedor_id: Optional[UUID] = None
    ativo: bool

    model_config = ConfigDict(from_attributes=True)



class ClienteCreateRequest(BaseModel):
    """
    Schema para requisição de criação de um novo Cliente.
    """
    nome: str = Field(..., min_length=1, max_length=100, description="Nome do cliente.")
    email: EmailStr = Field(..., description="E-mail do cliente.")
    documento: str = Field(..., min_length=11, max_length=18, description="CPF ou CNPJ do cliente.")


class ClienteUpdateRequest(BaseModel):
    """
    Schema para requisição de atualização dos dados de um Cliente.
    """
    nome: str = Field(..., min_length=1, max_length=100, description="Nome do cliente.")
    email: EmailStr = Field(..., description="E-mail do cliente.")
    ativo: bool = Field(..., description="Status de atividade do cliente.")


class ClienteResponse(BaseModel):
    """
    Schema para retorno das informações de um Cliente.
    """
    id: UUID
    nome: str
    email: str
    documento: str
    tenant_id: UUID
    ativo: bool

    model_config = ConfigDict(from_attributes=True)


class FornecedorCreateRequest(BaseModel):
    """
    Schema para requisição de criação de um novo Fornecedor.
    """
    nome_fantasia: str = Field(..., min_length=1, max_length=100, description="Nome fantasia.")
    razao_social: str = Field(..., min_length=1, max_length=100, description="Razão social.")
    cnpj: str = Field(..., min_length=14, max_length=18, description="CNPJ do fornecedor.")


class FornecedorUpdateRequest(BaseModel):
    """
    Schema para requisição de atualização dos dados de um Fornecedor.
    """
    nome_fantasia: str = Field(..., min_length=1, max_length=100, description="Nome fantasia.")
    razao_social: str = Field(..., min_length=1, max_length=100, description="Razão social.")
    ativo: bool = Field(..., description="Status de atividade do fornecedor.")


class FornecedorResponse(BaseModel):
    """
    Schema para retorno das informações de um Fornecedor.
    """
    id: UUID
    nome_fantasia: str
    razao_social: str
    cnpj: str
    tenant_id: UUID
    ativo: bool

    model_config = ConfigDict(from_attributes=True)


class MovimentacaoEstoqueRequest(BaseModel):
    """
    Schema para requisição de nova movimentação de estoque.
    """
    loja_id: UUID = Field(..., description="ID da loja física.")
    produto_id: UUID = Field(..., description="ID do produto.")
    tipo: str = Field(..., pattern="^(ENTRADA|SAIDA)$", description="Tipo de movimentação: ENTRADA ou SAIDA.")
    quantidade: int = Field(..., gt=0, le=1000000, description="Quantidade a ser movimentada (máximo 1.000.000).")
    motivo: str = Field(..., min_length=1, max_length=255, description="Motivo da movimentação.")


class MovimentacaoEstoqueResponse(BaseModel):
    """
    Schema para retorno de uma movimentação registrada (ledger).
    """
    id: UUID
    loja_id: UUID
    produto_id: UUID
    tipo: str
    quantidade: int
    motivo: str
    tenant_id: UUID
    data_movimentacao: datetime

    model_config = ConfigDict(from_attributes=True)


class EstoqueSaldoResponse(BaseModel):
    """
    Schema para retorno del saldo consolidado de estoque.
    """
    id: UUID
    loja_id: UUID
    produto_id: UUID
    quantidade: int
    tenant_id: UUID

    model_config = ConfigDict(from_attributes=True)


class RegistroMovimentacaoEstoqueResponse(BaseModel):
    """
    Schema para retorno de sucesso da movimentação com saldo atualizado e histórico registrado.
    """
    saldo: EstoqueSaldoResponse
    movimentacao: MovimentacaoEstoqueResponse

    model_config = ConfigDict(from_attributes=True)


class ItemImportadoNFeResponse(BaseModel):
    """
    Schema para retorno de cada item processado no XML de NF-e.
    """
    produto: ProdutoResponse
    quantidade_importada: float
    valor_unitario_nfe: float
    novo_produto_cadastrado: bool

    model_config = ConfigDict(from_attributes=True)


class ImportarNFeResponse(BaseModel):
    """
    Schema para resposta consolidada da importação de NF-e.
    """
    fornecedor: FornecedorResponse
    itens_processados: List[ItemImportadoNFeResponse]

    model_config = ConfigDict(from_attributes=True)
