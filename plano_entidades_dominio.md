# Plano Técnico: Criação das Entidades de Domínio Puras (Tenant e Usuario)

Para iniciarmos o desenvolvimento de forma calma e controlada, focaremos exclusivamente na criação das duas primeiras entidades de domínio na pasta [src/domain/entities/](file:///C:/Users/jonat/Documents/projeto-gerenciamento-saas/src/domain/entities/).

Elas serão implementadas usando **Python puro** com a biblioteca padrão `dataclasses`, livres de qualquer dependência externa (como SQLAlchemy ou FastAPI).

---

## 1. Estrutura de Arquivos a Serem Criados
* [src/domain/entities/tenant.py](file:///C:/Users/jonat/Documents/projeto-gerenciamento-saas/src/domain/entities/tenant.py) - Entidade pura `Tenant`.
* [src/domain/entities/usuario.py](file:///C:/Users/jonat/Documents/projeto-gerenciamento-saas/src/domain/entities/usuario.py) - Entidade pura `Usuario`.

---

## 2. Proposta de Design das Entidades

### Entidade: `Tenant`
Armazena e valida os dados básicos de uma empresa cliente contratante do SaaS.
* **Atributos**:
  * `id: UUID` (Identificador único).
  * `nome_fantasia: str` (Nome comercial).
  * `razao_social: str` (Razão social oficial).
  * `cnpj: str` (CNPJ - apenas números).
  * `data_cadastro: datetime` (Data de cadastro no sistema).
* **Validações de Domínio (executadas no `__post_init__`)**:
  * O CNPJ deve ser limpo (apenas números) e ter exatamente 14 dígitos.
  * Os campos `nome_fantasia` e `razao_social` não podem ser vazios.

### Entidade: `Usuario`
Mapeia os colaboradores que acessam o sistema, vinculados a um tenant específico.
* **Atributos**:
  * `id: UUID` (Identificador único).
  * `tenant_id: UUID` (Vínculo obrigatório com o Tenant).
  * `loja_atribuida_id: Optional[UUID]` (Filial física atribuída - opcional).
  * `nome: str` (Nome completo).
  * `email: str` (E-mail de acesso).
  * `senha_hash: str` (A senha criptografada).
  * `role: str` (Nível de acesso: `ADMIN_SAAS`, `DONO` ou `GERENTE`).
* **Validações de Domínio (executadas no `__post_init__`)**:
  * O `role` deve obrigatoriamente ser um dos três perfis permitidos.
  * O `email` deve conter um formato básico de e-mail válido (contendo `@` e `.`).
  * O `nome` não pode ser vazio.

---

## 3. Estratégia de Validação e Testes Unitários

Para garantir que as regras destas entidades funcionem como esperado, criaremos testes unitários focados na validação dos campos:
* **Testes de Sucesso**

* **Testes de Erro**: Tentar criar um Tenant com CNPJ contendo 13 dígitos ou letras, ou criar um Usuário com um perfil inválido (ex: "ATENDENTE"), garantindo que o Python lance uma exceção controlada (`ValueError`).
