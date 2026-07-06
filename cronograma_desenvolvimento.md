# Cronograma de Desenvolvimento: Gerenciador de Lojas SaaS (Fase 1)

Este documento registra o planejamento técnico macro, as ondas de entrega e o progresso das tarefas concluídas e pendentes para a construção da Fase 1 da plataforma.

---

## 🛠️ Progresso Geral do Projeto

```mermaid
gantt
    title Roadmap de Desenvolvimento (Fase 1)
    dateFormat  YYYY-MM-DD
    section Backend API
    Setup e Banco de Dados          :active, wave1, 2026-06-28, 3d
    Autenticação e Multi-Tenancy    : wave2, after wave1, 5d
    Catálogo Centralizado           : wave3, after wave2, 5d
    Ledger de Estoque & Concorrência: wave4, after wave3, 7d
    Transferência e Auditoria       : wave5, after wave4, 5d
    Faturamento & Financeiro        : wave6, after wave5, 5d
    section Frontend React
    Setup e Fluxo de Telas Base     : wave7, after wave2, 4d
    Telas de Cadastros e Estoque    : wave8, after wave7, 8d
    Financeiro & Dashboards         : wave9, after wave8, 6d
```

---

## 📋 Ondas de Desenvolvimento e Checklists

### 🌌 Onda 1: Setup, Banco de Dados e Isolamento Multi-tenant
*Objetivo: Estabelecer o alicerce técnico e garantir a segurança lógica dos inquilinos (tenants) no banco de dados.*

* **Infraestrutura e Base**:
  - [x] Configuração de dependências (`requirements.txt`) compatíveis com Python 3.13.
  - [x] Configuração de variáveis de ambiente (`.env`) e ignorados (`.gitignore`).
  - [x] Criação do `docker-compose.yml` (PostgreSQL na porta `5433` para evitar conflito com serviço local, Redis).
  - [x] Estrutura inicial do FastAPI (`src/infrastructure/web/main.py`).
  - [x] Setup do SQLAlchemy e inicialização do Alembic.
  - [x] Criação e validação do banco de testes PostgreSQL (`gerenciador_saas_test`) no Docker.
  - [x] Implementação de testes de conectividade e health check com `pytest`.
  - [x] Criação de branch `chore/setup-inicial` e envio dos commits no padrão Conventional Commits.
* **Autenticação, JWT e Segurança** (Próximo Passo):
  * **Regras de Negócio e Domínio (Responsável: Jonathas)**:
    - [x] Criar entidades de domínio puras de `Tenant` e `Usuario` em Python puro ([src/domain/entities/](src/domain/entities/)).
    - [x] Definir exceções de negócio customizadas em [src/domain/exceptions/](src/domain/exceptions/).
    - [x] Criar interfaces e contratos abstratos dos repositórios em [src/domain/repositories/](src/domain/repositories/).
    - [x] Implementar os casos de uso purificados em Python: `CriarTenant` e `AutenticarUsuario` em [src/use_cases/autenticacao/](src/use_cases/autenticacao/).
  * **Persistência e Modelagem de Banco (Responsável: Leonardo)**:
    - [x] Mapear os modelos SQLAlchemy físicos de `tenants` e `usuarios` em [src/infrastructure/database/models.py](src/infrastructure/database/models.py) e gerar a migração Alembic.
    - [x] Implementar repositórios SQLAlchemy concretos e configurar o filtro de sessão global do `tenant_id` para isolamento.
  * **Segurança, Web e Testes (Responsável: Douglas)**:
    - [x] Desenvolver utilitários de segurança: hashing de senhas com `bcrypt` e manipulação de tokens JWT em [src/infrastructure/security/](src/infrastructure/security/).
    - [x] Desenvolver as rotas web do FastAPI (`/auth/register`, `/auth/login`) e a dependência de injeção `get_current_user` em [src/infrastructure/web/](src/infrastructure/web/).
    - [x] Escrever a suíte de testes automatizados de integração e de simulação de vazamento multi-tenant (*SaaS leakage*) em [tests/](tests/).

---

### 📦 Onda 2: Catálogo Centralizado (Cadastros Base)
*Objetivo: Criar as tabelas e rotas necessárias para popular o banco de dados antes da movimentação de mercadorias.*

#### 👥 Divisão de Atividades por Responsável

##### 👤 Jonathas (Regras de Negócio e Domínio)
* **Atividades Independentes**:
  - [x] **[Urgência: Alta]** Criar entidade de domínio pura de `Loja` e contrato abstrato de seu repositório em [src/domain/](src/domain/).
  - [ ] **[Urgência: Alta]** Criar entidade de domínio pura de `Produto` e contrato abstrato de seu repositório em [src/domain/](src/domain/).
  - [ ] **[Urgência: Média]** Criar entidades de domínio puras (`Cliente`, `Fornecedor`) e contratos abstratos de seus repositórios em [src/domain/](src/domain/).
  - [ ] **[Urgência: Média]** Implementar a regra de negócio do cálculo de precificação inteligente sugerida por **Markup** no domínio.
* **Atividades Dependentes**:
  - [ ] **[Urgência: Alta]** Implementar os casos de uso purificados em Python para gerenciamento (CRUD) de Lojas e Produtos (depende da criação das entidades de domínio correspondentes).
  - [ ] **[Urgência: Média]** Implementar os casos de uso purificados em Python para gerenciamento de Clientes e Fornecedores (depende da criação das entidades de domínio correspondentes).

##### 👤 Leonardo (Persistência, Web e Testes)
* **Atividades Independentes**:
  - [ ] **[Urgência: Alta]** Desenvolver os schemas do Pydantic para validação de entrada/saída de Lojas e Produtos em `src/infrastructure/web/schemas/`.
  - [ ] **[Urgência: Média]** Desenvolver os schemas do Pydantic para validação de entrada/saída de Clientes e Fornecedores.
* **Atividades Dependentes**:
  - [ ] **[Urgência: Alta]** Mapear os modelos SQLAlchemy físicos de `lojas` e `produtos` em `models.py` (depende das entidades de domínio criadas por Jonathas).
  - [ ] **[Urgência: Alta]** Gerar e aplicar a migração do Alembic para as tabelas `lojas` e `produtos`.
  - [ ] **[Urgência: Alta]** Implementar repositórios SQLAlchemy concretos para Lojas e Produtos (depende das interfaces abstratas de repositório criadas por Jonathas).
  - [ ] **[Urgência: Alta]** Desenvolver as rotas web do FastAPI de CRUD para Lojas e Produtos (depende dos repositórios de Leonardo e casos de uso de Jonathas).
  - [ ] **[Urgência: Alta]** Escrever testes unitários de validação de schemas Pydantic e testes de integração de API de Lojas/Produtos (depende das rotas FastAPI e requer isolamento de tenant).
  - [ ] **[Urgência: Média]** Mapear os modelos SQLAlchemy físicos de `clientes` e `fornecedores` (depende das entidades de domínio criadas por Jonathas).
  - [ ] **[Urgência: Média]** Gerar e aplicar a migração do Alembic para as tabelas `clientes` e `fornecedores`.
  - [ ] **[Urgência: Média]** Implementar repositórios SQLAlchemy concretos para Clientes e Fornecedores (depende das interfaces abstratas de repositório criadas por Jonathas).
  - [ ] **[Urgência: Média]** Desenvolver as rotas web do FastAPI de CRUD para Clientes e Fornecedores (depende dos repositórios de Leonardo e casos de uso de Jonathas).
  - [ ] **[Urgência: Média]** Escrever testes de integração de API para Clientes/Fornecedores (depende das rotas FastAPI e inclui validação de limite de crédito).

---

### 🩸 Onda 3: O Coração do Estoque (Ledger & Concorrência)
*Objetivo: Construir a lógica de inventário blindada contra concorrência e falhas de quantidade física.*

- [ ] Criação da tabela de saldos (`estoque_saldos`) e ledger de histórico (`estoque_movimentacoes`).
- [ ] Caso de uso: Entrada de estoque simples e controle de saldo.
- [ ] Implementação do **Bloqueio Pessimista (`SELECT FOR UPDATE`)** nas transações de estoque.
- [ ] Caso de uso: Entrada rápida de estoque através do **Upload e parsing de XML de NF-e**.
- [ ] Testes de concorrência: simulação de requisições simultâneas forçando condições de corrida.

---

### 🚚 Onda 4: Transferências Logísticas e Auditoria Física
*Objetivo: Controlar o trânsito de produtos interlojas e gerenciar contagens rotativas.*

- [ ] Máquina de Estados de Transferência (`SOLICITADO`, `DESPACHADO`, `RECEBIDO`, `DIVERGENTE`).
- [ ] Fluxo de auditoria de divergências e justificativas logísticas.
- [ ] Caso de uso: Auditoria física de estoque (inventário local) com registro automático de perdas.
- [ ] Testes de transição de estados de transferência de estoque.

---

### 💰 Onda 5: Faturamento Administrativo, Financeiro e CRM
*Objetivo: Permitir vendas na retaguarda e integrar com fluxo de caixa e contas a pagar/receber.*

- [ ] Lógica de **Venda Administrativa** (formas de pagamento, descontos e itens de venda).
- [ ] Integração de Caixa: Geração automática de `FinanceiroLancamento` (receita) na finalização de vendas.
- [ ] Regra de Crediário: Incremento de `saldo_devedor_crediario` no cliente se a venda for no crediário.
- [ ] Controle manual de despesas operacionais da loja.
- [ ] Testes de fluxo financeiro completo de ponta a ponta.

---

### 📊 Onda 6: Analytics, Relatórios e Celery Workers
*Objetivo: Gerar inteligência de negócio e enviar fechamentos automáticos.*

- [ ] Endpoints analíticos do Dashboard (Ticket Médio, Faturamento vs Custo, Estoque Crítico/Rupturas).
- [ ] Endpoint da **Curva ABC** de produtos mais lucrativos.
- [ ] Configuração de tarefas agendadas no Celery/Redis: Relatório diário de faturamento por e-mail para donos.

---

### 🖥️ Onda 7: Frontend React (Interface SPA)
*Objetivo: Construir a interface do usuário responsiva e dinâmica.*

- [ ] Setup do React + Vite + Tailwind CSS.
- [ ] Estrutura de rotas protegidas por Roles do JWT (`ADMIN_SAAS`, `DONO`, `GERENTE`).
- [ ] Telas de Login e Configurações de Tenants.
- [ ] Telas de CRUDs (Produtos, Lojas, Funcionários, Clientes, Fornecedores).
- [ ] Painel de Estoque Multiloja e Tela de Transferências.
- [ ] Painel Financeiro e Dashboards analíticos com gráficos interativos.
