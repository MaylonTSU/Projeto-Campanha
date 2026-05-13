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
Dia 6 — Mensagens e Analytics concluídos.
37/37 testes passando.
Endpoints: campaigns (4), leads (3), campaign-leads (4), messages (2), analytics (1).
Mensagens vinculadas a campaign_lead_id (canal: email/whatsapp/sms, status: pendente por padrão).
Analytics retorna total_leads, total_conversoes, taxa_conversao e distribuicao_status por campanha.

## Próximo passo
Dia 7 — Deploy e entrega.
- Configurar variáveis de ambiente no Railway
- Testar API em produção
- Documentação básica para o Dr. Hailton

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