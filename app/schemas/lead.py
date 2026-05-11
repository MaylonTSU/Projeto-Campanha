import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.models.lead import LeadStatus


class LeadCreate(BaseModel):
    nome: str
    email: EmailStr
    telefone: str | None = None
    dados_extras: dict | None = None


class LeadFunnelUpdate(BaseModel):
    status: LeadStatus


class LeadResponse(BaseModel):
    id: uuid.UUID
    nome: str
    email: str
    telefone: str | None
    dados_extras: dict | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
