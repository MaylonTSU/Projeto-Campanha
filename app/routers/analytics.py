import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import analytics as analytics_service
from app.services import campaign as campaign_service

router = APIRouter(tags=["analytics"])


@router.get("/campaigns/{campaign_id}/stats")
def get_campaign_stats(campaign_id: uuid.UUID, db: Session = Depends(get_db)):
    campaign = campaign_service.get_campaign(db, campaign_id)
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campanha não encontrada")
    return analytics_service.get_campaign_stats(db, campaign_id)
