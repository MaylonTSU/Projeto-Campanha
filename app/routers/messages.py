import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.message import MessageCreate, MessageResponse
from app.services import campaign_lead as campaign_lead_service
from app.services import message as message_service

router = APIRouter(tags=["messages"])


@router.post(
    "/campaign-leads/{campaign_lead_id}/messages",
    response_model=MessageResponse,
    status_code=201,
)
def create_message(
    campaign_lead_id: uuid.UUID,
    data: MessageCreate,
    db: Session = Depends(get_db),
):
    cl = campaign_lead_service.get_campaign_lead(db, campaign_lead_id)
    if cl is None:
        raise HTTPException(status_code=404, detail="Participação não encontrada")
    return message_service.create_message(db, campaign_lead_id, data)


@router.get(
    "/campaign-leads/{campaign_lead_id}/messages",
    response_model=list[MessageResponse],
)
def list_messages(campaign_lead_id: uuid.UUID, db: Session = Depends(get_db)):
    cl = campaign_lead_service.get_campaign_lead(db, campaign_lead_id)
    if cl is None:
        raise HTTPException(status_code=404, detail="Participação não encontrada")
    return message_service.list_messages_by_campaign_lead(db, campaign_lead_id)
