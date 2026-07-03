from dataclasses import dataclass
from src.domain.entities.tenant import Tenant
from src.domain.entities.usuario import Usuario
from src.domain.repositories.tenant_repository import TenantRepository
from src.domain.repositories.usuario_repository import UsuarioRepository
from src.domain.exceptions.business import CnpjEmUsoException, EmailEmUsoException

@dataclass(frozen=True)
class CriarTenantInput:
    nome_fantasia: str
    razao_social: str
    cnpj: str
    dono_nome: str
    dono_email: str
    dono_senha_hash: str


@dataclass(frozen=True)
class CriarTenantOutput:
    tenant: Tenant
    usuario: Usuario


class CriarTenant:
    """
    Caso de Uso: Criar um novo Tenant (empresa/filial principal) e cadastrar seu respectivo Dono.
    """
    def __init__(
        self,
        tenant_repo: TenantRepository,
        usuario_repo: UsuarioRepository
    ) -> None:
        self.tenant_repo = tenant_repo
        self.usuario_repo = usuario_repo

    def executar(self, input_data: CriarTenantInput) -> CriarTenantOutput:
        # 1. Valida se o CNPJ já está cadastrado
        if self.tenant_repo.obter_por_cnpj(input_data.cnpj):
            raise CnpjEmUsoException(input_data.cnpj)

        # 2. Valida se o e-mail do proprietário já está em uso
        if self.usuario_repo.obter_por_email(input_data.dono_email):
            raise EmailEmUsoException(input_data.dono_email)

        # 3. Cria a entidade pura Tenant
        tenant = Tenant(
            nome_fantasia=input_data.nome_fantasia,
            razao_social=input_data.razao_social,
            cnpj=input_data.cnpj
        )
        tenant_salvo = self.tenant_repo.salvar(tenant)

        # 4. Cria a entidade pura Usuario vinculada ao Tenant como DONO
        usuario = Usuario(
            nome=input_data.dono_nome,
            email=input_data.dono_email,
            senha_hash=input_data.dono_senha_hash,
            role="DONO",
            tenant_id=tenant_salvo.id
        )
        usuario_salvo = self.usuario_repo.salvar(usuario)

        return CriarTenantOutput(tenant=tenant_salvo, usuario=usuario_salvo)
