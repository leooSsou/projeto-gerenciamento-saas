from dataclasses import dataclass
from uuid import UUID
from typing import List

from src.domain.entities.loja import Loja
from src.domain.repositories.loja_repository import LojaRepository
from src.domain.exceptions.business import (
    LojaNaoEncontradaException,
    CnpjLojaEmUsoException,
)

@dataclass(frozen=True)
class CriarLojaInput:
    nome: str
    cnpj: str
    endereco: str
    tenant_id: UUID


@dataclass(frozen=True)
class CriarLojaOutput:
    loja: Loja


class CriarLoja:
    """
    Caso de Uso: Criar uma nova filial/Loja para um Tenant específico.
    """
    def __init__(self, loja_repo: LojaRepository) -> None:
        self.loja_repo = loja_repo

    def executar(self, input_data: CriarLojaInput) -> CriarLojaOutput:
        # 1. Verifica se já existe outra loja com o mesmo CNPJ para o tenant
        loja_existente = self.loja_repo.obter_por_cnpj(input_data.cnpj, input_data.tenant_id)
        if loja_existente:
            raise CnpjLojaEmUsoException(input_data.cnpj)

        # 2. Instancia a entidade de domínio Loja (valida CNPJ e campos internamente)
        loja = Loja(
            nome=input_data.nome,
            cnpj=input_data.cnpj,
            endereco=input_data.endereco,
            tenant_id=input_data.tenant_id
        )

        # 3. Persiste a loja no banco
        loja_salva = self.loja_repo.salvar(loja)

        return CriarLojaOutput(loja=loja_salva)


@dataclass(frozen=True)
class ObterLojaOutput:
    loja: Loja


class ObterLoja:
    """
    Caso de Uso: Obter os dados de uma Loja específica respeitando o Tenant.
    """
    def __init__(self, loja_repo: LojaRepository) -> None:
        self.loja_repo = loja_repo

    def executar(self, loja_id: UUID, tenant_id: UUID) -> ObterLojaOutput:
        loja = self.loja_repo.obter_por_id(loja_id, tenant_id)
        if not loja:
            raise LojaNaoEncontradaException(str(loja_id))

        return ObterLojaOutput(loja=loja)


@dataclass(frozen=True)
class ListarLojasOutput:
    lojas: List[Loja]


class ListarLojas:
    """
    Caso de Uso: Listar todas as Lojas associadas a um Tenant.
    """
    def __init__(self, loja_repo: LojaRepository) -> None:
        self.loja_repo = loja_repo

    def executar(self, tenant_id: UUID) -> ListarLojasOutput:
        lojas = self.loja_repo.listar_todas(tenant_id)
        return ListarLojasOutput(lojas=lojas)


@dataclass(frozen=True)
class AtualizarLojaInput:
    id: UUID
    nome: str
    endereco: str
    ativo: bool
    tenant_id: UUID


@dataclass(frozen=True)
class AtualizarLojaOutput:
    loja: Loja


class AtualizarLoja:
    """
    Caso de Uso: Atualizar os campos editáveis de uma Loja específica de um Tenant.
    """
    def __init__(self, loja_repo: LojaRepository) -> None:
        self.loja_repo = loja_repo

    def executar(self, input_data: AtualizarLojaInput) -> AtualizarLojaOutput:
        # 1. Recupera a loja existente
        loja = self.loja_repo.obter_por_id(input_data.id, input_data.tenant_id)
        if not loja:
            raise LojaNaoEncontradaException(str(input_data.id))

        # 2. Cria nova instância com dados atualizados (CNPJ e ID permanecem inalterados)
        loja_atualizada = Loja(
            nome=input_data.nome,
            cnpj=loja.cnpj,
            endereco=input_data.endereco,
            tenant_id=loja.tenant_id,
            id=loja.id,
            ativo=input_data.ativo
        )

        # 3. Salva no banco de dados
        loja_salva = self.loja_repo.salvar(loja_atualizada)

        return AtualizarLojaOutput(loja=loja_salva)
