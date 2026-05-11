import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401 — registra todos os models no Base.metadata
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
def campaign_id(client):
    res = client.post("/campaigns/", json={"nome": "Campanha Leads"})
    assert res.status_code == 201
    return res.json()["id"]


def _get_campaign_lead_id(client, campaign_id: str, lead_id: str) -> str:
    res = client.get(f"/campaigns/{campaign_id}/leads")
    return next(cl["campaign_lead_id"] for cl in res.json() if cl["lead_id"] == lead_id)


def test_create_lead(client, campaign_id):
    response = client.post(
        f"/campaigns/{campaign_id}/leads",
        json={"nome": "João Silva", "email": "joao@email.com", "telefone": "11999990000"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["nome"] == "João Silva"
    assert data["email"] == "joao@email.com"
    assert "id" in data


def test_create_lead_campaign_not_found(client):
    response = client.post(
        f"/campaigns/{uuid.uuid4()}/leads",
        json={"nome": "Lead Fantasma", "email": "fantasma@email.com"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Campanha não encontrada"


def test_create_lead_invalid_email(client, campaign_id):
    response = client.post(
        f"/campaigns/{campaign_id}/leads",
        json={"nome": "Email Errado", "email": "nao-e-email"},
    )
    assert response.status_code == 422


def test_list_leads(client, campaign_id):
    response = client.get(f"/campaigns/{campaign_id}/leads")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert "campaign_lead_id" in data[0]
    assert "status" in data[0]
    assert "nome" in data[0]


def test_list_leads_campaign_not_found(client):
    response = client.get(f"/campaigns/{uuid.uuid4()}/leads")
    assert response.status_code == 404


def test_get_lead(client, campaign_id):
    create_res = client.post(
        f"/campaigns/{campaign_id}/leads",
        json={"nome": "Maria Souza", "email": "maria@email.com"},
    )
    lead_id = create_res.json()["id"]

    response = client.get(f"/leads/{lead_id}")
    assert response.status_code == 200
    assert response.json()["id"] == lead_id
    assert response.json()["nome"] == "Maria Souza"


def test_get_lead_not_found(client):
    response = client.get(f"/leads/{uuid.uuid4()}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Lead não encontrado"


def test_update_lead_funnel(client, campaign_id):
    create_res = client.post(
        f"/campaigns/{campaign_id}/leads",
        json={"nome": "Carlos Funil", "email": "carlos@email.com"},
    )
    lead_id = create_res.json()["id"]
    campaign_lead_id = _get_campaign_lead_id(client, campaign_id, lead_id)

    response = client.patch(
        f"/campaign-leads/{campaign_lead_id}/status", json={"status": "contatado"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "contatado"


def test_update_lead_funnel_to_convertido(client, campaign_id):
    create_res = client.post(
        f"/campaigns/{campaign_id}/leads",
        json={"nome": "Ana Convertida", "email": "ana@email.com"},
    )
    lead_id = create_res.json()["id"]
    campaign_lead_id = _get_campaign_lead_id(client, campaign_id, lead_id)

    response = client.patch(
        f"/campaign-leads/{campaign_lead_id}/status", json={"status": "convertido"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "convertido"


def test_update_lead_funnel_invalid_status(client, campaign_id):
    create_res = client.post(
        f"/campaigns/{campaign_id}/leads",
        json={"nome": "Lead Inválido", "email": "invalido@email.com"},
    )
    lead_id = create_res.json()["id"]
    campaign_lead_id = _get_campaign_lead_id(client, campaign_id, lead_id)

    response = client.patch(
        f"/campaign-leads/{campaign_lead_id}/status", json={"status": "status_inexistente"}
    )
    assert response.status_code == 422


def test_update_lead_funnel_not_found(client):
    response = client.patch(
        f"/campaign-leads/{uuid.uuid4()}/status", json={"status": "qualificado"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Participação não encontrada"
