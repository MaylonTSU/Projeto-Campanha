import uuid

from sqlalchemy.orm import Session

from app.models.campaign_lead import CampaignLead
from app.models.event import Event, EventTipo
from app.models.lead import Lead, LeadStatus
from app.schemas.lead import LeadCreate


def create_lead(db: Session, campaign_id: uuid.UUID, data: LeadCreate) -> Lead:
    try:
        lead = Lead(**data.model_dump())
        db.add(lead)
        db.flush()
        cl = CampaignLead(campaign_id=campaign_id, lead_id=lead.id)
        db.add(cl)
        db.flush()
        event = Event(
            campaign_lead_id=cl.id,
            tipo=EventTipo.abertura,
            dados={"etapa": LeadStatus.novo.value},
        )
        db.add(event)
        db.commit()
        db.refresh(lead)
        return lead
    except Exception:
        db.rollback()
        raise


def list_leads_by_campaign(db: Session, campaign_id: uuid.UUID) -> list[Lead]:
    return (
        db.query(Lead)
        .join(CampaignLead, CampaignLead.lead_id == Lead.id)
        .filter(CampaignLead.campaign_id == campaign_id)
        .all()
    )


def list_leads_with_status(db: Session, campaign_id: uuid.UUID) -> list[dict]:
    from sqlalchemy.orm import joinedload
    campaign_leads = (
        db.query(CampaignLead)
        .options(joinedload(CampaignLead.lead))
        .filter(CampaignLead.campaign_id == campaign_id)
        .all()
    )
    return [
        {
            "campaign_lead_id": cl.id,
            "lead_id": cl.lead_id,
            "nome": cl.lead.nome,
            "email": cl.lead.email,
            "telefone": cl.lead.telefone,
            "status": cl.status,
            "entrada_em": cl.entrada_em,
        }
        for cl in campaign_leads
    ]


def get_lead(db: Session, lead_id: uuid.UUID) -> Lead | None:
    return db.query(Lead).filter(Lead.id == lead_id).first()


def update_lead_funnel_stage(
    db: Session, campaign_lead_id: uuid.UUID, novo_status: LeadStatus
) -> CampaignLead | None:
    from app.services.campaign_lead import update_campaign_lead_status
    return update_campaign_lead_status(db, campaign_lead_id, novo_status)
