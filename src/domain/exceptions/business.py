class DomainException(Exception):
    """
    Classe base para todas as exceções de negócio do domínio.
    """
    pass


class CnpjEmUsoException(DomainException):
    """
    Exceção lançada ao tentar cadastrar um Tenant com CNPJ já existente.
    """
    def __init__(self, cnpj: str) -> None:
        self.cnpj = cnpj
        super().__init__(f"O CNPJ '{cnpj}' já está cadastrado no sistema.")


class EmailEmUsoException(DomainException):
    """
    Exceção lançada ao tentar cadastrar um Usuário com e-mail já existente.
    """
    def __init__(self, email: str) -> None:
        self.email = email
        super().__init__(f"O e-mail '{email}' já está cadastrado no sistema.")


class CredenciaisInvalidasException(DomainException):
    """
    Exceção lançada quando a senha ou e-mail de login estão incorretos.
    """
    def __init__(self) -> None:
        super().__init__("Credenciais inválidas: e-mail ou senha incorretos.")


class TenantNaoEncontradoException(DomainException):
    """
    Exceção lançada quando o inquilino/Tenant não é encontrado.
    """
    def __init__(self, identifier: str) -> None:
        super().__init__(f"Tenant com identificador '{identifier}' não foi encontrado.")


class UsuarioNaoEncontradoException(DomainException):
    """
    Exceção lançada quando o Usuário não é encontrado.
    """
    def __init__(self, identifier: str) -> None:
        super().__init__(f"Usuário com identificador '{identifier}' não foi encontrado.")
