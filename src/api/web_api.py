# Web & Mobile API Implementation
from fastapi import FastAPI, HTTPException
from src.services.api_service import APIService
from src.services.notification_service import NotificationService
from src.services.analytics_service import AnalyticsService
from pydantic import BaseModel
from src.community.collaboration import CollaborationManager
from src.utils.export import export_proposal_pdf, export_analytics_docx
import tempfile

app = FastAPI()
api_service = APIService()
collab_manager = CollaborationManager()
analytics_service = AnalyticsService()

class ProposalData(BaseModel):
    """Pydantic model for proposal data."""
    title: str
    content: str

class ShareRequest(BaseModel):
    proposal_id: int
    team: str

class CommentRequest(BaseModel):
    proposal_id: int
    comment: str

class TeamRequest(BaseModel):
    team_name: str
    members: list

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

@app.post("/collaboration/share")
def share_proposal(req: ShareRequest):
    return {"success": collab_manager.share_proposal(req.proposal_id, req.team)}

@app.post("/collaboration/comment")
def add_comment(req: CommentRequest):
    return {"success": collab_manager.add_comment(req.proposal_id, req.comment)}

@app.post("/collaboration/team")
def create_team(req: TeamRequest):
    return {"success": collab_manager.create_team(req.team_name, req.members)}

@app.get("/analytics/dashboard")
def get_dashboard():
    """Get analytics dashboard data."""
    return analytics_service.get_dashboard_data()

@app.get("/analytics/statistics")
def get_statistics():
    """Get advanced analytics statistics."""
    return analytics_service.get_statistics()

@app.post("/analytics/report")
def generate_report(params: dict):
    """Generate analytics report."""
    return {"report": analytics_service.generate_report(params)}

@app.post("/export/proposal/pdf")
def export_proposal_pdf_api(proposal: dict):
    """Export proposal to PDF and return filename."""
    filename = tempfile.mktemp(suffix=".pdf")
    export_proposal_pdf(proposal, filename)
    return {"filename": filename}

@app.post("/export/analytics/docx")
def export_analytics_docx_api(analytics: dict):
    """Export analytics to DOCX and return filename."""
    filename = tempfile.mktemp(suffix=".docx")
    export_analytics_docx(analytics, filename)
    return {"filename": filename}

@app.post("/analytics/custom")
def custom_analytics_query(query: dict):
    """Run a custom analytics query (filtering, aggregation)."""
    # Example: filter proposal counts above a threshold
    threshold = query.get("proposal_count_threshold", 0)
    stats = analytics_service.get_statistics()
    filtered = [x for x in stats["proposal_counts"] if x > threshold]
    return {"filtered_proposal_counts": filtered}
