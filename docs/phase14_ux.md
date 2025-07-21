# Phase 14: Enhanced User Experience

## Goals
- Improve GUI responsiveness and accessibility
- Add onboarding/help dialogs

## Implementation
- Onboarding dialog stub in `src/gui/gui.py`

## Export API Usage Example
```python
import requests
# Export proposal to PDF
requests.post('http://localhost:8000/export/proposal/pdf', json={"title": "Test", "content": "Sample"})
# Export analytics to DOCX
requests.post('http://localhost:8000/export/analytics/docx', json={"total_proposals": 10})
```

## Export GUI Usage Example
```python
window.export_proposal({"title": "Test", "content": "Sample"}, "test_proposal.pdf")
window.export_analytics({"total_proposals": 10}, "analytics_report.docx")
```
