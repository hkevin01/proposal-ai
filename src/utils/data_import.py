"""
Data Import Utility
Supports importing proposals/opportunities from CSV, Excel, and APIs.
"""
import pandas as pd
import requests
from typing import List, Dict, Any, Optional


def import_from_csv(path: str) -> List[Dict[str, Any]]:
    """Import data from a CSV file."""
    df = pd.read_csv(path)
    return df.to_dict(orient="records")


def import_from_excel(path: str) -> List[Dict[str, Any]]:
    """Import data from an Excel file."""
    df = pd.read_excel(path)
    return df.to_dict(orient="records")


def import_from_api(url: str, timeout: Optional[int] = 10) -> List[Dict[str, Any]]:
    """Import data from a REST API endpoint."""
    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()
    return resp.json()


def validate_import_config(config: Dict[str, Any]) -> bool:
    """Validate import source config against required schema."""
    if not isinstance(config, dict):
        return False
    for source in config.get("sources", []):
        required = source.get("schema", {}).get("required_fields", [])
        for field in required:
            if field not in source:
                return False
    return True


class DataImportManager:
    """
    Manages multiple data import sources and provides unified import interface.
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def validate_config(self) -> bool:
        """
        Validate the manager's import configuration.
        """
        return validate_import_config(self.config)

    def import_all(self) -> Dict[str, List[Dict[str, Any]]]:
        """Import data from all configured sources."""
        results = {}
        for path in self.config.get("csv_paths", []):
            results[path] = import_from_csv(path)
        for path in self.config.get("excel_paths", []):
            results[path] = import_from_excel(path)
        for url in self.config.get("api_endpoints", []):
            results[url] = import_from_api(url)
        return results
