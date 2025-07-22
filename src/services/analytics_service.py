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
from src.services.roles_service import RolesService
from src.analytics.realtime_analytics import RealtimeAnalytics  # noqa: F401
from src.analytics.filters import (
    filter_by_min_proposals,
    filter_by_success_rate
)


class AnalyticsService:
    """
    Service for analytics and reporting.
    Provides dashboard data, report generation,
    statistics, and data import integration.
    """

    def __init__(self,
                 import_config: Optional[Dict[str, Any]] = None,
                 user_role: str = "viewer"):
        """
        Initialize the AnalyticsService.
        Args:
            import_config: Optional configuration for data import sources.
            user_role: Role of the current user (default: "viewer").
        """
        self.logger = logging.getLogger("AnalyticsService")
        self.logger.info("AnalyticsService initialized.")
        self.analytics_data = {
            "total_proposals": 10,
            "total_opportunities": 5,
            "proposal_success_rate": 0.7,
            "top_opportunities": [
                "IAC Space Competition",
                "NASA SBIR"
            ]
        }
        self.import_manager = DataImportManager(import_config or {})
        self.roles_service = RolesService()
        self.user_role = user_role
        self.realtime = RealtimeAnalytics()

    def _validate_dashboard_data(self, data: Dict[str, Any]) -> bool:
        """Validate dashboard data structure and values."""
        required_keys = [
            "total_proposals",
            "total_opportunities",
            "proposal_success_rate",
            "top_opportunities"
        ]
        for key in required_keys:
            if key not in data:
                self.logger.error(f"Missing key in dashboard data: {key}")
                return False
        if not isinstance(data["top_opportunities"], list):
            self.logger.error("top_opportunities must be a list.")
            return False
        return True

    def get_dashboard_data(self) -> Dict[str, Any]:
        """
        Aggregate dashboard data, handle missing data edge cases.
        Returns:
            dict: Aggregated dashboard data.
        """
        try:
            self.logger.info("Aggregating dashboard data.")
            data = self.analytics_data.copy()
            if data["total_proposals"] == 0:
                data["proposal_success_rate"] = 0.0
                data["top_opportunities"] = []
            if not self._validate_dashboard_data(data):
                return {}
            return data
        except (ValueError, KeyError) as exc:
            self.logger.error("Error in dashboard data: %s", exc)
            return {}
        except Exception as exc:
            self.logger.error("Error in dashboard data: %s", exc)
            return {}

    def generate_report(self, params: Dict[str, Any]) -> str:
        """
        Generate analytics report, handle missing params edge cases.
        Args:
            params: Parameters for report generation.
        Returns:
            str: Report summary or error message.
        """
        try:
            self.logger.info("Generating report with params: %s", params)
            if not params or not isinstance(params, dict):
                return "Error: Invalid report parameters."
            score = random.uniform(0, 1)
            summary = params.get("type", "summary")
            return f"Report type: {summary}, score: {score:.2f}"
        except (ValueError, KeyError) as exc:
            self.logger.error("Error generating report: %s", exc)
            return "Error generating report."
        except Exception as exc:
            self.logger.error("Error generating report: %s", exc)
            return "Error generating report."

    def generate_detailed_report(
        self,
        output_dir: str = "analytics_reports"
    ) -> str:
        """Generate a detailed analytics report and save visualizations."""
        from src.analytics.analytics_report import generate_report
        data = self.get_statistics()
        return generate_report(data, output_dir)

    def get_statistics(self) -> Dict[str, Any]:
        """
        Return advanced statistics, handle edge cases.
        Returns:
            dict: Statistics data.
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
        except (ValueError, KeyError) as exc:
            self.logger.error("Error in analytics calculation: %s", exc)
            return {}
        except Exception as exc:
            self.logger.error("Error in donor analytics: %s", exc)
            return {}

    def load_external_data(
        self,
        source_type: str,
        path_or_url: str
    ) -> List[Dict[str, Any]]:
        """
        Import external data into analytics service with role check.
        Args:
            source_type: Type of source ("csv", "excel", "api").
            path_or_url: Path or URL to import from.
        Returns:
            list: Imported data records.
        Raises:
            PermissionError: If user does not have import permission.
        """
        if not self.roles_service.has_permission(self.user_role, "import"):
            self.logger.error("Permission denied for import action.")
            raise PermissionError("User does not have import permission.")
        try:
            if source_type == "csv":
                data = import_from_csv(path_or_url)
            elif source_type == "excel":
                data = import_from_excel(path_or_url)
            elif source_type == "api":
                data = import_from_api(path_or_url)
            else:
                self.logger.error(
                    "Unknown import source type: %s",
                    source_type
                )
                return []
            self.logger.info(
                "Imported %d records from %s source.",
                len(data), source_type
            )
            return data
        except (IOError, OSError) as exc:
            self.logger.error("Error loading external data: %s", exc)
            return []
        except Exception as exc:
            self.logger.error("Error loading external data: %s", exc)
            return []

    def import_all_sources(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Import data from all configured sources using DataImportManager.
        Returns:
            dict: All imported data grouped by source.
        """
        try:
            results = self.import_manager.import_all()
            self.logger.info(
                "Imported data from all sources: %s",
                list(results.keys())
            )
            return results
        except (IOError, OSError) as exc:
            self.logger.error("Error importing all sources: %s", exc)
            return {}
        except Exception as exc:
            self.logger.error("Error importing all sources: %s", exc)
            return {}

    def validate_environment(self) -> bool:
        """
        Validate required packages and configuration for analytics service.
        Returns:
            bool: True if environment is valid, False otherwise.
        """
        if not hasattr(self, "import_manager") or self.import_manager is None:
            self.logger.error("DataImportManager is not initialized.")
            return False
        self.logger.info("Environment validation passed.")
        return True

    def get_interactive_dashboard(
        self,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Return dashboard data with interactive filtering options."""
        data = self.get_dashboard_data()
        if filters:
            # Example: filter by min proposals
            min_proposals = filters.get("min_proposals")
            if min_proposals is not None:
                if data["total_proposals"] < min_proposals:
                    data["top_opportunities"] = []
        return data

    def get_advanced_dashboard(
        self,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Return dashboard data with advanced filtering options."""
        data = self.get_dashboard_data()
        if filters:
            if "min_proposals" in filters:
                data = filter_by_min_proposals(
                    data,
                    filters["min_proposals"]
                )
            if "min_success_rate" in filters:
                data = filter_by_success_rate(
                    data,
                    filters["min_success_rate"]
                )
        return data

    def export_dashboard_chart(self, chart_type: str, filename: str) -> bool:
        """Export dashboard chart to file with role check."""
        if not self.roles_service.has_permission(self.user_role, "export"):
            self.logger.error("Permission denied for chart export.")
            return False
        try:
            from src.analytics.visualization import export_chart
            stats = self.get_statistics()
            export_chart(stats, chart_type, filename)
            self.logger.info("Exported %s chart to %s", chart_type, filename)
            return True
        except (IOError, OSError) as exc:
            self.logger.error("Error in export: %s", exc)
            return False
        except Exception as exc:
            self.logger.error("Error in export: %s", exc)
            return False
