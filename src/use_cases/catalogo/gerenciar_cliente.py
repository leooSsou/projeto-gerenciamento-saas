from dataclasses import dataclass
from uuid import UUID
from typing import List

from src.domain.entities.cliente import Cliente
from src.domain.repositories.cliente_repository import ClienteRepository
from src.domain.exceptions.business import (
    ClienteNaoEncontradoException,
    DocumentoClienteEmUsoException,
)

@dataclass(frozen=True)
class CriarClienteInput:
    nome: str
    email: str
    documento: str
    tenant_id: UUID


@dataclass(frozen=True)
class CriarClienteOutput:
    cliente: Cliente


class CriarCliente:
    """
    Caso de Uso: Criar um novo Cliente.
    """
    def __init__(self, cliente_repo: ClienteRepository) -> None:
        self.cliente_repo = cliente_repo

    def executar(self, input_data: CriarClienteInput) -> CriarClienteOutput:
        # 1. Verifica se já existe outro cliente com o mesmo documento para o tenant
        cliente_existente = self.cliente_repo.obter_por_documento(input_data.documento, input_data.tenant_id)
        if cliente_existente:
            raise DocumentoClienteEmUsoException(input_data.documento)

        # 2. Instancia a entidade de domínio Cliente
        cliente = Cliente(
            nome=input_data.nome,
            email=input_data.email,
            documento=input_data.documento,
            tenant_id=input_data.tenant_id
        )

        # 3. Salva no banco
        cliente_salvo = self.cliente_repo.salvar(cliente)

        return CriarClienteOutput(cliente=cliente_salvo)


@dataclass(frozen=True)
class ObterClienteOutput:
    cliente: Cliente


class ObterCliente:
    """
    Caso de Uso: Obter detalhes de um Cliente pelo ID.
    """
    def __init__(self, cliente_repo: ClienteRepository) -> None:
        self.cliente_repo = cliente_repo

    def executar(self, cliente_id: UUID, tenant_id: UUID) -> ObterClienteOutput:
        cliente = self.cliente_repo.obter_por_id(cliente_id, tenant_id)
        if not cliente:
            raise ClienteNaoEncontradoException(str(cliente_id))

        return ObterClienteOutput(cliente=cliente)


@dataclass(frozen=True)
class ListarClientesOutput:
    clientes: List[Cliente]


class ListarClientes:
    """
    Caso de Uso: Listar todos os Clientes de um Tenant.
    """
    def __init__(self, cliente_repo: ClienteRepository) -> None:
        self.cliente_repo = cliente_repo

    def executar(self, tenant_id: UUID) -> ListarClientesOutput:
        clientes = self.cliente_repo.listar_todos(tenant_id)
        return ListarClientesOutput(clientes=clientes)


@dataclass(frozen=True)
class AtualizarClienteInput:
    id: UUID
    nome: str
    email: str
    ativo: bool
    tenant_id: UUID


@dataclass(frozen=True)
class AtualizarClienteOutput:
    cliente: Cliente


class AtualizarCliente:
    """
    Caso de Uso: Atualizar dados de um Cliente.
    """
    def __init__(self, cliente_repo: ClienteRepository) -> None:
        self.cliente_repo = cliente_repo

    def executar(self, input_data: AtualizarClienteInput) -> AtualizarClienteOutput:
        # 1. Recupera o cliente existente
        cliente = self.cliente_repo.obter_por_id(input_data.id, input_data.tenant_id)
        if not cliente:
            raise ClienteNaoEncontradoException(str(input_data.id))

        # 2. Cria nova instância (documento e tenant permanecem imutáveis)
        cliente_atualizado = Cliente(
            nome=input_data.nome,
            email=input_data.email,
            documento=cliente.documento,
            tenant_id=cliente.tenant_id,
            id=cliente.id,
            ativo=input_data.ativo
        )

        # 3. Salva no banco
        cliente_salvo = self.cliente_repo.salvar(cliente_atualizado)

        return AtualizarClienteOutput(cliente=cliente_salvo)
