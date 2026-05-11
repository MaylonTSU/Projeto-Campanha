import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, JSON, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class LeadStatus(str, enum.Enum):
    novo = "novo"
    contatado = "contatado"
    qualificado = "qualificado"
    convertido = "convertido"
    descartado = "descartado"


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    telefone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    dados_extras: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    campaign_leads: Mapped[list["CampaignLead"]] = relationship("CampaignLead", back_populates="lead")
