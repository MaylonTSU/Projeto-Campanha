import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.campaign_lead import CampaignLeadWithLeadResponse
from app.schemas.lead import LeadCreate, LeadResponse
from app.services import campaign as campaign_service
from app.services import lead as lead_service

router = APIRouter(tags=["leads"])


@router.post("/campaigns/{campaign_id}/leads", response_model=LeadResponse, status_code=201)
def create_lead(campaign_id: uuid.UUID, data: LeadCreate, db: Session = Depends(get_db)):
    campaign = campaign_service.get_campaign(db, campaign_id)
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campanha não encontrada")
    return lead_service.create_lead(db, campaign_id, data)


@router.get("/campaigns/{campaign_id}/leads", response_model=list[CampaignLeadWithLeadResponse])
def list_leads(campaign_id: uuid.UUID, db: Session = Depends(get_db)):
    campaign = campaign_service.get_campaign(db, campaign_id)
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campanha não encontrada")
    return lead_service.list_leads_with_status(db, campaign_id)


@router.get("/leads/{lead_id}", response_model=LeadResponse)
def get_lead(lead_id: uuid.UUID, db: Session = Depends(get_db)):
    lead = lead_service.get_lead(db, lead_id)
    if lead is None:
        raise HTTPException(status_code=404, detail="Lead não encontrado")
    return lead
