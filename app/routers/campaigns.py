import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.campaign import CampaignCreate, CampaignResponse, CampaignStatusUpdate
from app.services import campaign as campaign_service

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


@router.post("/", response_model=CampaignResponse, status_code=201)
def create_campaign(data: CampaignCreate, db: Session = Depends(get_db)):
    return campaign_service.create_campaign(db, data)


@router.get("/", response_model=list[CampaignResponse])
def list_campaigns(db: Session = Depends(get_db)):
    return campaign_service.list_campaigns(db)


@router.get("/{campaign_id}", response_model=CampaignResponse)
def get_campaign(campaign_id: uuid.UUID, db: Session = Depends(get_db)):
    campaign = campaign_service.get_campaign(db, campaign_id)
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campanha não encontrada")
    return campaign


@router.patch("/{campaign_id}/status", response_model=CampaignResponse)
def update_campaign_status(
    campaign_id: uuid.UUID, data: CampaignStatusUpdate, db: Session = Depends(get_db)
):
    campaign = campaign_service.update_campaign_status(db, campaign_id, data.status)
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campanha não encontrada")
    return campaign
