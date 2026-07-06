import pytest
from uuid import UUID, uuid4
from typing import Optional, Dict, List

from src.domain.entities.tenant import Tenant
from src.domain.entities.usuario import Usuario
from src.domain.entities.loja import Loja
from src.domain.repositories.tenant_repository import TenantRepository
from src.domain.repositories.usuario_repository import UsuarioRepository
from src.domain.repositories.loja_repository import LojaRepository
from src.domain.exceptions.business import (
    CnpjEmUsoException,
    EmailEmUsoException,
    CredenciaisInvalidasException,
    LojaNaoEncontradaException,
    CnpjLojaEmUsoException,
)
from src.use_cases.autenticacao.criar_tenant import (
    CriarTenant,
    CriarTenantInput,
)
from src.use_cases.autenticacao.autenticar_usuario import (
    AutenticarUsuario,
    AutenticarUsuarioInput,
    ServicoCriptografia,
)
from src.use_cases.catalogo.gerenciar_loja import (
    CriarLoja,
    CriarLojaInput,
    ObterLoja,
    ListarLojas,
    AtualizarLoja,
    AtualizarLojaInput,
)

# -----------------------------------------------------------------------------
# Mocks / Implementações In-Memory para Teste de Unidade dos Casos de Uso
# -----------------------------------------------------------------------------

class InMemoryTenantRepository(TenantRepository):
    def __init__(self) -> None:
        self.tenants: Dict[UUID, Tenant] = {}

    def salvar(self, tenant: Tenant) -> Tenant:
        self.tenants[tenant.id] = tenant
        return tenant

    def obter_por_cnpj(self, cnpj: str) -> Optional[Tenant]:
        # Normaliza o CNPJ removendo formatação para a busca
        cnpj_limpo = "".join(filter(str.isdigit, cnpj))
        for t in self.tenants.values():
            if t.cnpj == cnpj_limpo:
                return t
        return None

    def obter_por_id(self, id: UUID) -> Optional[Tenant]:
        return self.tenants.get(id)


class InMemoryUsuarioRepository(UsuarioRepository):
    def __init__(self) -> None:
        self.usuarios: Dict[UUID, Usuario] = {}

    def salvar(self, usuario: Usuario) -> Usuario:
        self.usuarios[usuario.id] = usuario
        return usuario

    def obter_por_email(self, email: str) -> Optional[Usuario]:
        for u in self.usuarios.values():
            if u.email.lower() == email.lower():
                return u
        return None

    def obter_por_id(self, id: UUID) -> Optional[Usuario]:
        return self.usuarios.get(id)


class FakeServicoCriptografia(ServicoCriptografia):
    def verificar_senha(self, senha_plana: str, senha_hash: str) -> bool:
        # Lógica simples para mock: assume que a senha bate se for igual ao hash com prefixo "hash_"
        return senha_hash == f"hash_{senha_plana}"

    def gerar_hash(self, senha_plana: str) -> str:
        return f"hash_{senha_plana}"

# -----------------------------------------------------------------------------
# Testes do Caso de Uso: CriarTenant
# -----------------------------------------------------------------------------

def test_criar_tenant_sucesso() -> None:
    tenant_repo = InMemoryTenantRepository()
    usuario_repo = InMemoryUsuarioRepository()
    servico_cripto = FakeServicoCriptografia()
    use_case = CriarTenant(tenant_repo, usuario_repo, servico_cripto)

    input_data = CriarTenantInput(
        nome_fantasia="Loja Principal",
        razao_social="Loja Principal S/A",
        cnpj="12.345.678/0001-95",
        dono_nome="Carlos Silva",
        dono_email="carlos@email.com",
        dono_senha_plana="senha123"
    )

    output = use_case.executar(input_data)

    # Verifica se os objetos foram gerados corretamente
    assert output.tenant.nome_fantasia == "Loja Principal"
    assert output.tenant.cnpj == "12345678000195"  # CNPJ deve estar limpo
    assert output.usuario.nome == "Carlos Silva"
    assert output.usuario.email == "carlos@email.com"
    assert output.usuario.role == "DONO"
    assert output.usuario.tenant_id == output.tenant.id
    assert output.usuario.senha_hash == "hash_senha123"

    # Verifica se foram salvos nos repositórios
    assert tenant_repo.obter_por_id(output.tenant.id) is not None
    assert usuario_repo.obter_por_id(output.usuario.id) is not None


def test_criar_tenant_cnpj_duplicado() -> None:
    tenant_repo = InMemoryTenantRepository()
    usuario_repo = InMemoryUsuarioRepository()
    servico_cripto = FakeServicoCriptografia()
    use_case = CriarTenant(tenant_repo, usuario_repo, servico_cripto)

    # Cadastra um tenant com o mesmo CNPJ previamente
    tenant_repo.salvar(Tenant(
        nome_fantasia="Outro Nome",
        razao_social="Razao Social Ltda",
        cnpj="12345678000195"
    ))

    input_data = CriarTenantInput(
        nome_fantasia="Loja Principal",
        razao_social="Loja Principal S/A",
        cnpj="12.345.678/0001-95",
        dono_nome="Carlos Silva",
        dono_email="carlos@email.com",
        dono_senha_plana="senha123"
    )

    with pytest.raises(CnpjEmUsoException):
        use_case.executar(input_data)


def test_criar_tenant_email_dono_duplicado() -> None:
    tenant_repo = InMemoryTenantRepository()
    usuario_repo = InMemoryUsuarioRepository()
    servico_cripto = FakeServicoCriptografia()
    use_case = CriarTenant(tenant_repo, usuario_repo, servico_cripto)

    # Cadastra um usuário com o mesmo e-mail previamente
    usuario_repo.salvar(Usuario(
        nome="Outro Carlos",
        email="carlos@email.com",
        senha_hash="qualquer_hash",
        role="DONO",
        tenant_id=uuid4()
    ))

    input_data = CriarTenantInput(
        nome_fantasia="Loja Principal",
        razao_social="Loja Principal S/A",
        cnpj="12.345.678/0001-95",
        dono_nome="Carlos Silva",
        dono_email="carlos@email.com",
        dono_senha_plana="senha123"
    )

    with pytest.raises(EmailEmUsoException):
        use_case.executar(input_data)

# -----------------------------------------------------------------------------
# Testes do Caso de Uso: AutenticarUsuario
# -----------------------------------------------------------------------------

def test_autenticar_usuario_sucesso() -> None:
    usuario_repo = InMemoryUsuarioRepository()
    tenant_repo = InMemoryTenantRepository()
    servico_cripto = FakeServicoCriptografia()
    use_case = AutenticarUsuario(usuario_repo, tenant_repo, servico_cripto)

    # Cria e salva o Tenant associado
    tenant = Tenant(
        nome_fantasia="Empresa Teste",
        razao_social="Empresa Teste Ltda",
        cnpj="12.345.678/0001-95"
    )
    tenant_repo.salvar(tenant)

    # Cria o usuário cadastrado no mock (com loja para perfil GERENTE)
    usuario = Usuario(
        nome="Ana Souza",
        email="ana@email.com",
        senha_hash="hash_senha123",
        role="GERENTE",
        tenant_id=tenant.id,
        loja_atribuida_id=uuid4()
    )
    usuario_repo.salvar(usuario)

    input_data = AutenticarUsuarioInput(
        email="ana@email.com",
        senha_plana="senha123"
    )

    output = use_case.executar(input_data)
    assert output.usuario.id == usuario.id
    assert output.usuario.nome == "Ana Souza"


def test_autenticar_usuario_email_inexistente() -> None:
    usuario_repo = InMemoryUsuarioRepository()
    tenant_repo = InMemoryTenantRepository()
    servico_cripto = FakeServicoCriptografia()
    use_case = AutenticarUsuario(usuario_repo, tenant_repo, servico_cripto)

    input_data = AutenticarUsuarioInput(
        email="inexistente@email.com",
        senha_plana="senha123"
    )

    with pytest.raises(CredenciaisInvalidasException):
        use_case.executar(input_data)


def test_autenticar_usuario_senha_incorreta() -> None:
    usuario_repo = InMemoryUsuarioRepository()
    tenant_repo = InMemoryTenantRepository()
    servico_cripto = FakeServicoCriptografia()
    use_case = AutenticarUsuario(usuario_repo, tenant_repo, servico_cripto)

    # Cria e salva o Tenant associado
    tenant = Tenant(
        nome_fantasia="Empresa Teste",
        razao_social="Empresa Teste Ltda",
        cnpj="12.345.678/0001-95"
    )
    tenant_repo.salvar(tenant)

    usuario_repo.salvar(Usuario(
        nome="Ana Souza",
        email="ana@email.com",
        senha_hash="hash_senha123",
        role="GERENTE",
        tenant_id=tenant.id,
        loja_atribuida_id=uuid4()
    ))

    input_data = AutenticarUsuarioInput(
        email="ana@email.com",
        senha_plana="senha_errada"
    )

    with pytest.raises(CredenciaisInvalidasException):
        use_case.executar(input_data)


# -----------------------------------------------------------------------------
# Mocks e Testes do Catálogo de Lojas (Onda 2 - TDD)
# -----------------------------------------------------------------------------

class InMemoryLojaRepository(LojaRepository):
    def __init__(self) -> None:
        self.lojas: Dict[UUID, Loja] = {}

    def salvar(self, loja: Loja) -> Loja:
        self.lojas[loja.id] = loja
        return loja

    def obter_por_id(self, id: UUID, tenant_id: UUID) -> Optional[Loja]:
        loja = self.lojas.get(id)
        if loja and loja.tenant_id == tenant_id:
            return loja
        return None

    def obter_por_cnpj(self, cnpj: str, tenant_id: UUID) -> Optional[Loja]:
        cnpj_limpo = "".join(filter(str.isdigit, cnpj))
        for loja in self.lojas.values():
            if loja.cnpj == cnpj_limpo and loja.tenant_id == tenant_id:
                return loja
        return None

    def listar_todas(self, tenant_id: UUID) -> List[Loja]:
        return [loja for loja in self.lojas.values() if loja.tenant_id == tenant_id]


def test_criar_loja_sucesso() -> None:
    loja_repo = InMemoryLojaRepository()
    use_case = CriarLoja(loja_repo)
    tenant_id = uuid4()

    input_data = CriarLojaInput(
        nome="Filial Centro",
        cnpj="25.923.825/0001-09",
        endereco="Av. Central, 100",
        tenant_id=tenant_id
    )

    output = use_case.executar(input_data)
    assert output.loja.nome == "Filial Centro"
    assert output.loja.cnpj == "25923825000109"
    assert output.loja.endereco == "Av. Central, 100"
    assert output.loja.tenant_id == tenant_id
    assert output.loja.ativo is True


def test_criar_loja_cnpj_duplicado() -> None:
    loja_repo = InMemoryLojaRepository()
    use_case = CriarLoja(loja_repo)
    tenant_id = uuid4()

    loja_existente = Loja(
        nome="Outra Loja",
        cnpj="25.923.825/0001-09",
        endereco="Rua Teste, 10",
        tenant_id=tenant_id
    )
    loja_repo.salvar(loja_existente)

    input_data = CriarLojaInput(
        nome="Filial Centro",
        cnpj="25.923.825/0001-09",
        endereco="Av. Central, 100",
        tenant_id=tenant_id
    )

    with pytest.raises(CnpjLojaEmUsoException):
        use_case.executar(input_data)


def test_obter_loja_sucesso() -> None:
    loja_repo = InMemoryLojaRepository()
    use_case = ObterLoja(loja_repo)
    tenant_id = uuid4()

    loja = Loja(
        nome="Filial Norte",
        cnpj="05.292.609/0001-03",
        endereco="Av. Norte, 200",
        tenant_id=tenant_id
    )
    loja_repo.salvar(loja)

    output = use_case.executar(loja_id=loja.id, tenant_id=tenant_id)
    assert output.loja.id == loja.id
    assert output.loja.nome == "Filial Norte"


def test_obter_loja_nao_encontrada() -> None:
    loja_repo = InMemoryLojaRepository()
    use_case = ObterLoja(loja_repo)
    tenant_id = uuid4()

    with pytest.raises(LojaNaoEncontradaException):
        use_case.executar(loja_id=uuid4(), tenant_id=tenant_id)


def test_listar_lojas() -> None:
    loja_repo = InMemoryLojaRepository()
    use_case = ListarLojas(loja_repo)
    tenant_a = uuid4()
    tenant_b = uuid4()

    loja_a1 = Loja(nome="A1", cnpj="25.923.825/0001-09", endereco="End", tenant_id=tenant_a)
    loja_a2 = Loja(nome="A2", cnpj="05.292.609/0001-03", endereco="End", tenant_id=tenant_a)
    loja_b1 = Loja(nome="B1", cnpj="67.827.595/0001-24", endereco="End", tenant_id=tenant_b)

    loja_repo.salvar(loja_a1)
    loja_repo.salvar(loja_a2)
    loja_repo.salvar(loja_b1)

    output_a = use_case.executar(tenant_id=tenant_a)
    assert len(output_a.lojas) == 2
    assert any(loja.nome == "A1" for loja in output_a.lojas)
    assert any(loja.nome == "A2" for loja in output_a.lojas)

    output_b = use_case.executar(tenant_id=tenant_b)
    assert len(output_b.lojas) == 1
    assert output_b.lojas[0].nome == "B1"


def test_atualizar_loja_sucesso() -> None:
    loja_repo = InMemoryLojaRepository()
    use_case = AtualizarLoja(loja_repo)
    tenant_id = uuid4()

    loja = Loja(
        nome="Filial Centro",
        cnpj="25.923.825/0001-09",
        endereco="Av. Central, 100",
        tenant_id=tenant_id
    )
    loja_repo.salvar(loja)

    input_data = AtualizarLojaInput(
        id=loja.id,
        nome="Filial Centro Renovada",
        endereco="Av. Central, 150",
        ativo=False,
        tenant_id=tenant_id
    )

    output = use_case.executar(input_data)
    assert output.loja.nome == "Filial Centro Renovada"
    assert output.loja.endereco == "Av. Central, 150"
    assert output.loja.ativo is False


