# 📋 Integração da Entidade Loja - Onda 2

Olá Leonardo, segue a especificação técnica para a implementação da infraestrutura da **Loja** (Banco de Dados, Repositório e FastAPI).

---

## 1. Mapeamento do Banco de Dados (SQLAlchemy)
Em `src/infrastructure/database/models.py`, criar a classe `LojaModel`:

* **Herança**: Deve herdar de `Base` e `HasTenant` (para garantir o isolamento global de tenant).
* **Campos**:
  - `id`: `Mapped[UUID]` (Chave Primária, padrão `uuid4`).
  - `nome`: `Mapped[str]` (String de tamanho 100, `nullable=False`).
  - `cnpj`: `Mapped[str]` (String de tamanho 14, `unique=True` ou unique combinado com tenant se aplicável, `nullable=False`).
  - `endereco`: `Mapped[str]` (String de tamanho 255, `nullable=False`).
  - `ativo`: `Mapped[bool]` (Boolean, `default=True`, `nullable=False`).

---

## 2. Migração com Alembic
Gerar a migração para criar a tabela física `lojas`:
```bash
docker compose run --rm backend alembic revision --autogenerate -m "criar tabela lojas"
```

---

## 3. Repositório Concreto (SQLAlchemy)
Em `src/infrastructure/database/repositorios_concrete.py`, criar `SQLAlchemyLojaRepository`:

* **Interface**: Deve implementar a classe abstrata `LojaRepository`.
* **Métodos**:
  - `salvar(self, loja: Loja) -> Loja`
  - `obter_por_id(self, id: UUID, tenant_id: UUID) -> Optional[Loja]`
  - `obter_por_cnpj(self, cnpj: str, tenant_id: UUID) -> Optional[Loja]`
  - `listar_todas(self, tenant_id: UUID) -> List[Loja]`
* **Mapeador**: Lembrar de criar o mapper para traduzir entre o modelo de banco (`LojaModel`) e a entidade pura de domínio (`Loja`).

---

## 4. Endpoints FastAPI
Desenvolver as rotas CRUD protegidas por `get_current_user` garantindo o escopo do tenant ativo.
