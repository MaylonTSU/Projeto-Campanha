import uuid

from sqlalchemy.orm import Session

from app.models.campaign_lead import CampaignLead
from app.models.event import Event, EventTipo
from app.models.lead import LeadStatus


def create_campaign_lead(
    db: Session, campaign_id: uuid.UUID, lead_id: uuid.UUID
) -> CampaignLead:
    try:
        cl = CampaignLead(campaign_id=campaign_id, lead_id=lead_id)
        db.add(cl)
        db.flush()
        event = Event(
            campaign_lead_id=cl.id,
            tipo=EventTipo.abertura,
            dados={"etapa": LeadStatus.novo.value},
        )
        db.add(event)
        db.commit()
        db.refresh(cl)
        return cl
    except Exception:
        db.rollback()
        raise


def get_campaign_lead(db: Session, campaign_lead_id: uuid.UUID) -> CampaignLead | None:
    return db.query(CampaignLead).filter(CampaignLead.id == campaign_lead_id).first()


def list_campaign_leads(db: Session, campaign_id: uuid.UUID) -> list[CampaignLead]:
    return (
        db.query(CampaignLead)
        .filter(CampaignLead.campaign_id == campaign_id)
        .all()
    )


def update_campaign_lead_status(
    db: Session, campaign_lead_id: uuid.UUID, novo_status: LeadStatus
) -> CampaignLead | None:
    cl = get_campaign_lead(db, campaign_lead_id)
    if cl is None:
        return None
    try:
        status_anterior = cl.status
        cl.status = novo_status
        db.flush()
        event = Event(
            campaign_lead_id=cl.id,
            tipo=EventTipo.abertura,
            dados={"de": status_anterior.value, "para": novo_status.value},
        )
        db.add(event)
        db.commit()
        db.refresh(cl)
        return cl
    except Exception:
        db.rollback()
        raise
