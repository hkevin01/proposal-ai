"""
Configuration module for Proposal AI
Handles file paths and configurations
"""

import os

# Get the project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Define standard paths
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
CONFIG_DIR = os.path.join(PROJECT_ROOT, "config")
DOCS_DIR = os.path.join(PROJECT_ROOT, "docs")
TESTS_DIR = os.path.join(PROJECT_ROOT, "tests")

# Database paths
MAIN_DATABASE_PATH = os.path.join(DATA_DIR, "proposal_ai.db")
OPPORTUNITIES_DATABASE_PATH = os.path.join(DATA_DIR, "opportunities.db")
DONORS_DATABASE_PATH = os.path.join(DATA_DIR, "donors.db")

# Configuration file paths
MONITORING_CONFIG_PATH = os.path.join(CONFIG_DIR, "monitoring_config.json")
DONOR_CONFIG_PATH = os.path.join(CONFIG_DIR, "donor_config.json")
ANALYTICS_REPORT_PATH = os.path.join(CONFIG_DIR, "analytics_report.json")

# Create directories if they don't exist
for directory in [DATA_DIR, CONFIG_DIR]:
    os.makedirs(directory, exist_ok=True)


def get_database_path(db_name: str = "proposal_ai.db") -> str:
    """Get the full path for a database file in the data directory"""
    return os.path.join(DATA_DIR, db_name)


def get_config_path(config_name: str) -> str:
    """Get the full path for a config file in the config directory"""
    return os.path.join(CONFIG_DIR, config_name)


def get_data_path(data_name: str) -> str:
    """Get the full path for a data file in the data directory"""
    return os.path.join(DATA_DIR, data_name)
