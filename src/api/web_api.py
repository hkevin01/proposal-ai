# Web & Mobile API Implementation
from fastapi import FastAPI, HTTPException
from src.services.api_service import APIService
from src.services.notification_service import NotificationService
from src.services.analytics_service import AnalyticsService
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from src.community.collaboration import CollaborationManager
from src.utils.export import export_proposal_pdf, export_analytics_docx
import tempfile

app = FastAPI()
api_service = APIService()
collab_manager = CollaborationManager()
analytics_service = AnalyticsService(user_role="admin")

router = APIRouter()

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

@router.get("/analytics/custom")
def custom_analytics_query(filters: dict = Query(None)):
    """API endpoint for custom analytics queries with filters."""
    service = AnalyticsService(user_role="viewer")
    return service.get_interactive_dashboard(filters)

@router.get("/analytics/export")
def export_analytics_chart(chart_type: str = "bar", filename: str = "chart.png"):
    """API endpoint to export analytics chart."""
    service = AnalyticsService(user_role="editor")
    success = service.export_dashboard_chart(chart_type, filename)
    return {"success": success, "filename": filename}

@router.post("/analytics/import")
def import_analytics_data(source_type: str, path_or_url: str, user_role: str = "viewer"):
    service = AnalyticsService(user_role=user_role)
    try:
        data = service.import_external_data(source_type, path_or_url)
        return {"status": "success", "imported": len(data)}
    except PermissionError:
        raise HTTPException(status_code=403, detail="Permission denied.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/realtime")
def get_realtime_analytics():
    # Example: return latest dashboard data
    return analytics_service.get_dashboard_data()

@router.get("/analytics/drilldown")
def get_drilldown_analytics():
    """API endpoint for drill-down analytics."""
    service = AnalyticsService(user_role="viewer")
    stats = service.get_statistics()
    # Example: return opportunity counts by index
    return {"drilldown": stats["opportunity_counts"]}
