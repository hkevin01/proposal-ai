# Phase 15: Documentation Expansion

## Goals
- Expand API documentation and usage examples
- Add developer guides for new modules
- Update README with new features and usage instructions

## API Usage Example
```python
import requests
response = requests.get('http://localhost:8000/opportunities')
print(response.json())
```

## GUI Usage Example
```python
from src.gui.gui import MainWindow

if __name__ == "__main__":
    # Launch the Proposal AI GUI
    window = MainWindow()
    window.show()
```

## CLI Usage Example
```python
from src.api.web_api import api_service

if __name__ == "__main__":
    # List all opportunities from CLI
    print(api_service.get_opportunities())
```

## Developer Guide
- Service Layer: See `src/services/`
- Error Handling: See `src/utils/error_handling.py`
- Config Encryption: See `src/utils/config_encryption.py`

## Mobile/Web API Integration
- Endpoints available via FastAPI in `src/api/web_api.py`
- Example: `/opportunities`, `/proposals`
- See API docs for request/response formats

## Next Steps
- Add more usage examples for GUI and CLI
- Document integration points for mobile/web API
