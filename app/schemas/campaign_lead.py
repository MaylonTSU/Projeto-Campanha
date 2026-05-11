import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.lead import LeadStatus


class CampaignLeadCreate(BaseModel):
    campaign_id: uuid.UUID
    lead_id: uuid.UUID


class CampaignLeadResponse(BaseModel):
    id: uuid.UUID
    campaign_id: uuid.UUID
    lead_id: uuid.UUID
    status: LeadStatus
    entrada_em: datetime

    model_config = {"from_attributes": True}


class CampaignLeadStatusUpdate(BaseModel):
    status: LeadStatus


class CampaignLeadWithLeadResponse(BaseModel):
    campaign_lead_id: uuid.UUID
    lead_id: uuid.UUID
    nome: str
    email: str
    telefone: str | None
    status: LeadStatus
    entrada_em: datetime

    model_config = {"from_attributes": True}
