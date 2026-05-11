import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class CampaignStatus(str, enum.Enum):
    rascunho = "rascunho"
    ativa = "ativa"
    pausada = "pausada"
    concluida = "concluida"
    cancelada = "cancelada"


class Campaign(Base):
    __tablename__ = "campaigns"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    nicho: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[CampaignStatus] = mapped_column(
        Enum(CampaignStatus), nullable=False, default=CampaignStatus.rascunho
    )
    data_inicio: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    data_fim: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    campaign_leads: Mapped[list["CampaignLead"]] = relationship("CampaignLead", back_populates="campaign")
