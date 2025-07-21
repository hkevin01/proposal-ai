# Phase 18: Data Import & Integration

## Goals
- Import proposals and opportunities from CSV, Excel, and APIs
- Centralize import source configuration
- Integrate imported data into analytics

## Schema Validation
Import configuration must include:
- csv_paths: list
- excel_paths: list
- api_endpoints: list

## Usage Examples
```python
from src.services.analytics_service import AnalyticsService
service = AnalyticsService(import_config={
    "csv_paths": ["data/proposals.csv"],
    "excel_paths": ["data/proposals.xlsx"],
    "api_endpoints": ["https://api.example.com/proposals"]
})
assert service.import_manager.validate_config()
```
