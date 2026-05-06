import uuid

from sqlalchemy.orm import Session

from app.models.campaign import Campaign, CampaignStatus
from app.schemas.campaign import CampaignCreate


def create_campaign(db: Session, data: CampaignCreate) -> Campaign:
    campaign = Campaign(**data.model_dump())
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    return campaign


def list_campaigns(db: Session) -> list[Campaign]:
    return db.query(Campaign).all()


def get_campaign(db: Session, campaign_id: uuid.UUID) -> Campaign | None:
    return db.query(Campaign).filter(Campaign.id == campaign_id).first()


def update_campaign_status(
    db: Session, campaign_id: uuid.UUID, status: CampaignStatus
) -> Campaign | None:
    campaign = get_campaign(db, campaign_id)
    if campaign is None:
        return None
    campaign.status = status
    db.commit()
    db.refresh(campaign)
    return campaign
