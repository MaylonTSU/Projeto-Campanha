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
def campaign_id(client):
    res = client.post("/campaigns/", json={"nome": "Campanha Analytics"})
    assert res.status_code == 201
    return res.json()["id"]


def _enroll_lead(client, campaign_id: str, nome: str, email: str) -> str:
    lead = client.post(
        f"/campaigns/{campaign_id}/leads",
        json={"nome": nome, "email": email},
    )
    lead_id = lead.json()["id"]
    res = client.get(f"/campaigns/{campaign_id}/leads")
    cl = next(item for item in res.json() if item["lead_id"] == lead_id)
    return cl["campaign_lead_id"]


def test_stats_campanha_vazia(client):
    camp = client.post("/campaigns/", json={"nome": "Campanha Vazia"})
    cid = camp.json()["id"]
    response = client.get(f"/campaigns/{cid}/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total_leads"] == 0
    assert data["total_conversoes"] == 0
    assert data["taxa_conversao"] == 0.0
    assert isinstance(data["distribuicao_status"], dict)


def test_stats_com_leads(client, campaign_id):
    cl1 = _enroll_lead(client, campaign_id, "Lead A", "a@email.com")
    cl2 = _enroll_lead(client, campaign_id, "Lead B", "b@email.com")
    cl3 = _enroll_lead(client, campaign_id, "Lead C", "c@email.com")

    client.patch(f"/campaign-leads/{cl2}/status", json={"status": "convertido"})
    client.patch(f"/campaign-leads/{cl3}/status", json={"status": "qualificado"})

    response = client.get(f"/campaigns/{campaign_id}/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total_leads"] == 3
    assert data["total_conversoes"] == 1
    assert data["taxa_conversao"] == round(1 / 3 * 100, 2)
    assert data["distribuicao_status"]["convertido"] == 1
    assert data["distribuicao_status"]["qualificado"] == 1
    assert data["distribuicao_status"]["novo"] == 1


def test_stats_todos_convertidos(client):
    camp = client.post("/campaigns/", json={"nome": "Campanha 100%"})
    cid = camp.json()["id"]
    cl1 = _enroll_lead(client, cid, "Lead X", "x@email.com")
    cl2 = _enroll_lead(client, cid, "Lead Y", "y@email.com")
    client.patch(f"/campaign-leads/{cl1}/status", json={"status": "convertido"})
    client.patch(f"/campaign-leads/{cl2}/status", json={"status": "convertido"})

    response = client.get(f"/campaigns/{cid}/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total_leads"] == 2
    assert data["total_conversoes"] == 2
    assert data["taxa_conversao"] == 100.0


def test_stats_campanha_not_found(client):
    response = client.get(f"/campaigns/{uuid.uuid4()}/stats")
    assert response.status_code == 404
    assert response.json()["detail"] == "Campanha não encontrada"
