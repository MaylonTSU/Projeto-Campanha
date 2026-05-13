import uuid

from sqlalchemy.orm import Session

from app.models.message import Message
from app.schemas.message import MessageCreate


def create_message(db: Session, campaign_lead_id: uuid.UUID, data: MessageCreate) -> Message:
    msg = Message(
        campaign_lead_id=campaign_lead_id,
        canal=data.canal,
        conteudo=data.conteudo,
        assunto=data.assunto,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


def list_messages_by_campaign_lead(
    db: Session, campaign_lead_id: uuid.UUID
) -> list[Message]:
    return (
        db.query(Message)
        .filter(Message.campaign_lead_id == campaign_lead_id)
        .order_by(Message.created_at)
        .all()
    )
