import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.campaign import CampaignStatus


class CampaignCreate(BaseModel):
    nome: str
    descricao: str | None = None
    nicho: str | None = None
    data_inicio: datetime | None = None
    data_fim: datetime | None = None


class CampaignStatusUpdate(BaseModel):
    status: CampaignStatus


class CampaignResponse(BaseModel):
    id: uuid.UUID
    nome: str
    descricao: str | None
    nicho: str | None
    status: CampaignStatus
    data_inicio: datetime | None
    data_fim: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
