# Gerenciador de Campanhas — Dr. Hailton

## O que é esse projeto
Módulo plugável de campanhas de marketing para agentes de IA.
Permite criar, executar e acompanhar campanhas em diferentes nichos.
Projeto real para cliente. Prazo: 7 dias. Deploy: Railway.

## Stack
- Python 3.13
- FastAPI (API REST)
- SQLAlchemy (ORM)
- PostgreSQL via Supabase
- Railway (deploy)
- pytest (testes)

## Padrão arquitetural
Orchestrator-Workers.
O Campaign Engine é o orquestrador central.
Workers: Campaign, Audience, Message, Funnel, Analytics.

## Estrutura de pastas esperada
app/
main.py
database.py
models/
routers/
services/
schemas/
tests/
.env.example
requirements.txt

## Convenções obrigatórias
- Todo endpoint novo precisa ter teste correspondente em tests/
- Commits pequenos e descritivos (ex: "Add campaign create endpoint")
- Nunca commitar arquivo .env
- Rodar os testes antes de cada commit

## Status atual
Dia 1 — Setup inicial. Projeto vazio.

## Decisões tomadas
- Workflow fixo para o MVP (não agente autônomo)
- Português para nomes de variáveis de negócio, inglês para código

## Common Hurdles

### Windows: ativar venv bloqueado por política de execução
**Erro:** `venv\Scripts\activate` falha com PSSecurityException
**Solução:** Rodar antes: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

## Status atual
Dia 1 — Concluído.
Estrutura criada, FastAPI rodando, health endpoint funcionando.
Dois commits no GitHub. .gitignore configurado.

## Status atual
Dia 2 — Concluído.
4 tabelas criadas no Supabase: campaigns, leads, messages, events.
Modelos SQLAlchemy com relacionamentos e enums.
8/8 testes passando. Repositório limpo no GitHub.

## Hurdles encontrados
- Alembic autogenerate vazio: modelos precisam ser importados no env.py com `import app.models`
- UUID PostgreSQL-específico quebra testes SQLite: usar `sqlalchemy.Uuid` genérico
- database.py precisou de fallback SQLite para testes rodarem sem .env
- pycache commitado: usar `git rm -r --cached` para remover do rastreamento

## Status atual
Dia 3 — Concluído.
CRUD de campanhas implementado com 4 endpoints e 8 testes.
16/16 testes passando.

## Hurdles encontrados
- SQLite :memory: com pool de conexões: usar `StaticPool` no engine de teste
- Modelos precisam ser importados antes de `Base.metadata.create_all`: adicionar `import app.models` no topo do test_campaigns.py

## Próximo passo
Dia 4 — Funil e eventos.
Criar endpoints para leads e movimentação no funil.