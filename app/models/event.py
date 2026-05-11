import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, JSON, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class EventTipo(str, enum.Enum):
    abertura = "abertura"
    clique = "clique"
    resposta = "resposta"
    conversao = "conversao"
    descadastro = "descadastro"


class Event(Base):
    __tablename__ = "events"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    campaign_lead_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("campaign_leads.id", ondelete="CASCADE"), nullable=False
    )
    message_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("messages.id", ondelete="SET NULL"), nullable=True
    )
    tipo: Mapped[EventTipo] = mapped_column(Enum(EventTipo), nullable=False, index=True)
    dados: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    campaign_lead: Mapped["CampaignLead"] = relationship("CampaignLead", back_populates="events")
    message: Mapped["Message | None"] = relationship("Message", back_populates="events")
