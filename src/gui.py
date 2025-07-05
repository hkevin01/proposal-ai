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

from database import DatabaseManager
from discovery_engine import OpportunityProcessor

# Import the AI proposal components
try:
    from ai_proposal_generator import (
        AIProposalGenerator,
        ProposalContext,
        ProposalManager,
    )
    from proposal_editor_gui import ProposalEditorWidget, ProposalGenerationWorker
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

# Import enhanced discovery features
try:
    from enhanced_gui_tab import EnhancedDiscoveryTab
    ENHANCED_DISCOVERY_AVAILABLE = True
except ImportError:
    ENHANCED_DISCOVERY_AVAILABLE = False
    print("Warning: Enhanced discovery features not available. Install required packages.")
    print("Warning: AI proposal generation not available. Install OpenAI and transformers packages.")


class ScrapingWorker(QThread):
    """Worker thread for web scraping to avoid blocking GUI"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(int)
    error = pyqtSignal(str)
    
    def run(self):
        try:
            self.progress.emit("Starting opportunity discovery...")
            # Here you would run the Scrapy spider
            # For now, simulate with a timer
            import time
            
            steps = [
                "Initializing scrapers...",
                "Scraping IAC website...", 
                "Scraping NASA SBIR...",
                "Scraping ESA calls...",
                "Processing data...",
                "Updating database..."
            ]
            
            for i, step in enumerate(steps):
                self.progress.emit(step)
                time.sleep(1)  # Simulate work
                
            # Process scraped data
            processor = OpportunityProcessor()
            processor.process_unprocessed_opportunities()
            
            self.finished.emit(len(steps))
            
        except Exception as e:
            self.error.emit(str(e))


class OpportunityDetailDialog(QWidget):
    """Dialog to show detailed opportunity information"""
    
    def __init__(self, opportunity_data):
        super().__init__()
        self.opportunity_data = opportunity_data
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle("Opportunity Details")
        self.setGeometry(200, 200, 600, 500)
        
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel(self.opportunity_data.get('name', 'No Title'))
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title_label)
        
        # Details form
        form_layout = QFormLayout()
        
        # Organization
        org_label = QLabel(self.opportunity_data.get('org_name', 'Unknown'))
        form_layout.addRow("Organization:", org_label)
        
        # Deadline
        deadline_label = QLabel(self.opportunity_data.get('deadline', 'Not specified'))
        form_layout.addRow("Deadline:", deadline_label)
        
        # Status
        status_label = QLabel(self.opportunity_data.get('status', 'Open'))
        form_layout.addRow("Status:", status_label)
        
        # URL
        if self.opportunity_data.get('url'):
            url_label = QLabel(f'<a href="{self.opportunity_data["url"]}">{self.opportunity_data["url"]}</a>')
            url_label.setOpenExternalLinks(True)
            form_layout.addRow("Website:", url_label)
        
        layout.addLayout(form_layout)
        
        # Description
        desc_group = QGroupBox("Description")
        desc_layout = QVBoxLayout()
        desc_text = QTextEdit()
        desc_text.setPlainText(self.opportunity_data.get('description', 'No description available'))
        desc_text.setReadOnly(True)
        desc_layout.addWidget(desc_text)
        desc_group.setLayout(desc_layout)
        layout.addWidget(desc_group)
        
        # Requirements
        req_group = QGroupBox("Requirements")
        req_layout = QVBoxLayout()
        req_text = QTextEdit()
        req_text.setPlainText(self.opportunity_data.get('requirements', 'No requirements specified'))
        req_text.setReadOnly(True)
        req_layout.addWidget(req_text)
        req_group.setLayout(req_layout)
        layout.addWidget(req_group)
        
        self.setLayout(layout)


class ProposalAIMainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
        self.scraping_worker = None
        self.setup_ui()
        self.load_initial_data()
    
    def setup_ui(self):
        self.setWindowTitle('Proposal AI - Opportunity Discovery & Management')
        self.setGeometry(100, 100, 1200, 800)
        
        # Apply modern styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QTabWidget::pane {
                border: 1px solid #c0c0c0;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #0078d4;
            }
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QGroupBox {
                font-weight: bold;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Create central widget with tabs
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.create_discovery_tab()
        
        # Add enhanced discovery tab if available
        if ENHANCED_DISCOVERY_AVAILABLE:
            self.enhanced_discovery_tab = EnhancedDiscoveryTab(self.db_manager)
            self.tab_widget.addTab(self.enhanced_discovery_tab, "🚀 Enhanced Discovery")
        
        self.create_opportunities_tab()
        self.create_proposals_tab()
        self.create_settings_tab()
    
    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        file_menu.addAction('Export Data', self.export_data)
        file_menu.addAction('Import Data', self.import_data)
        file_menu.addSeparator()
        file_menu.addAction('Exit', self.close)
        
        # Tools menu
        tools_menu = menubar.addMenu('Tools')
        tools_menu.addAction('Run Discovery', self.start_discovery)
        tools_menu.addAction('Refresh Database', self.refresh_database)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        help_menu.addAction('About', self.show_about)
    
    def create_discovery_tab(self):
        """Tab for running opportunity discovery"""
        discovery_widget = QWidget()
        layout = QVBoxLayout(discovery_widget)
        
        # Control panel
        control_group = QGroupBox("Discovery Control")
        control_layout = QVBoxLayout()
        
        # Status display
        self.discovery_status = QLabel("Ready to discover opportunities")
        control_layout.addWidget(self.discovery_status)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        control_layout.addWidget(self.progress_bar)
        
        # Control buttons
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("🔍 Start Discovery")
        self.start_button.clicked.connect(self.start_discovery)
        self.stop_button = QPushButton("⏹ Stop")
        self.stop_button.setEnabled(False)
        
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addStretch()
        
        control_layout.addLayout(button_layout)
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
        
        # Configuration panel
        config_group = QGroupBox("Discovery Configuration")
        config_layout = QFormLayout()
        
        self.target_websites = QLineEdit("IAC, NASA, ESA, Grants.gov")
        self.keywords_input = QLineEdit("space, aerospace, research, innovation")
        self.max_results = QComboBox()
        self.max_results.addItems(["50", "100", "200", "500"])
        
        config_layout.addRow("Target Websites:", self.target_websites)
        config_layout.addRow("Keywords:", self.keywords_input)
        config_layout.addRow("Max Results:", self.max_results)
        
        config_group.setLayout(config_layout)
        layout.addWidget(config_group)
        
        # Results preview
        results_group = QGroupBox("Latest Discoveries")
        results_layout = QVBoxLayout()
        
        self.discovery_results = QListWidget()
        results_layout.addWidget(self.discovery_results)
        
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)
        
        self.tab_widget.addTab(discovery_widget, "🔍 Discovery")
    
    def create_opportunities_tab(self):
        """Tab for browsing and managing opportunities"""
        opportunities_widget = QWidget()
        layout = QVBoxLayout(opportunities_widget)
        
        # Search and filter panel
        search_group = QGroupBox("Search & Filter")
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search opportunities...")
        self.search_input.textChanged.connect(self.filter_opportunities)
        
        self.organization_filter = QComboBox()
        self.organization_filter.addItem("All Organizations")
        self.organization_filter.currentTextChanged.connect(self.filter_opportunities)
        
        self.status_filter = QComboBox()
        self.status_filter.addItems(["All Status", "Open", "Closed", "Upcoming"])
        self.status_filter.currentTextChanged.connect(self.filter_opportunities)
        
        search_layout.addWidget(QLabel("Search:"))
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(QLabel("Organization:"))
        search_layout.addWidget(self.organization_filter)
        search_layout.addWidget(QLabel("Status:"))
        search_layout.addWidget(self.status_filter)
        
        search_group.setLayout(search_layout)
        layout.addWidget(search_group)
        
        # Opportunities table
        self.opportunities_table = QTableWidget()
        self.opportunities_table.setColumnCount(6)
        self.opportunities_table.setHorizontalHeaderLabels([
            "Title", "Organization", "Deadline", "Status", "Created", "Actions"
        ])
        self.opportunities_table.cellDoubleClicked.connect(self.show_opportunity_details)
        layout.addWidget(self.opportunities_table)
        
        self.tab_widget.addTab(opportunities_widget, "📋 Opportunities")
    
    def create_proposals_tab(self):
        """Tab for AI-powered proposal creation and management"""
        if AI_AVAILABLE:
            # Use the full-featured AI proposal editor
            self.proposal_editor = ProposalEditorWidget(self.db_manager)
            self.tab_widget.addTab(self.proposal_editor, "🤖 AI Proposals")
        else:
            # Fallback basic proposals interface
            proposals_widget = QWidget()
            layout = QVBoxLayout(proposals_widget)
            
            # Warning about missing AI features
            warning_group = QGroupBox("⚠️ AI Features Not Available")
            warning_layout = QVBoxLayout()
            warning_label = QLabel(
                "AI proposal generation requires additional packages.\n"
                "Install with: pip install openai transformers torch"
            )
            warning_label.setStyleSheet("color: #d4822a; font-weight: bold;")
            warning_layout.addWidget(warning_label)
            warning_group.setLayout(warning_layout)
            layout.addWidget(warning_group)
            
            # Basic proposal management panel
            management_group = QGroupBox("Basic Proposal Management")
            management_layout = QHBoxLayout()
            
            new_proposal_btn = QPushButton("📝 New Proposal")
            import_proposal_btn = QPushButton("📁 Import Proposal")
            export_proposals_btn = QPushButton("💾 Export All")
            
            # Connect to placeholder functions
            new_proposal_btn.clicked.connect(self.create_basic_proposal)
            import_proposal_btn.clicked.connect(self.import_proposal)
            export_proposals_btn.clicked.connect(self.export_proposals)
            
            management_layout.addWidget(new_proposal_btn)
            management_layout.addWidget(import_proposal_btn)
            management_layout.addWidget(export_proposals_btn)
            management_layout.addStretch()
            
            management_group.setLayout(management_layout)
            layout.addWidget(management_group)
            
            # Basic proposals table
            self.proposals_table = QTableWidget()
            self.proposals_table.setColumnCount(5)
            self.proposals_table.setHorizontalHeaderLabels([
                "Title", "Opportunity", "Status", "Deadline", "Last Modified"
            ])
            layout.addWidget(self.proposals_table)
            
            self.tab_widget.addTab(proposals_widget, "📄 Proposals")
    
    def create_basic_proposal(self):
        """Create a basic proposal without AI assistance"""
        QMessageBox.information(self, "Basic Proposal", 
                              "Basic proposal creation feature coming soon!\n"
                              "For AI-powered proposal generation, install the required packages.")
    
    def import_proposal(self):
        """Import an existing proposal"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Import Proposal", "", 
            "Text Files (*.txt);;Word Documents (*.docx);;All Files (*)"
        )
        if filename:
            QMessageBox.information(self, "Import", f"Would import: {filename}")
    
    def export_proposals(self):
        """Export all proposals"""
        QMessageBox.information(self, "Export", "Export feature coming soon!")
    
    def create_settings_tab(self):
        """Tab for application settings"""
        settings_widget = QWidget()
        layout = QVBoxLayout(settings_widget)
        
        # Database settings
        db_group = QGroupBox("Database Settings")
        db_layout = QFormLayout()
        
        self.db_path_input = QLineEdit("proposal_ai.db")
        backup_btn = QPushButton("Create Backup")
        
        db_layout.addRow("Database Path:", self.db_path_input)
        db_layout.addRow("", backup_btn)
        
        db_group.setLayout(db_layout)
        layout.addWidget(db_group)
        
        # Scraping settings
        scraping_group = QGroupBox("Scraping Settings")
        scraping_layout = QFormLayout()
        
        self.scraping_interval = QComboBox()
        self.scraping_interval.addItems(["Manual", "Daily", "Weekly", "Monthly"])
        
        self.user_agent = QLineEdit("Proposal-AI-Bot 1.0")
        self.timeout_setting = QComboBox()
        self.timeout_setting.addItems(["30s", "60s", "120s", "300s"])
        
        scraping_layout.addRow("Auto-Discovery:", self.scraping_interval)
        scraping_layout.addRow("User Agent:", self.user_agent)
        scraping_layout.addRow("Timeout:", self.timeout_setting)
        
        scraping_group.setLayout(scraping_layout)
        layout.addWidget(scraping_group)
        
        # Notification settings
        notification_group = QGroupBox("Notifications")
        notification_layout = QVBoxLayout()
        
        self.email_notifications = QCheckBox("Email notifications for new opportunities")
        self.deadline_reminders = QCheckBox("Deadline reminders")
        self.status_updates = QCheckBox("Status update notifications")
        
        notification_layout.addWidget(self.email_notifications)
        notification_layout.addWidget(self.deadline_reminders)
        notification_layout.addWidget(self.status_updates)
        
        notification_group.setLayout(notification_layout)
        layout.addWidget(notification_group)
        
        layout.addStretch()
        
        self.tab_widget.addTab(settings_widget, "⚙️ Settings")
    
    def load_initial_data(self):
        """Load initial data into the interface"""
        self.refresh_opportunities_table()
        self.refresh_organization_filter()
    
    def refresh_opportunities_table(self):
        """Refresh the opportunities table with latest data"""
        events = self.db_manager.get_events()
        
        self.opportunities_table.setRowCount(len(events))
        
        for row, event in enumerate(events):
            # Assuming event structure: (id, name, org_id, date, deadline, desc, url, req, status, created, org_name)
            self.opportunities_table.setItem(row, 0, QTableWidgetItem(event[1] or ""))  # name
            self.opportunities_table.setItem(row, 1, QTableWidgetItem(event[10] if len(event) > 10 else "Unknown"))  # org_name
            self.opportunities_table.setItem(row, 2, QTableWidgetItem(event[4] or ""))  # deadline
            self.opportunities_table.setItem(row, 3, QTableWidgetItem(event[8] or "Open"))  # status
            self.opportunities_table.setItem(row, 4, QTableWidgetItem(event[9] or ""))  # created
            
            # Store full event data in the first item for later retrieval
            item = self.opportunities_table.item(row, 0)
            if item:
                item.setData(Qt.UserRole, event)
    
    def refresh_organization_filter(self):
        """Refresh organization filter dropdown"""
        current_text = self.organization_filter.currentText()
        self.organization_filter.clear()
        self.organization_filter.addItem("All Organizations")
        
        # Get unique organizations from database
        events = self.db_manager.get_events()
        organizations = set()
        for event in events:
            if len(event) > 10 and event[10]:
                organizations.add(event[10])
        
        for org in sorted(organizations):
            self.organization_filter.addItem(org)
        
        # Restore previous selection if possible
        index = self.organization_filter.findText(current_text)
        if index >= 0:
            self.organization_filter.setCurrentIndex(index)
    
    def filter_opportunities(self):
        """Filter opportunities based on search criteria"""
        search_text = self.search_input.text().lower()
        org_filter = self.organization_filter.currentText()
        status_filter = self.status_filter.currentText()
        
        for row in range(self.opportunities_table.rowCount()):
            show_row = True
            
            # Apply search filter
            if search_text:
                title_item = self.opportunities_table.item(row, 0)
                org_item = self.opportunities_table.item(row, 1)
                title_text = title_item.text().lower() if title_item else ""
                org_text = org_item.text().lower() if org_item else ""
                
                if search_text not in title_text and search_text not in org_text:
                    show_row = False
            
            # Apply organization filter
            if org_filter != "All Organizations":
                org_item = self.opportunities_table.item(row, 1)
                if not org_item or org_item.text() != org_filter:
                    show_row = False
            
            # Apply status filter
            if status_filter != "All Status":
                status_item = self.opportunities_table.item(row, 3)
                if not status_item or status_item.text() != status_filter:
                    show_row = False
            
            self.opportunities_table.setRowHidden(row, not show_row)
    
    def start_discovery(self):
        """Start the opportunity discovery process"""
        if self.scraping_worker and self.scraping_worker.isRunning():
            return
        
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        
        # Start worker thread
        self.scraping_worker = ScrapingWorker()
        self.scraping_worker.progress.connect(self.update_discovery_status)
        self.scraping_worker.finished.connect(self.discovery_finished)
        self.scraping_worker.error.connect(self.discovery_error)
        self.scraping_worker.start()
    
    def update_discovery_status(self, message):
        """Update discovery status display"""
        self.discovery_status.setText(message)
        self.status_bar.showMessage(message)
    
    def discovery_finished(self, count):
        """Handle discovery completion"""
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.progress_bar.setVisible(False)
        
        self.discovery_status.setText(f"Discovery completed! Found {count} opportunities.")
        self.status_bar.showMessage("Discovery completed")
        
        # Refresh data
        self.refresh_opportunities_table()
        self.refresh_organization_filter()
        
        # Show notification
        QMessageBox.information(self, "Discovery Complete", 
                              f"Successfully discovered {count} new opportunities!")
    
    def discovery_error(self, error_message):
        """Handle discovery errors"""
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.progress_bar.setVisible(False)
        
        self.discovery_status.setText(f"Error: {error_message}")
        self.status_bar.showMessage("Discovery failed")
        
        QMessageBox.critical(self, "Discovery Error", 
                           f"An error occurred during discovery:\n{error_message}")
    
    def show_opportunity_details(self, row, column):
        """Show detailed view of selected opportunity"""
        item = self.opportunities_table.item(row, 0)
        if item:
            event_data = item.data(Qt.UserRole)
            if event_data:
                # Convert tuple to dict for easier access
                opportunity_dict = {
                    'name': event_data[1],
                    'org_name': event_data[10] if len(event_data) > 10 else 'Unknown',
                    'deadline': event_data[4],
                    'status': event_data[8],
                    'description': event_data[5],
                    'url': event_data[6],
                    'requirements': event_data[7]
                }
                
                detail_dialog = OpportunityDetailDialog(opportunity_dict)
                detail_dialog.show()
    
    def export_data(self):
        """Export data to file"""
        self.status_bar.showMessage("Export functionality coming soon...")
    
    def import_data(self):
        """Import data from file"""
        self.status_bar.showMessage("Import functionality coming soon...")
    
    def refresh_database(self):
        """Refresh database connection and data"""
        self.refresh_opportunities_table()
        self.refresh_organization_filter()
        self.status_bar.showMessage("Database refreshed")
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "About Proposal AI", 
                         "Proposal AI v1.0\n\nAI-powered proposal discovery and management system\n"
                         "for space and technology opportunities.")


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
