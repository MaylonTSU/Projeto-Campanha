import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.campaign_lead import CampaignLeadResponse, CampaignLeadStatusUpdate
from app.services import campaign as campaign_service
from app.services import campaign_lead as campaign_lead_service

router = APIRouter(tags=["campaign-leads"])


@router.post(
    "/campaigns/{campaign_id}/leads/{lead_id}/enroll",
    response_model=CampaignLeadResponse,
    status_code=201,
)
def enroll_lead(
    campaign_id: uuid.UUID, lead_id: uuid.UUID, db: Session = Depends(get_db)
):
    campaign = campaign_service.get_campaign(db, campaign_id)
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campanha não encontrada")
    return campaign_lead_service.create_campaign_lead(db, campaign_id, lead_id)


@router.get(
    "/campaigns/{campaign_id}/campaign-leads",
    response_model=list[CampaignLeadResponse],
)
def list_campaign_leads(campaign_id: uuid.UUID, db: Session = Depends(get_db)):
    campaign = campaign_service.get_campaign(db, campaign_id)
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campanha não encontrada")
    return campaign_lead_service.list_campaign_leads(db, campaign_id)


@router.get("/campaign-leads/{campaign_lead_id}", response_model=CampaignLeadResponse)
def get_campaign_lead(campaign_lead_id: uuid.UUID, db: Session = Depends(get_db)):
    cl = campaign_lead_service.get_campaign_lead(db, campaign_lead_id)
    if cl is None:
        raise HTTPException(status_code=404, detail="Participação não encontrada")
    return cl


@router.patch(
    "/campaign-leads/{campaign_lead_id}/status",
    response_model=CampaignLeadResponse,
)
def update_campaign_lead_status(
    campaign_lead_id: uuid.UUID,
    data: CampaignLeadStatusUpdate,
    db: Session = Depends(get_db),
):
    cl = campaign_lead_service.update_campaign_lead_status(db, campaign_lead_id, data.status)
    if cl is None:
        raise HTTPException(status_code=404, detail="Participação não encontrada")
    return cl
