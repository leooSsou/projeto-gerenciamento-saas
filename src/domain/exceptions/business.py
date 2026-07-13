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


class LojaNaoEncontradaException(DomainException):
    """
    Exceção lançada quando a busca por uma loja falha.
    """
    def __init__(self, identifier: str) -> None:
        super().__init__(f"Loja com identificador '{identifier}' não foi encontrada.")


class CnpjLojaEmUsoException(DomainException):
    """
    Exceção lançada quando há tentativa de cadastrar CNPJ duplicado na tabela de lojas.
    """
    def __init__(self, cnpj: str) -> None:
        self.cnpj = cnpj
        super().__init__(f"O CNPJ '{cnpj}' já está cadastrado em outra loja no sistema.")


class ProdutoNaoEncontradoException(DomainException):
    """
    Exceção lançada quando a busca por um produto falha.
    """
    def __init__(self, identifier: str) -> None:
        super().__init__(f"Produto com identificador '{identifier}' não foi encontrado.")


class SkuProdutoEmUsoException(DomainException):
    """
    Exceção lançada quando há tentativa de cadastrar SKU duplicado para o mesmo tenant.
    """
    def __init__(self, sku: str) -> None:
        self.sku = sku
        super().__init__(f"O SKU '{sku}' já está cadastrado em outro produto no sistema.")


class ClienteNaoEncontradoException(DomainException):
    """
    Exceção lançada quando a busca por um cliente falha.
    """
    def __init__(self, identifier: str) -> None:
        super().__init__(f"Cliente com identificador '{identifier}' não foi encontrado.")


class DocumentoClienteEmUsoException(DomainException):
    """
    Exceção lançada quando há tentativa de cadastrar documento (CPF/CNPJ) duplicado para o mesmo tenant.
    """
    def __init__(self, documento: str) -> None:
        self.documento = documento
        super().__init__(f"O documento '{documento}' já está cadastrado em outro cliente no sistema.")


class FornecedorNaoEncontradoException(DomainException):
    """
    Exceção lançada quando a busca por um fornecedor falha.
    """
    def __init__(self, identifier: str) -> None:
        super().__init__(f"Fornecedor com identificador '{identifier}' não foi encontrado.")


class CnpjFornecedorEmUsoException(DomainException):
    """
    Exceção lançada quando há tentativa de cadastrar CNPJ duplicado de fornecedor para o mesmo tenant.
    """
    def __init__(self, cnpj: str) -> None:
        self.cnpj = cnpj
        super().__init__(f"O CNPJ '{cnpj}' já está cadastrado em outro fornecedor no sistema.")


