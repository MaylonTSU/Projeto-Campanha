from fastapi import FastAPI

from app.routers.campaign_leads import router as campaign_leads_router
from app.routers.campaigns import router as campaigns_router
from app.routers.leads import router as leads_router

app = FastAPI(title="Gerenciador de Campanhas")

app.include_router(campaigns_router)
app.include_router(leads_router)
app.include_router(campaign_leads_router)


@app.get("/health")
def health():
    return {"status": "ok"}
