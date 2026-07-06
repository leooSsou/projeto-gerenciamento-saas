from abc import ABC, abstractmethod
from dataclasses import dataclass
from src.domain.entities.usuario import Usuario
from src.domain.repositories.usuario_repository import UsuarioRepository
from src.domain.repositories.tenant_repository import TenantRepository
from src.domain.exceptions.business import CredenciaisInvalidasException, TenantNaoEncontradoException

class ServicoCriptografia(ABC):
    """
    Interface abstrata para serviços de criptografia e hashing de senhas.
    """
    @abstractmethod
    def verificar_senha(self, senha_plana: str, senha_hash: str) -> bool:
        """
        Retorna True se a senha plana coincidir com o hash, senão False.
        """
        pass

    @abstractmethod
    def gerar_hash(self, senha_plana: str) -> str:
        """
        Gera um hash seguro a partir de uma senha em texto plano.
        """
        pass


@dataclass(frozen=True)
class AutenticarUsuarioInput:
    email: str
    senha_plana: str


@dataclass(frozen=True)
class AutenticarUsuarioOutput:
    usuario: Usuario


class AutenticarUsuario:
    """
    Caso de Uso: Autenticar um usuário no sistema com base no e-mail e senha informados.
    """
    def __init__(
        self,
        usuario_repo: UsuarioRepository,
        tenant_repo: TenantRepository,
        servico_cripto: ServicoCriptografia
    ) -> None:
        self.usuario_repo = usuario_repo
        self.tenant_repo = tenant_repo
        self.servico_cripto = servico_cripto

    def executar(self, input_data: AutenticarUsuarioInput) -> AutenticarUsuarioOutput:
        # 1. Recupera o usuário pelo e-mail
        usuario = self.usuario_repo.obter_por_email(input_data.email)
        if not usuario:
            raise CredenciaisInvalidasException()

        # 2. Valida se o Tenant associado existe na base de dados
        tenant = self.tenant_repo.obter_por_id(usuario.tenant_id)
        if not tenant:
            raise TenantNaoEncontradoException()

        # 3. Valida a senha utilizando a acoplagem do serviço de criptografia
        if not self.servico_cripto.verificar_senha(input_data.senha_plana, usuario.senha_hash):
            raise CredenciaisInvalidasException()

        return AutenticarUsuarioOutput(usuario=usuario)

