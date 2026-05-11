import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class MessageCanal(str, enum.Enum):
    email = "email"
    whatsapp = "whatsapp"
    sms = "sms"


class MessageStatus(str, enum.Enum):
    pendente = "pendente"
    enviada = "enviada"
    entregue = "entregue"
    falhou = "falhou"


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    campaign_lead_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("campaign_leads.id", ondelete="CASCADE"), nullable=False
    )
    canal: Mapped[MessageCanal] = mapped_column(Enum(MessageCanal), nullable=False)
    assunto: Mapped[str | None] = mapped_column(String(255), nullable=True)
    conteudo: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[MessageStatus] = mapped_column(
        Enum(MessageStatus), nullable=False, default=MessageStatus.pendente
    )
    enviada_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    campaign_lead: Mapped["CampaignLead"] = relationship("CampaignLead", back_populates="messages")
    events: Mapped[list["Event"]] = relationship("Event", back_populates="message")
