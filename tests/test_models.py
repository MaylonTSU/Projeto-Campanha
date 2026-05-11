import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import (
    Campaign,
    CampaignLead,
    CampaignStatus,
    Event,
    EventTipo,
    Lead,
    LeadStatus,
    Message,
    MessageCanal,
    MessageStatus,
)


@pytest.fixture(scope="module")
def db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)


def test_campaign_defaults(db):
    campaign = Campaign(nome="Campanha Teste", nicho="saúde")
    db.add(campaign)
    db.commit()
    db.refresh(campaign)

    assert isinstance(campaign.id, uuid.UUID)
    assert campaign.status == CampaignStatus.rascunho
    assert campaign.descricao is None
    assert campaign.data_inicio is None


def test_lead_defaults(db):
    campaign = db.query(Campaign).first()
    lead = Lead(nome="João Silva", email="joao@example.com")
    db.add(lead)
    db.flush()
    cl = CampaignLead(campaign_id=campaign.id, lead_id=lead.id)
    db.add(cl)
    db.commit()
    db.refresh(lead)
    db.refresh(cl)

    assert isinstance(lead.id, uuid.UUID)
    assert cl.status == LeadStatus.novo
    assert lead.telefone is None
    assert lead.dados_extras is None


def test_message_defaults(db):
    cl = db.query(CampaignLead).first()
    message = Message(
        campaign_lead_id=cl.id,
        canal=MessageCanal.email,
        conteudo="Olá, temos uma oferta especial para você!",
    )
    db.add(message)
    db.commit()
    db.refresh(message)

    assert isinstance(message.id, uuid.UUID)
    assert message.status == MessageStatus.pendente
    assert message.assunto is None
    assert message.enviada_em is None


def test_event_creation(db):
    cl = db.query(CampaignLead).first()
    message = db.query(Message).first()
    event = Event(
        campaign_lead_id=cl.id,
        message_id=message.id,
        tipo=EventTipo.abertura,
        dados={"ip": "192.168.0.1"},
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    assert isinstance(event.id, uuid.UUID)
    assert event.tipo == EventTipo.abertura
    assert event.dados["ip"] == "192.168.0.1"


def test_campaign_status_enum():
    assert list(CampaignStatus) == ["rascunho", "ativa", "pausada", "concluida", "cancelada"]


def test_lead_status_enum():
    assert list(LeadStatus) == ["novo", "contatado", "qualificado", "convertido", "descartado"]


def test_message_status_enum():
    assert list(MessageStatus) == ["pendente", "enviada", "entregue", "falhou"]


def test_event_tipo_enum():
    assert list(EventTipo) == ["abertura", "clique", "resposta", "conversao", "descadastro"]
