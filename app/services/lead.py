import uuid

from sqlalchemy.orm import Session

from app.models.event import Event, EventTipo
from app.models.lead import Lead, LeadStatus
from app.schemas.lead import LeadCreate


def create_lead(db: Session, campaign_id: uuid.UUID, data: LeadCreate) -> Lead:
    lead = Lead(campaign_id=campaign_id, **data.model_dump())
    db.add(lead)
    db.flush()
    event = Event(
        campaign_id=campaign_id,
        lead_id=lead.id,
        tipo=EventTipo.abertura,
        dados={"etapa": LeadStatus.novo.value},
    )
    db.add(event)
    db.commit()
    db.refresh(lead)
    return lead


def list_leads_by_campaign(db: Session, campaign_id: uuid.UUID) -> list[Lead]:
    return db.query(Lead).filter(Lead.campaign_id == campaign_id).all()


def get_lead(db: Session, lead_id: uuid.UUID) -> Lead | None:
    return db.query(Lead).filter(Lead.id == lead_id).first()


def update_lead_funnel_stage(
    db: Session, lead_id: uuid.UUID, novo_status: LeadStatus
) -> Lead | None:
    lead = get_lead(db, lead_id)
    if lead is None:
        return None
    status_anterior = lead.status
    lead.status = novo_status
    db.flush()
    event = Event(
        campaign_id=lead.campaign_id,
        lead_id=lead.id,
        tipo=EventTipo.resposta,
        dados={"de": status_anterior.value, "para": novo_status.value},
    )
    db.add(event)
    db.commit()
    db.refresh(lead)
    return lead
