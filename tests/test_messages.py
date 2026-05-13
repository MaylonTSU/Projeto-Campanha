import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.database import Base, get_db
from app.main import app


@pytest.fixture(scope="module")
def client():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)


@pytest.fixture(scope="module")
def campaign_lead_id(client):
    camp = client.post("/campaigns/", json={"nome": "Campanha Msg"})
    assert camp.status_code == 201
    campaign_id = camp.json()["id"]

    lead = client.post(
        f"/campaigns/{campaign_id}/leads",
        json={"nome": "Lead Msg", "email": "leadmsg@email.com"},
    )
    assert lead.status_code == 201
    lead_id = lead.json()["id"]

    res = client.get(f"/campaigns/{campaign_id}/leads")
    cl = next(item for item in res.json() if item["lead_id"] == lead_id)
    return cl["campaign_lead_id"]


def test_create_message_email(client, campaign_lead_id):
    response = client.post(
        f"/campaign-leads/{campaign_lead_id}/messages",
        json={
            "canal": "email",
            "conteudo": "Olá, tudo bem?",
            "assunto": "Primeiro contato",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["canal"] == "email"
    assert data["assunto"] == "Primeiro contato"
    assert data["conteudo"] == "Olá, tudo bem?"
    assert data["status"] == "pendente"
    assert data["campaign_lead_id"] == campaign_lead_id


def test_create_message_whatsapp_sem_assunto(client, campaign_lead_id):
    response = client.post(
        f"/campaign-leads/{campaign_lead_id}/messages",
        json={"canal": "whatsapp", "conteudo": "Oi! Vi que você se cadastrou."},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["canal"] == "whatsapp"
    assert data["assunto"] is None


def test_create_message_campaign_lead_not_found(client):
    response = client.post(
        f"/campaign-leads/{uuid.uuid4()}/messages",
        json={"canal": "sms", "conteudo": "Mensagem fantasma"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Participação não encontrada"


def test_create_message_canal_invalido(client, campaign_lead_id):
    response = client.post(
        f"/campaign-leads/{campaign_lead_id}/messages",
        json={"canal": "telegram", "conteudo": "Canal inválido"},
    )
    assert response.status_code == 422


def test_list_messages(client, campaign_lead_id):
    response = client.get(f"/campaign-leads/{campaign_lead_id}/messages")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2
    assert data[0]["canal"] in ("email", "whatsapp", "sms")


def test_list_messages_campaign_lead_not_found(client):
    response = client.get(f"/campaign-leads/{uuid.uuid4()}/messages")
    assert response.status_code == 404
    assert response.json()["detail"] == "Participação não encontrada"
