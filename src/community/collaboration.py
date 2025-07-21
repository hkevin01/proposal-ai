"""
Collaboration and Community Sharing Module for Proposal AI.
"""
import logging
from typing import List, Dict

class CollaborationManager:
    """Manage sharing, commenting, and team collaboration for proposals."""
    def __init__(self):
        self.logger = logging.getLogger("CollaborationManager")
        self.shared_proposals: List[Dict] = []
        self.comments: Dict[int, List[str]] = {}
        self.teams: Dict[str, List[str]] = {}
        self.logger.info("CollaborationManager initialized.")

    def share_proposal(self, proposal_id: int, team: str) -> bool:
        self.logger.info("Sharing proposal %d with team %s", proposal_id, team)
        self.shared_proposals.append({"proposal_id": proposal_id, "team": team})
        return True

    def add_comment(self, proposal_id: int, comment: str) -> bool:
        self.logger.info("Adding comment to proposal %d: %s", proposal_id, comment)
        if proposal_id not in self.comments:
            self.comments[proposal_id] = []
        self.comments[proposal_id].append(comment)
        return True

    def create_team(self, team_name: str, members: List[str]) -> bool:
        self.logger.info("Creating team %s with members %s", team_name, members)
        self.teams[team_name] = members
        return True
