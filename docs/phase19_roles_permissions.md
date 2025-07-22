# Phase 19: Roles & Permissions

## Goals
- Implement user roles (admin, analyst, viewer)
- Add permissions for analytics, import, and export actions
- Integrate role checks in GUI and API

## Planned Features
- Role-based access control for analytics dashboard
- Permission checks for data import/export
- Admin-only configuration management

## Integration Notes
- Use RolesService for permission checks in analytics and import actions
- Use RealtimeAnalytics to notify dashboard of data changes

## Usage Example
```python
# Example role check
if user.role == "admin":
    service.import_external_data(...)
else:
    raise PermissionError("Only admins can import data.")

from src.services.analytics_service import AnalyticsService
service = AnalyticsService(user_role="admin")
service.import_external_data("csv", "data/proposals.csv")  # Allowed
service.user_role = "viewer"
try:
    service.import_external_data("csv", "data/proposals.csv")  # Raises PermissionError
except PermissionError:
    print("Permission denied.")
```
