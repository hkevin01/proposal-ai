# Source Code Organization Summary

## New Directory Structure

The `src/` directory has been reorganized into logical subfolders for better maintainability:

```
src/
├── __init__.py
├── main.py                 # Main entry point
├── core/                   # Core functionality
│   ├── __init__.py
│   ├── config.py          # Configuration management
│   ├── database.py        # Database operations
│   └── schema_phase1.py   # Database schemas
├── gui/                    # User interface components
│   ├── __init__.py
│   ├── gui.py             # Main GUI application
│   ├── enhanced_gui_tab.py # Enhanced discovery tab
│   ├── proposal_editor_gui.py # Proposal editor
│   └── donor_gui.py       # Donor management interface
├── discovery/              # Opportunity discovery
│   ├── __init__.py
│   ├── discovery_engine.py # Basic discovery engine
│   ├── enhanced_discovery_engine.py # Advanced discovery
│   └── api_integrations.py # External API integrations
├── donors/                 # Donor management
│   ├── __init__.py
│   ├── donor_database.py  # Donor database operations
│   ├── donor_enhanced_discovery.py # Donor discovery
│   └── donor_integration_demo.py # Demo functionality
├── proposals/              # Proposal generation
│   ├── __init__.py
│   ├── ai_proposal_generator.py # AI-powered proposal generation
│   └── resume_parser.py   # Resume parsing for profiles
├── monitoring/             # System monitoring
│   ├── __init__.py
│   ├── opportunity_monitor.py # Real-time monitoring
│   └── analytics_dashboard.py # Analytics and reporting
└── utils/                  # Utilities and helpers
    ├── __init__.py
    └── sample_data.py     # Sample data generation
```

## Benefits of New Structure

1. **Logical Grouping**: Related functionality is grouped together
2. **Clear Separation**: Core, GUI, and business logic are separated
3. **Scalability**: Easy to add new features within existing categories
4. **Maintainability**: Easier to find and maintain specific functionality
5. **Module Independence**: Each subfolder can be developed independently

## Import Path Updates

With the new structure, imports use relative paths:
- `from ..core.config import MAIN_DATABASE_PATH`
- `from ..donors.donor_database import DonorDatabase`
- `from ..discovery.api_integrations import APIIntegrationManager`

## Running the Application

The main entry point remains the same:
```bash
# From project root
python -m src.main

# Or run GUI directly
python -m src.gui.gui
```

## Development Guidelines

1. **Core Module**: Contains fundamental system components
2. **GUI Module**: All user interface code goes here
3. **Discovery Module**: Opportunity finding and API integrations
4. **Donors Module**: Everything related to donor management
5. **Proposals Module**: AI generation and proposal management
6. **Monitoring Module**: Analytics, monitoring, and reporting
7. **Utils Module**: Shared utilities and helper functions

This organization makes the codebase more professional and easier to navigate for both development and maintenance.
