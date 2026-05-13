import uuid

from sqlalchemy.orm import Session

from app.models.campaign_lead import CampaignLead
from app.models.lead import LeadStatus


def get_campaign_stats(db: Session, campaign_id: uuid.UUID) -> dict:
    campaign_leads = (
        db.query(CampaignLead)
        .filter(CampaignLead.campaign_id == campaign_id)
        .all()
    )

    total_leads = len(campaign_leads)
    total_conversoes = sum(1 for cl in campaign_leads if cl.status == LeadStatus.convertido)
    taxa_conversao = round(total_conversoes / total_leads * 100, 2) if total_leads > 0 else 0.0

    distribuicao_status: dict[str, int] = {}
    for status in LeadStatus:
        distribuicao_status[status.value] = 0
    for cl in campaign_leads:
        distribuicao_status[cl.status.value] += 1

    return {
        "total_leads": total_leads,
        "total_conversoes": total_conversoes,
        "taxa_conversao": taxa_conversao,
        "distribuicao_status": distribuicao_status,
    }
