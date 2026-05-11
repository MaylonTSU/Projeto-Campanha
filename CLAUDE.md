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

## Estrutura de pastas
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
- Commits pequenos e descritivos
- Nunca commitar arquivo .env
- Rodar os testes antes de cada commit

## Decisões arquiteturais tomadas
- Workflow fixo para o MVP (não agente autônomo)
- Português para nomes de variáveis de negócio, inglês para código
- Relação N para N entre leads e campaigns via tabela campaign_leads
- leads é tabela independente — sem campaign_id direto
- messages e events apontam para campaign_lead_id, não para lead_id

## Status atual
Dia 4 — Concluído.
27/27 testes passando.
Endpoints: campaigns (4), leads com funil (4).
Evento registrado automaticamente a cada movimentação de funil.

## Em andamento
Refatoração do modelo de dados para N para N (leads ↔ campaigns).
Etapa atual: 6 de 6 — Testes.

Etapas concluídas:
1. CampaignLead criado, campaign_id removido de Lead, Message e Event
   atualizados para campaign_lead_id.
2. Migration gerada e aplicada no Supabase (alembic upgrade head).
3. Schemas atualizados: campaign_lead.py criado (CampaignLeadCreate,
   CampaignLeadResponse, CampaignLeadStatusUpdate,
   CampaignLeadWithLeadResponse); LeadResponse sem campaign_id e status.
4. Services atualizados: campaign_lead.py criado (create, get, list,
   update_status); lead.py reescrito — create_lead usa transação Lead +
   CampaignLead + Event; list_leads_with_status adicionado com joinedload.
5. Routers atualizados: campaign_leads.py criado (enroll, list, get,
   update_status); leads.py atualizado — GET /leads retorna
   CampaignLeadWithLeadResponse, /funnel removido; main.py registra
   campaign_leads router.

## Próximo passo
Etapa 6 — Reescrever testes para cobrir o novo modelo N para N.

## Hurdles documentados
- Windows venv bloqueado: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`
- Alembic autogenerate vazio: importar modelos no env.py com `import app.models`
- UUID PostgreSQL quebra testes SQLite: usar `sqlalchemy.Uuid` genérico
- database.py precisa de fallback SQLite: `os.environ.get("DATABASE_URL", "sqlite:///:memory:")`
- pycache no git: `git rm -r --cached __pycache__`
- SQLite em memória com FastAPI: usar `StaticPool` no engine de teste
- Importar `app.models` antes de `Base.metadata.create_all` nos testes
- .env exposto: `git filter-branch --force` + trocar senha imediatamente
- EmailStr requer: `pip install 'pydantic[email]'`
- Débito técnico: EventTipo.abertura usado para transições de funil —
  criar EventTipo.mudanca_status no futuro
- sa.Enum com create_type=False não evita CREATE TYPE no op.create_table:
  usar postgresql.ENUM (from sqlalchemy.dialects import postgresql) que
  respeita create_type=False de forma confiável