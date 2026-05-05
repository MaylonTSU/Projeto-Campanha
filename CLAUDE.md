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