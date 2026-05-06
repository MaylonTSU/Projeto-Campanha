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


def test_create_campaign(client):
    response = client.post("/campaigns/", json={"nome": "Campanha Saúde", "nicho": "saúde"})
    assert response.status_code == 201
    data = response.json()
    assert data["nome"] == "Campanha Saúde"
    assert data["nicho"] == "saúde"
    assert data["status"] == "rascunho"
    assert "id" in data


def test_create_campaign_minimal(client):
    response = client.post("/campaigns/", json={"nome": "Só o Nome"})
    assert response.status_code == 201
    data = response.json()
    assert data["descricao"] is None
    assert data["nicho"] is None


def test_list_campaigns(client):
    response = client.get("/campaigns/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_get_campaign(client):
    create_res = client.post("/campaigns/", json={"nome": "Campanha Get"})
    campaign_id = create_res.json()["id"]

    response = client.get(f"/campaigns/{campaign_id}")
    assert response.status_code == 200
    assert response.json()["id"] == campaign_id
    assert response.json()["nome"] == "Campanha Get"


def test_get_campaign_not_found(client):
    response = client.get(f"/campaigns/{uuid.uuid4()}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Campanha não encontrada"


def test_update_campaign_status(client):
    create_res = client.post("/campaigns/", json={"nome": "Campanha Status"})
    campaign_id = create_res.json()["id"]

    response = client.patch(f"/campaigns/{campaign_id}/status", json={"status": "ativa"})
    assert response.status_code == 200
    assert response.json()["status"] == "ativa"


def test_update_campaign_status_invalid(client):
    create_res = client.post("/campaigns/", json={"nome": "Campanha Inválida"})
    campaign_id = create_res.json()["id"]

    response = client.patch(f"/campaigns/{campaign_id}/status", json={"status": "inexistente"})
    assert response.status_code == 422


def test_update_campaign_status_not_found(client):
    response = client.patch(
        f"/campaigns/{uuid.uuid4()}/status", json={"status": "ativa"}
    )
    assert response.status_code == 404
