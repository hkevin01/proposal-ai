# Web & Mobile API Implementation
from fastapi import FastAPI, HTTPException
from src.services.api_service import APIService
from src.services.notification_service import NotificationService
from src.services.analytics_service import AnalyticsService
from pydantic import BaseModel

app = FastAPI()
api_service = APIService()

class ProposalData(BaseModel):
    """Pydantic model for proposal data."""
    title: str
    content: str

@app.get("/opportunities")
def get_opportunities():
    """Get all available opportunities."""
    return api_service.get_opportunities()

@app.post("/proposals")
def submit_proposal(proposal_data: ProposalData):
    """Submit a new proposal."""
    return api_service.submit_proposal(proposal_data.dict())

@app.get("/cli/opportunities")
def cli_get_opportunities():
    try:
        return api_service.get_opportunities()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
