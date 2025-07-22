"""
PyQt GUI for Proposal AI - Opportunity Discovery and Management
"""
import json
import sys

from PyQt5.QtCore import QDate, Qt, QThread, QTimer, pyqtSignal
from PyQt5.QtGui import QColor, QFont, QIcon, QPalette
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDateEdit,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenuBar,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSplitter,
    QStatusBar,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..core.config import MAIN_DATABASE_PATH
from ..core.database import DatabaseManager
from ..discovery.discovery_engine import OpportunityProcessor
from src.services.api_service import APIService
from src.services.notification_service import NotificationService
from src.services.analytics_service import AnalyticsService

class MainWindow(QMainWindow):
    """Main application window for Proposal AI."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Proposal AI")
        self.setGeometry(100, 100, 800, 600)
        label = QLabel("Welcome to Proposal AI!", self)
        label.move(350, 250)

    def show(self):
        """Show the main window."""
        app = QApplication(sys.argv)
        self.show()
        app.exec_()
    
    def export_proposal(self, proposal, filename):
        """Export a proposal to PDF."""
        export_proposal_pdf(proposal, filename)
        print(f"Proposal exported to {filename}")

    def export_analytics(self, analytics, filename):
        """Export analytics data to DOCX."""
        export_analytics_docx(analytics, filename)
        print(f"Analytics exported to {filename}")
    
    def visualize_proposal_counts(self):
        """Visualize proposal counts as a bar chart."""
        stats = self.analytics.get_statistics()
        plot_proposal_counts(stats)

    def visualize_success_rates(self):
        """Visualize proposal success rates as a line chart."""
        stats = self.analytics.get_statistics()
        plot_success_rates(stats)

    def export_proposal_chart(self, filename):
        """Export proposal counts chart to file."""
        import matplotlib.pyplot as plt
        stats = self.analytics.get_statistics()
        plot_proposal_counts(stats)
        plt.savefig(filename)
        print(f"Proposal chart exported to {filename}")

    def export_success_rate_chart(self, filename):
        """Export success rates chart to file."""
        import matplotlib.pyplot as plt
        stats = self.analytics.get_statistics()
        plot_success_rates(stats)
        plt.savefig(filename)
        print(f"Success rate chart exported to {filename}")
    
    def show_interactive_proposal_counts(self, filter_fn=None):
        """Show interactive proposal counts chart with optional filtering."""
        stats = self.analytics.get_statistics()
        if filter_fn:
            stats["proposal_counts"] = list(filter(filter_fn, stats["proposal_counts"]))
        show_interactive_proposal_counts(stats)

    def show_interactive_success_rates(self, filter_fn=None):
        """Show interactive success rates chart with optional filtering."""
        stats = self.analytics.get_statistics()
        if filter_fn:
            stats["success_rates"] = list(filter(filter_fn, stats["success_rates"]))
        show_interactive_success_rates(stats)

    def import_data_with_role(self, source_type, path_or_url, user_role):
        """Import data with role-based permission check."""
        service = AnalyticsService(user_role=user_role)
        try:
            data = service.import_external_data(source_type, path_or_url)
            self.statusBar().showMessage(f"Imported {len(data)} records.")
        except PermissionError:
            self.statusBar().showMessage("Permission denied for import.")
        except Exception as e:
            self.statusBar().showMessage(f"Import error: {e}")

    def update_dashboard_realtime(self):
        """Update dashboard with real-time analytics."""
        service = AnalyticsService()
        data = service.get_dashboard_data()
        # Example: update widgets (pseudo-code)
        if hasattr(self, 'dashboard_widget'):
            self.dashboard_widget.update_data(data)
        if hasattr(self, 'chart_widget'):
            self.chart_widget.update_chart(data)
        self.statusBar().showMessage("Dashboard updated with real-time data.")


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Proposal AI")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Proposal AI Team")
    
    # Create and show main window
    window = ProposalAIMainWindow()
    window.show()
    
    return app.exec_()


if __name__ == '__main__':
    sys.exit(main())
