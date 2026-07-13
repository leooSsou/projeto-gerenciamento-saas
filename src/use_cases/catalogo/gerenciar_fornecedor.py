from dataclasses import dataclass
from uuid import UUID
from typing import List

from src.domain.entities.fornecedor import Fornecedor
from src.domain.repositories.fornecedor_repository import FornecedorRepository
from src.domain.exceptions.business import (
    FornecedorNaoEncontradoException,
    CnpjFornecedorEmUsoException,
)

@dataclass(frozen=True)
class CriarFornecedorInput:
    nome_fantasia: str
    razao_social: str
    cnpj: str
    tenant_id: UUID


@dataclass(frozen=True)
class CriarFornecedorOutput:
    fornecedor: Fornecedor


class CriarFornecedor:
    """
    Caso de Uso: Criar um novo Fornecedor.
    """
    def __init__(self, fornecedor_repo: FornecedorRepository) -> None:
        self.fornecedor_repo = fornecedor_repo

    def executar(self, input_data: CriarFornecedorInput) -> CriarFornecedorOutput:
        # 1. Verifica se já existe outro fornecedor com o mesmo CNPJ para o tenant
        fornecedor_existente = self.fornecedor_repo.obter_por_cnpj(input_data.cnpj, input_data.tenant_id)
        if fornecedor_existente:
            raise CnpjFornecedorEmUsoException(input_data.cnpj)

        # 2. Instancia a entidade de domínio Fornecedor
        fornecedor = Fornecedor(
            nome_fantasia=input_data.nome_fantasia,
            razao_social=input_data.razao_social,
            cnpj=input_data.cnpj,
            tenant_id=input_data.tenant_id
        )

        # 3. Salva no banco
        fornecedor_salvo = self.fornecedor_repo.salvar(fornecedor)

        return CriarFornecedorOutput(fornecedor=fornecedor_salvo)


@dataclass(frozen=True)
class ObterFornecedorOutput:
    fornecedor: Fornecedor


class ObterFornecedor:
    """
    Caso de Uso: Obter detalhes de um Fornecedor pelo ID.
    """
    def __init__(self, fornecedor_repo: FornecedorRepository) -> None:
        self.fornecedor_repo = fornecedor_repo

    def executar(self, fornecedor_id: UUID, tenant_id: UUID) -> ObterFornecedorOutput:
        fornecedor = self.fornecedor_repo.obter_por_id(fornecedor_id, tenant_id)
        if not fornecedor:
            raise FornecedorNaoEncontradoException(str(fornecedor_id))

        return ObterFornecedorOutput(fornecedor=fornecedor)


@dataclass(frozen=True)
class ListarFornecedoresOutput:
    fornecedores: List[Fornecedor]


class ListarFornecedores:
    """
    Caso de Uso: Listar todos os Fornecedores de um Tenant.
    """
    def __init__(self, fornecedor_repo: FornecedorRepository) -> None:
        self.fornecedor_repo = fornecedor_repo

    def executar(self, tenant_id: UUID) -> ListarFornecedoresOutput:
        fornecedores = self.fornecedor_repo.listar_todos(tenant_id)
        return ListarFornecedoresOutput(fornecedores=fornecedores)


@dataclass(frozen=True)
class AtualizarFornecedorInput:
    id: UUID
    nome_fantasia: str
    razao_social: str
    ativo: bool
    tenant_id: UUID


@dataclass(frozen=True)
class AtualizarFornecedorOutput:
    fornecedor: Fornecedor


class AtualizarFornecedor:
    """
    Caso de Uso: Atualizar dados de um Fornecedor.
    """
    def __init__(self, fornecedor_repo: FornecedorRepository) -> None:
        self.fornecedor_repo = fornecedor_repo

    def executar(self, input_data: AtualizarFornecedorInput) -> AtualizarFornecedorOutput:
        # 1. Recupera o fornecedor existente
        fornecedor = self.fornecedor_repo.obter_por_id(input_data.id, input_data.tenant_id)
        if not fornecedor:
            raise FornecedorNaoEncontradoException(str(input_data.id))

        # 2. Cria nova instância (cnpj e tenant permanecem imutáveis)
        fornecedor_atualizado = Fornecedor(
            nome_fantasia=input_data.nome_fantasia,
            razao_social=input_data.razao_social,
            cnpj=fornecedor.cnpj,
            tenant_id=fornecedor.tenant_id,
            id=fornecedor.id,
            ativo=input_data.ativo
        )

        # 3. Salva no banco
        fornecedor_salvo = self.fornecedor_repo.salvar(fornecedor_atualizado)

        return   AtualizarFornecedorOutput(fornecedor=fornecedor_salvo)
