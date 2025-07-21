"""
API Service Layer
Handles business logic for API endpoints.
"""

import logging
from typing import List, Dict, Any

class APIService:
    """Service for API business logic."""

    def __init__(self):
        self.logger = logging.getLogger("APIService")
        self.opportunities = [
            {"id": 1, "title": "IAC Space Competition", "description": "International event for space proposals."},
            {"id": 2, "title": "NASA SBIR", "description": "Small Business Innovation Research grants."}
        ]
        self.proposals = []
        self.logger.info("APIService initialized.")

    def get_opportunities(self) -> List[Dict[str, Any]]:
        """Fetch available opportunities."""
        self.logger.info("Fetching opportunities.")
        return self.opportunities

    def submit_proposal(self, proposal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit a proposal."""
        if not proposal_data.get("title") or not proposal_data.get("content"):
            self.logger.error("Invalid proposal data: %s", proposal_data)
            return {"error": "Invalid proposal data"}
        proposal_data["id"] = len(self.proposals) + 1
        self.proposals.append(proposal_data)
        self.logger.info("Proposal submitted: %s", proposal_data)
        return proposal_data
