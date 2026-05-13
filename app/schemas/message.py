import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.message import MessageCanal, MessageStatus


class MessageCreate(BaseModel):
    canal: MessageCanal
    conteudo: str
    assunto: str | None = None


class MessageResponse(BaseModel):
    id: uuid.UUID
    campaign_lead_id: uuid.UUID
    canal: MessageCanal
    assunto: str | None
    conteudo: str
    status: MessageStatus
    enviada_em: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}
