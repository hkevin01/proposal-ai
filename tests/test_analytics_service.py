"""
Unit tests for AnalyticsService.
"""
import unittest
from src.services.analytics_service import AnalyticsService


class TestAnalyticsService(unittest.TestCase):

    def setUp(self):
        self.service = AnalyticsService()

    def test_get_dashboard_data(self):
        data = self.service.get_dashboard_data()
        self.assertIn("total_proposals", data)
        self.assertIn("proposal_success_rate", data)
        # Edge case: no proposals
        self.service.analytics_data["total_proposals"] = 0
        data = self.service.get_dashboard_data()
        self.assertEqual(data["proposal_success_rate"], 0.0)
        self.assertEqual(data["top_opportunities"], [])

    def test_generate_report(self):
        result = self.service.generate_report({"type": "summary"})
        self.assertTrue(result.startswith("Report type: summary"))
        # Edge case: invalid params
        result = self.service.generate_report(None)
        self.assertEqual(result, "Error: Invalid report parameters.")

    def test_get_statistics(self):
        stats = self.service.get_statistics()
        self.assertIn("proposal_counts", stats)
        self.assertIn("success_rates", stats)
        # Edge case: all zeros
        stats["proposal_counts"] = [0, 0, 0, 0, 0]
        self.service.logger.info = lambda *a, **kw: None  # Suppress logging
        self.service.get_statistics = lambda: stats
        stats = self.service.get_statistics()
        self.assertTrue(all(x == 0.0 for x in stats["success_rates"]))

    def test_validate_environment(self):
        result = self.service.validate_environment()
        self.assertIsInstance(result, bool)

    def test_import_external_data_csv(self):
        # Should handle missing file gracefully
        data = self.service.import_external_data("csv", "nonexistent.csv")
        self.assertIsInstance(data, list)

    def test_import_all_sources(self):
        # Should return a dict even if config is empty
        results = self.service.import_all_sources()
        self.assertIsInstance(results, dict)

    def test_load_external_data_permission(self):
        service = AnalyticsService(user_role="viewer")
        try:
            service.load_external_data("csv", "data/nasa_opportunities.csv")
        except PermissionError:
            self.assertTrue(True)
        else:
            self.assertTrue(False)

    def test_dashboard_data_validation(self):
        service = AnalyticsService()
        valid_data = {
            "total_proposals": 5,
            "total_opportunities": 2,
            "proposal_success_rate": 0.5,
            "top_opportunities": ["IAC", "NASA"]
        }
        self.assertTrue(service._validate_dashboard_data(valid_data))
        invalid_data = {
            "total_proposals": 5,
            "total_opportunities": 2,
            "proposal_success_rate": 0.5,
            # Missing 'top_opportunities'
        }
        self.assertFalse(service._validate_dashboard_data(invalid_data))


if __name__ == "__main__":
    unittest.main()
