from pydantic import BaseModel, EmailStr, Field
from uuid import UUID

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

    class ConfigDict:
        from_attributes = True

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

    class ConfigDict:
        from_attributes = True
