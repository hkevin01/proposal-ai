"""
Analytics Service Layer
Handles business logic for analytics and reporting.
"""

import logging
from typing import Dict, Any, List, Optional
import random
from src.utils.data_import import (
    import_from_csv,
    import_from_excel,
    import_from_api,
    DataImportManager
)

class AnalyticsService:
    """
    Service for analytics and reporting.
    Provides dashboard data, report generation, statistics, and data import integration.
    """

    def __init__(self, import_config: Optional[Dict[str, Any]] = None):
        self.logger = logging.getLogger("AnalyticsService")
        self.logger.info("AnalyticsService initialized.")
        self.analytics_data = {
            "total_proposals": 10,
            "total_opportunities": 5,
            "proposal_success_rate": 0.7,
            "top_opportunities": ["IAC Space Competition", "NASA SBIR"]
        }
        self.import_manager = DataImportManager(import_config or {})

    def get_dashboard_data(self) -> Dict[str, Any]:
        """
        Aggregate dashboard data, handle missing data edge cases.
        """
        try:
            self.logger.info("Aggregating dashboard data.")
            data = self.analytics_data.copy()
            if data["total_proposals"] == 0:
                data["proposal_success_rate"] = 0.0
                data["top_opportunities"] = []
            return data
        except KeyError as e:
            self.logger.error("Missing key in dashboard data: %s", e)
            return {}
        except Exception as e:
            self.logger.error("Error aggregating dashboard data: %s", e)
            return {}

    def generate_report(self, params: Dict[str, Any]) -> str:
        """
        Generate analytics report, handle missing params edge cases.
        """
        try:
            self.logger.info("Generating report with params: %s", params)
            if not params or not isinstance(params, dict):
                return "Error: Invalid report parameters."
            score = random.uniform(0, 1)
            summary = params.get("type", "summary")
            return f"Report type: {summary}, score: {score:.2f}"
        except Exception as e:
            self.logger.error("Error generating report: %s", e)
            return "Error generating report."

    def get_statistics(self) -> Dict[str, Any]:
        """
        Return advanced statistics, handle edge cases.
        """
        try:
            stats = {
                "proposal_counts": [random.randint(1, 10) for _ in range(5)],
                "opportunity_counts": [random.randint(1, 5) for _ in range(5)],
                "success_rates": [random.uniform(0.5, 1.0) for _ in range(5)]
            }
            if all(x == 0 for x in stats["proposal_counts"]):
                stats["success_rates"] = [0.0 for _ in range(5)]
            self.logger.info("Returning advanced statistics.")
            return stats
        except KeyError as e:
            self.logger.error("Missing key in statistics: %s", e)
            return {}
        except Exception as e:
            self.logger.error("Error getting statistics: %s", e)
            return {}

    def import_external_data(self, source_type: str, path_or_url: str) -> List[Dict[str, Any]]:
        """
        Import external data into analytics service.
        """
        try:
            if source_type == "csv":
                data = import_from_csv(path_or_url)
            elif source_type == "excel":
                data = import_from_excel(path_or_url)
            elif source_type == "api":
                data = import_from_api(path_or_url)
            else:
                self.logger.error(
                    "Unknown import source type: %s", source_type
                )
                return []
            self.logger.info(
                "Imported %d records from %s source.", len(data), source_type
            )
            return data
        except Exception as e:
            self.logger.error("Error importing external data: %s", e)
            return []

    def import_all_sources(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Import data from all configured sources using DataImportManager.
        """
        try:
            results = self.import_manager.import_all()
            self.logger.info(
                "Imported data from all sources: %s", list(results.keys())
            )
            return results
        except Exception as e:
            self.logger.error("Error importing all sources: %s", e)
            return {}

    def validate_environment(self) -> bool:
        """
        Validate required packages and configuration for analytics service.
        """
        try:
            import pandas
            import requests
        except ImportError as e:
            self.logger.error("Missing required package: %s", e.name)
            return False
        if not hasattr(self, "import_manager") or self.import_manager is None:
            self.logger.error("DataImportManager is not initialized.")
            return False
        self.logger.info("Environment validation passed.")
        return True
