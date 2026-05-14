# CLAUDE.md — Diretrizes Globais de Projeto

> Arquivo de configuração lido automaticamente pelo Claude Code em todo projeto.
> Aplica-se a todos os repositórios. Regras locais em `CLAUDE.local.md` sobrescrevem quando necessário.

---

## 1. IDENTIDADE DO PROJETO

Ao iniciar qualquer sessão, Claude deve identificar o contexto ativo:

```
DOMÍNIO: [SAP-Logistics | Trading-Automation | SaaS-Product]
STACK:    [definido no CLAUDE.local.md do projeto]
FASE:     [discovery | development | refactor | hotfix]
```

Se não encontrar `CLAUDE.local.md`, perguntar ao utilizador antes de avançar.

---

## 2. ECONOMIA DE TOKENS — REGRAS OBRIGATÓRIAS

### 2.1 Comunicação compacta
- Respostas em **bullet points** ou blocos de código — nunca texto narrativo longo
- Sem preâmbulos ("Claro!", "Com certeza!", "Ótima pergunta!")
- Sem resumos no final do que já foi dito
- Confirmar entendimento em **uma linha** antes de executar

### 2.2 Leitura de ficheiros
- Ler apenas ficheiros **explicitamente necessários** para a tarefa
- Nunca ler toda a codebase antes de perguntar o scope
- Preferir leitura por **função/classe específica** em vez de ficheiro inteiro
- Usar `grep` / `find` antes de abrir ficheiros

### 2.3 Geração de código
- Gerar apenas o **diff/bloco alterado**, não o ficheiro inteiro
- Indicar `// ... resto do código inalterado ...` quando aplicável
- Para ficheiros > 200 linhas, mostrar apenas a secção modificada

### 2.4 Iteração
- Máximo **1 pergunta de clarificação** por turno
- Propor solução com assunções explícitas em vez de perguntar múltiplas dúvidas
- Formato de assunção: `[ASSUME: X = Y — confirmar ou corrigir]`

---

## 3. ARQUITETURA DE DESENVOLVIMENTO EM MÓDULOS

### 3.1 Estrutura de diretórios obrigatória

```
project-root/
├── CLAUDE.md              ← este ficheiro (global)
├── CLAUDE.local.md        ← overrides locais (git-ignored)
├── .context/
│   ├── architecture.md    ← diagrama e decisões de arquitetura
│   ├── decisions/         ← ADR (Architecture Decision Records)
│   │   └── ADR-001.md
│   └── glossary.md        ← termos de domínio (SAP/Trading/SaaS)
├── src/
│   ├── modules/           ← cada módulo é independente
│   │   └── <module-name>/
│   │       ├── index.ts
│   │       ├── types.ts
│   │       ├── service.ts
│   │       └── __tests__/
│   ├── shared/            ← código partilhado entre módulos
│   │   ├── utils/
│   │   ├── types/
│   │   └── constants/
│   └── core/              ← infraestrutura (DB, API clients, auth)
├── docs/
│   └── api/
└── scripts/               ← automações e utilitários
```

### 3.2 Princípios de modularidade

**Cada módulo deve:**
- Ter uma única responsabilidade de domínio
- Exportar API pública via `index.ts`
- Não importar de outros módulos diretamente — usar `shared/` ou injeção de dependência
- Conter os seus próprios tipos em `types.ts`
- Ter testes unitários em `__tests__/`

**Claude nunca deve:**
- Criar dependências circulares entre módulos
- Adicionar lógica de negócio em `core/` ou `shared/`
- Misturar camadas (ex: acesso a DB em controladores)

### 3.3 Padrões por domínio

#### SAP Logistics (MM / EWM / SD / ACM)
```
modules/
├── goods-movement/     ← MM: entradas, saídas, transferências
├── warehouse-ops/      ← EWM: tarefas, bins, stock
├── sales-processing/   ← SD: ordens, entregas, faturas
├── catch-weight/       ← ACM: gestão de peso variável
└── integration/        ← IDocs, BAPIs, RFCs
```

#### Trading Automation
```
modules/
├── market-data/        ← feeds, normalização, cache
├── strategy-engine/    ← lógica de sinais, backtesting
├── order-management/   ← execução, gestão de posições
├── risk-control/       ← stop-loss, exposure, drawdown
└── reporting/          ← P&L, métricas, dashboards
```

#### SaaS Product / AI Automation
```
modules/
├── auth/               ← autenticação, autorização, tenancy
├── ai-pipeline/        ← prompts, agentes, orquestração
├── integrations/       ← conectores externos (SAP, XTB, etc.)
├── billing/            ← planos, uso, webhooks
└── analytics/          ← eventos, funis, retenção
```

---

## 4. REGRAS DE REPOSITÓRIO E CONTROLO DE VERSÃO

### 4.1 Branches
```
main          ← produção (protegida, só via PR)
develop       ← integração contínua
feature/xxx   ← novas funcionalidades
fix/xxx       ← correções de bugs
hotfix/xxx    ← correções urgentes em produção
refactor/xxx  ← melhorias sem mudança de comportamento
```

### 4.2 Convenção de commits (Conventional Commits)
```
feat(module):     nova funcionalidade
fix(module):      correção de bug
refactor(module): refatoração sem mudança de comportamento
test(module):     adição/alteração de testes
docs(module):     documentação
chore:            tarefas de manutenção (deps, config)
perf(module):     melhoria de performance

Exemplos:
feat(warehouse-ops): add bin replenishment trigger
fix(risk-control): correct drawdown calculation on overnight gaps
docs(auth): update SSO integration guide
```

### 4.3 Pull Requests
- Título = mensagem do commit principal
- Descrição obrigatória: **O quê**, **Porquê**, **Como testar**
- Máximo **400 linhas** por PR (exceto scaffolding inicial)
- Associar a issue/ticket quando existir

### 4.4 `.gitignore` obrigatório
```
CLAUDE.local.md
.env
.env.*
*.local
node_modules/
dist/
build/
.DS_Store
__pycache__/
*.pyc
.context/secrets/
```

---

## 5. GESTÃO DE CONTEXTO ENTRE SESSÕES

### 5.1 Ficheiro `.context/architecture.md`
Claude deve **ler este ficheiro primeiro** em cada sessão nova.
Formato mínimo:
```markdown
# Arquitetura — [Nome do Projeto]
**Stack:** ...
**Decisões chave:** ...
**Estado atual:** ...
**Próximos passos:** ...
**Restrições:** ...
```

### 5.2 ADR — Architecture Decision Records
Para cada decisão técnica relevante, criar ficheiro em `.context/decisions/`:
```markdown
# ADR-XXX: [Título]
**Data:** YYYY-MM-DD
**Estado:** proposed | accepted | deprecated
**Contexto:** Por que esta decisão foi necessária
**Decisão:** O que foi decidido
**Consequências:** Trade-offs e impactos
```

### 5.3 Glossário de domínio
Manter `.context/glossary.md` com termos específicos:
- Abreviações SAP (GR, GI, TO, TR, HU...)
- Termos de trading (SL, TP, drawdown, spread...)
- Acrónimos do produto SaaS

---

## 6. QUALIDADE E TESTES

### 6.1 Cobertura mínima
| Tipo | Mínimo |
|------|--------|
| Unitários (lógica de negócio) | 80% |
| Integração (APIs, módulos) | 60% |
| E2E (fluxos críticos) | Fluxos happy-path cobertos |

### 6.2 Antes de propor código, Claude deve verificar
- [ ] Existe tipo/interface para os dados manipulados?
- [ ] A função tem mais de uma responsabilidade? → dividir
- [ ] Há side effects não declarados?
- [ ] O erro é tratado ou propagado explicitamente?
- [ ] Existe teste para o caso de falha?

### 6.3 Code review checklist (para PRs)
```
[ ] Segue estrutura de módulos definida
[ ] Sem imports cruzados entre módulos
[ ] Tipos definidos (sem `any` não justificado)
[ ] Testes adicionados/atualizados
[ ] Sem secrets em código
[ ] Commit message no formato correto
[ ] CLAUDE.local.md atualizado se arquitetura mudou
```

---

## 7. SEGURANÇA E DADOS SENSÍVEIS

- **Nunca** colocar credenciais, API keys ou passwords em código
- Usar variáveis de ambiente — documentar em `.env.example`
- Dados de clientes/posições de trading: apenas em ambientes isolados
- Logs nunca devem conter PII ou dados financeiros completos
- Conexões SAP: RFC destinations geridas externamente ao código

---

## 8. INSTRUÇÕES PARA CLAUDE EM CADA SESSÃO

### Ao iniciar uma tarefa, Claude deve:
1. Confirmar domínio ativo (SAP / Trading / SaaS)
2. Ler `.context/architecture.md` se existir
3. Identificar módulo(s) afetado(s)
4. Declarar assunções em `[ASSUME: ...]` antes de codificar
5. Propor abordagem em **máximo 5 bullets** antes de implementar

### Claude nunca deve:
- Alterar ficheiros fora do scope declarado
- Refatorar código não relacionado com a tarefa
- Instalar dependências sem aprovação explícita
- Tomar decisões de arquitetura sem criar ADR

### Formato de resposta padrão:
```
SCOPE: [módulo(s) afetado(s)]
ABORDAGEM: [1-3 bullets]
[ASSUME: x = y]
--- código ---
PRÓXIMO PASSO: [ação recomendada]
```

---

## 9. OVERRIDES LOCAIS — CLAUDE.local.md

Este ficheiro **não é versionado** e sobrescreve qualquer regra acima para o projeto específico.

Template mínimo:
```markdown
# CLAUDE.local.md — [Nome do Projeto]

## Stack
- Runtime: Node 20 / Python 3.12 / ABAP
- Framework: ...
- DB: ...

## Módulos ativos
- [ ] módulo-a
- [ ] módulo-b

## Restrições específicas
- ...

## Estado atual
- Última sessão: YYYY-MM-DD
- Em progresso: ...
- Bloqueadores: ...
```

---

*Versão: 1.0 | Atualizar conforme projetos evoluem*
