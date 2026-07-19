# 🚀 Documento de Contexto Geral e Handoff do Projeto (Gerenciador de Lojas SaaS)

> **Atenção para qualquer IA ou Desenvolvedor resumindo este projeto:**  
> Este documento contém **todo o contexto arquitetural, estado atual do código, testes, governança Git e o plano da próxima etapa (Onda 3)**. Leia este documento com atenção antes de tomar qualquer ação no código.

---

## 📌 1. Visão Geral do Projeto & Tech Stack

O **Gerenciador de Lojas SaaS** é uma plataforma web de retaguarda e controle financeiro/estoque multiloja com isolamento lógico multi-tenant (*Shared Database, Shared Schema*).

### 🛠️ Tecnologias Utilizadas:
* **Backend**: Python 3.12+ com **FastAPI**.
* **Banco de Dados**: **PostgreSQL 15** (em contêiner Docker na porta `5433` para desenvolvimento/testes local).
* **ORM / Query Builder**: **SQLAlchemy 2.0** (estilo imperativo/clássico com mixins).
* **Migrações**: **Alembic**.
* **Mensageria & Filas**: **Redis** (na porta `6380`) e **Celery** (planejado para Onda 6).
* **Segurança e Rate Limiting**: `bcrypt` (hash de senhas), `python-jose` (tokens JWT) e `slowapi` + Redis (Rate Limiting contra ataques DDoS).
* **Testes**: `pytest` com 100% das suítes rodando isoladamente em banco de dados de teste.
* **Orquestração**: `docker-compose.yml`.

---

## 🏛️ 2. Arquitetura e Padrões de Design (Rigorosamente Seguidos)

O projeto segue rigorosamente os princípios da **Clean Architecture**:

```plaintext
src/
├── domain/                      # Camada 1: Núcleo do Domínio (Regras Puras de Negócio)
│   ├── entities/                # Dataclasses Python congeladas (frozen=True), POPOs sem SQLAlchemy
│   ├── exceptions/              # Exceções de negócio customizadas (DomainException)
│   └── repositories/            # Contratos e Interfaces Abstratas de persistência (ABC)
│
├── use_cases/                   # Camada 2: Casos de Uso da Aplicação
│   ├── autenticacao/            # CriarTenant, AutenticarUsuario
│   ├── catalogo/                # CRUDs de Lojas, Produtos, Clientes e Fornecedores
│   └── estoque/                 # (Onda 3) RegistrarMovimentacao, ImportarNFe
│
└── infrastructure/              # Camada 3 e 4: Frameworks, Drivers e Persistência
    ├── database/                # Modelos SQLAlchemy, Migrations (Alembic) e Repositórios Concretos
    ├── security/                # Bcrypt, JWT handler, Password hashing
    └── web/                     # Rotas FastAPI, Middlewares, Schemas Pydantic, SlowAPI Rate Limiter
```

### 🔒 Isolamento Multi-tenant Absoluto:
* Todas as tabelas de inquilinos possuem a coluna `tenant_id` fornecida pelo mixin `HasTenant` em `src/infrastructure/database/mixins.py`.
* O isolamento lógico é forçado automaticamente no SQLAlchemy via evento `do_orm_execute` em `src/infrastructure/database/session.py`.
* **Regra**: Nenhuma consulta `SELECT`, `UPDATE` ou `DELETE` pode vazar dados de outro `tenant_id`. Se a sessão tiver um `tenant_id` ativo, a cláusula `WHERE tenant_id = current_tenant_id` é injetada de forma implícita.

---

## 📊 3. Estado Atual do Projeto & Progresso (Status Concluído)

Atualmente, **59 testes automatizados estão passando com 100% de sucesso** no Docker (`docker compose exec backend pytest`).

### ✅ Onda 1: Setup, Banco de Dados, Autenticação e Segurança (100% Concluído)
* Setup completo de Docker (PostgreSQL porta `5433`, Redis porta `6380`).
* Entidades de domínio puras `Tenant` e `Usuario`.
* Sistema de autenticação JWT injetando `tenant_id` e `role` (`ADMIN_SAAS`, `DONO`, `GERENTE`).
* Dependência FastAPI `get_current_user` injetando o contexto do tenant ativo na sessão do banco.
* Proteção de **Rate Limiting** com SlowAPI + Redis em rotas críticas de login/cadastro e testes de DDoS em `tests/test_rate_limit.py`.
* Testes de vazamento multi-tenant (*SaaS Leakage*) em `tests/test_vazamento_seguranca.py`.

### ✅ Onda 2: Catálogo Centralizado - Lojas, Produtos, Clientes e Fornecedores (100% Concluído)
* Entidades de domínio puras e repositórios para `Loja`, `Produto`, `Cliente` e `Fornecedor`.
* Regra de negócio de **Precificação Inteligente por Markup** (`calcular_preco_venda(preco_custo, markup)` em `produto.py`).
* Validações matemáticas estritas de CPF e CNPJ com limpeza de caracteres não numéricos em `loja.py`, `cliente.py` e `fornecedor.py`.
* Schemas Pydantic, modelos SQLAlchemy com constraints compostas (`sku + tenant_id`, `cnpj + tenant_id`, `documento + tenant_id`), migrações Alembic e rotas FastAPI CRUD completas.
* Testes de integração de API e testes de vulnerabilidade multi-tenant em `tests/test_vulnerabilidade_catalogo.py`.

### 🌿 Governança Git / GitHub:
* O repositório foi limpo e padronizado. Todas as branches obsoletas/mescladas foram removidas.
* Restaram apenas as branches oficiais: `main` e `develop` (ambas perfeitamente sincronizadas local e remotamente no GitHub `leooSsou/projeto-gerenciamento-saas`).
* O fluxo de entrega adota **Squash and Merge** em entregas de Ondas para manter a `main` com um commit limpo e descritivo por entrega.

---

## 🎯 4. Próxima Etapa: Onda 3 - O Coração do Estoque (Ledger & Concorrência)

Estamos atualmente na **Onda 3**, devidamente planejada e com as atividades divididas em **Frentes Verticais Independentes** entre **Leonardo (User + IA)** e **Jonathas** para desenvolvimento sem bloqueios.

### 📐 Estrutura da Onda 3 (Frentes Verticais):

#### 👤 Frente 1: Ledger de Estoque & Controle de Concorrência (Fim a Fim) -> **RESPONSÁVEL: Leonardo (User + IA)**
* **Objetivo**: Construir a infraestrutura de tabelas de saldo/histórico, a movimentação manual simples e a trava pessimista de banco contra concorrência.
* **Tarefas a Desenvolver**:
  1. **Domínio**:
     - Criar `EstoqueSaldo` (dataclass `frozen=True` com validação `quantidade >= 0`) em `src/domain/entities/estoque_saldo.py`.
     - Criar `EstoqueMovimentacao` (dataclass `frozen=True` com `tipo` = `ENTRADA` | `SAIDA`, `quantidade > 0` e `motivo`) em `src/domain/entities/estoque_movimentacao.py`.
     - Criar `EstoqueInsuficienteException` em `src/domain/exceptions/business.py`.
     - Criar contratos abstratos `EstoqueSaldoRepository` e `EstoqueMovimentacaoRepository` em `src/domain/repositories/`.
  2. **Persistência & Banco**:
     - Mapear `EstoqueSaldoModel` e `EstoqueMovimentacaoModel` em `src/infrastructure/database/models.py`.
     - Gerar e aplicar a migração Alembic (`alembic revision --autogenerate -m "criar tabelas estoque_saldos e estoque_movimentacoes"`).
     - Criar `RepositorioEstoqueSaldoSQLAlchemy` e `RepositorioEstoqueMovimentacaoSQLAlchemy` em `repositorios_concrete.py`.
     - **CRÍTICO**: Implementar o método `obter_por_loja_e_produto_com_lock` no repositório utilizando `.with_for_update()` do SQLAlchemy para aplicar o bloqueio pessimista (`SELECT FOR UPDATE`).
  3. **Caso de Uso**:
     - Implementar `RegistrarMovimentacaoEstoque` em `src/use_cases/estoque/registrar_movimentacao.py` (executa a transação com lock, valida saldo em saídas, ajusta a tabela de saldos e registra o histórico imutável no ledger).
  4. **Web / API**:
     - Criar schemas Pydantic em `schemas.py` (`MovimentacaoEstoqueRequest`, `MovimentacaoEstoqueResponse`, etc.).
     - Criar rotas FastAPI em `src/infrastructure/web/estoque.py`:
       - `POST /estoque/movimentar`
       - `GET /estoque/saldos`
       - `GET /estoque/movimentacoes`
     - Registrar o router em `main.py`.
  5. **Testes Automatizados**:
     - Testes de integração em `tests/test_estoque_ledger.py`.
     - Testes de concorrência com requisições simultâneas em paralelo (threads) em `tests/test_concorrencia_estoque.py` (validando que a trava `SELECT FOR UPDATE` impede saldos negativos em retiradas síncronas).

#### 👤 Frente 2: Importação de NF-e & Precificação Inteligente -> **RESPONSÁVEL: Jonathas**
* **Objetivo**: Parser de XML de NF-e (v4.00), auto-cadastro de fornecedores/produtos e recálculo do custo médio ponderado.
* **Tarefas de Jonathas**:
  - Adicionar `codigo_barras` e `fornecedor_id` no modelo `Produto` e na tabela `produtos`.
  - Criar parser de XML de NF-e e o caso de uso `ImportarEstoqueNFe`.
  - Criar rota `POST /estoque/importar-xml`.

---

## 🗺️ 5. Roadmap das Próximas Ondas (Visão de Futuro)

* **Onda 4**: Transferências Logísticas e Auditoria Física (Máquina de estados `SOLICITADO` -> `DESPACHADO` -> `RECEBIDO` / `DIVERGENTE`, contagem rotativa e perdas).
* **Onda 5**: Faturamento Administrativo, Financeiro (Contas a pagar/receber) e CRM (Crediário / límite de crédito de clientes).
* **Onda 6**: Analytics, Dashboards (Curva ABC, Ticket Médio, Rupturas de Estoque) e Celery/Redis Workers para envio de relatórios por e-mail.
* **Onda 7**: Frontend React SPA (Vite + Tailwind CSS + TanStack Query).

---

## ⚡ 6. Comandos Essenciais para Iniciar no Novo Ambiente

Assim que você reinstalar o sistema operacional e clonar o repositório (`git clone`), execute os seguintes comandos no terminal:

### 1. Iniciar os Contêineres Docker:
```bash
docker compose up --build -d
```

### 2. Verificar Status dos Serviços:
```bash
docker compose ps
```

### 3. Rodar a Suíte Completa de Testes Automatizados:
```bash
docker compose exec backend pytest
```
*(Espera-se que todos os 59 testes passem com 100% de sucesso).*

### 4. Executar Migrações do Alembic (se necessário):
```bash
docker compose exec backend alembic upgrade head
```

---

## 📝 7. Instrução Final para a IA ao Retomar o Projeto

> **Para a IA que assumir o atendimento neste novo ambiente:**
> 1. Diga ao usuário que você leu este documento (`DOCUMENTO_CONTEXTO_IA.md`).
> 2. Confirme que entende o estado do projeto (Ondas 1 e 2 100% concluídas com 59 testes passando).
> 3. Informe que estamos prontos para iniciar a **Frente 1 da Onda 3** (desenvolvimento do Ledger de Estoque & Controle de Concorrência Fim a Fim por Leonardo e você).
> 4. Siga rigorosamente a Clean Architecture e os padrões de teste descritos neste documento.
