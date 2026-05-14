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
Dia 7 — Deploy concluído. Projeto entregue.
37/37 testes passando. 14 endpoints funcionando em produção.
Endpoints: campaigns (4), leads (3), campaign-leads (4), messages (2), analytics (1).
Mensagens vinculadas a campaign_lead_id (canal: email/whatsapp/sms, status: pendente por padrão).
Analytics retorna total_leads, total_conversoes, taxa_conversao e distribuicao_status por campanha.
Deploy: Railway + Supabase PostgreSQL.
Código no GitHub: MaylonTSU/Projeto-Campanha (branch main).
API em produção: https://web-production-dd3b.up.railway.app
Documentação: https://web-production-dd3b.up.railway.app/docs

## Próximo passo
Projeto MVP entregue. Possíveis evoluções futuras:
- Autenticação (JWT)
- Agendamento de campanhas
- Integração real com canais (email/WhatsApp/SMS)
- Dashboard front-end para o Dr. Hailton

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
- SSL com Supabase no Railway: usar NullPool + connect_args={"sslmode": "require"}
  para conexões PostgreSQL; SQLite mantém check_same_thread: False para testes
- Supabase com Railway: conexão direta usa IPv6 — Railway não suporta.
  Solução: usar Transaction Pooler (aws-1-us-west-2.pooler.supabase.com:6543)
  URL format: postgresql://postgres.PROJECT_ID:SENHA@aws-1-us-west-2.pooler.supabase.com:6543/postgres