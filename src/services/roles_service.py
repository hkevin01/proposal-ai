"""
Roles & Permissions Service
Handles user roles and permission checks for analytics and import actions.
"""
import logging
from typing import Dict, Any

class RolesService:
    """
    Service for managing user roles and permissions.
    """
    def __init__(self):
        self.logger = logging.getLogger("RolesService")
        self.roles = {"admin": ["import", "export", "analytics"], "analyst": ["analytics"], "viewer": []}

    def has_permission(self, user_role: str, action: str) -> bool:
        """Check if the user role has permission for the given action."""
        role_permissions = {
            "admin": ["import", "export", "analytics", "edit", "view"],
            "editor": ["export", "analytics", "edit", "view"],
            "viewer": ["view"]
        }
        return action in role_permissions.get(user_role, [])
