import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, UniqueConstraint, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.lead import LeadStatus


class CampaignLead(Base):
    __tablename__ = "campaign_leads"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False
    )
    lead_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("leads.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[LeadStatus] = mapped_column(
        Enum(LeadStatus), nullable=False, default=LeadStatus.novo
    )
    entrada_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (UniqueConstraint("campaign_id", "lead_id", name="uq_campaign_lead"),)

    campaign: Mapped["Campaign"] = relationship("Campaign", back_populates="campaign_leads")
    lead: Mapped["Lead"] = relationship("Lead", back_populates="campaign_leads")
    messages: Mapped[list["Message"]] = relationship("Message", back_populates="campaign_lead")
    events: Mapped[list["Event"]] = relationship("Event", back_populates="campaign_lead")
