import unittest
from src.analytics import interactive_dashboard


class TestInteractiveDashboard(unittest.TestCase):

    def test_show_interactive_proposal_counts(self):
        stats = {"proposal_counts": [1, 2, 3, 4, 5]}
        # Should not raise
        interactive_dashboard.show_interactive_proposal_counts(stats)

    def test_show_interactive_success_rates(self):
        stats = {"success_rates": [0.5, 0.6, 0.7, 0.8, 0.9]}
        # Should not raise
        interactive_dashboard.show_interactive_success_rates(stats)


if __name__ == "__main__":
    unittest.main()
