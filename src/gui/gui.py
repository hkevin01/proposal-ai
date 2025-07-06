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

# Import the AI proposal components
try:
    from ..proposals.ai_proposal_generator import (
        AIProposalGenerator,
        ProposalContext,
        ProposalManager,
    )
    from .proposal_editor_gui import ProposalEditorWidget, ProposalGenerationWorker
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

# Import donor functionality
try:
    from ..donors.donor_database import DonorDatabase
    from ..donors.donor_enhanced_discovery import DonorEnhancedDiscovery
    from .donor_gui import DonorManagementWidget
    DONOR_FUNCTIONALITY_AVAILABLE = True
except ImportError:
    DONOR_FUNCTIONALITY_AVAILABLE = False

# Import enhanced discovery features
try:
    from .enhanced_gui_tab import EnhancedDiscoveryTab
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
            from ..core.database import DatabaseManager
            from ..discovery.api_integrations import APIIntegrationManager
            from ..discovery.enhanced_discovery_engine import (
                EnhancedOpportunityDiscoverer,
            )
            
            self.progress.emit("Starting enhanced discovery...")
            
            # Initialize discovery systems
            enhanced_discoverer = EnhancedOpportunityDiscoverer()
            api_manager = APIIntegrationManager()
            db_manager = DatabaseManager()
            
            # Get keywords from GUI (default for now)
            keywords = ['artificial intelligence', 'machine learning', 'space', 
                       'aerospace', 'research', 'innovation']
            
            all_opportunities = []
            
            # Phase 1: API Discovery
            self.progress.emit("🔍 Discovering from APIs (Grants.gov, NASA, NSF, arXiv)...")
            try:
                api_opportunities = api_manager.get_all_api_opportunities(keywords, 15)
                all_opportunities.extend(api_opportunities)
                self.progress.emit(f"✅ Found {len(api_opportunities)} opportunities from APIs")
            except Exception as e:
                self.progress.emit(f"⚠️ API discovery error: {e}")
            
            # Phase 2: Enhanced Web Discovery
            self.progress.emit("🔍 Enhanced web scraping from 50+ sources...")
            try:
                web_opportunities = enhanced_discoverer.discover_opportunities(max_per_source=10)
                all_opportunities.extend(web_opportunities)
                self.progress.emit(f"✅ Found {len(web_opportunities)} opportunities from web scraping")
            except Exception as e:
                self.progress.emit(f"⚠️ Web discovery error: {e}")
            
            # Phase 3: Save to database
            self.progress.emit("💾 Saving opportunities to database...")
            try:
                saved_count = 0
                for opp in all_opportunities:
                    try:
                        # Save to database
                        db_manager.save_opportunity(opp)
                        saved_count += 1
                    except Exception as e:
                        print(f"Error saving opportunity: {e}")
                        continue
                
                self.progress.emit(f"✅ Saved {saved_count} opportunities to database")
                
            except Exception as e:
                self.progress.emit(f"⚠️ Database save error: {e}")
            
            total_found = len(all_opportunities)
            self.progress.emit(f"🎯 Discovery complete! Total: {total_found} opportunities")
            self.finished.emit(total_found)
            
        except Exception as e:
            self.error.emit(str(e))


class OpportunityDetailDialog(QWidget):
    """Enhanced dialog to show detailed opportunity information"""
    
    def __init__(self, opportunity_data, db_manager=None):
        super().__init__()
        self.opportunity_data = opportunity_data
        self.db_manager = db_manager
        self.setup_ui()
        self.load_additional_data()
    
    def setup_ui(self):
        self.setWindowTitle("Opportunity Details")
        self.setGeometry(150, 150, 900, 700)
        self.setWindowIcon(self.style().standardIcon(
            self.style().SP_FileDialogDetailedView))
        
        main_layout = QVBoxLayout()
        
        # Header with title and quick actions
        header_layout = QHBoxLayout()
        
        # Title
        title_text = str(self.opportunity_data.get('name', 'No Title'))
        title_label = QLabel(title_text)
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setWordWrap(True)
        header_layout.addWidget(title_label)
        
        # Quick action buttons
        action_layout = QVBoxLayout()
        
        bookmark_btn = QPushButton("📌 Bookmark")
        bookmark_btn.clicked.connect(self.bookmark_opportunity)
        action_layout.addWidget(bookmark_btn)
        
        apply_btn = QPushButton("📝 Mark as Applied")
        apply_btn.clicked.connect(self.mark_as_applied)
        action_layout.addWidget(apply_btn)
        
        export_btn = QPushButton("💾 Export Details")
        export_btn.clicked.connect(self.export_details)
        action_layout.addWidget(export_btn)
        
        header_layout.addLayout(action_layout)
        main_layout.addLayout(header_layout)
        
        # Tab widget for organized information
        self.tab_widget = QTabWidget()
        
        # Overview Tab
        self.setup_overview_tab()
        
        # Details Tab
        self.setup_details_tab()
        
        # Analysis Tab
        self.setup_analysis_tab()
        
        # Actions Tab
        self.setup_actions_tab()
        
        main_layout.addWidget(self.tab_widget)
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)
    
    def setup_overview_tab(self):
        """Setup the overview tab with key information"""
        overview_widget = QWidget()
        layout = QVBoxLayout()
        
        # Key information grid
        info_group = QGroupBox("Key Information")
        info_layout = QFormLayout()
        
        # Organization
        org_text = str(self.opportunity_data.get('org_name', 'Unknown'))
        org_label = QLabel(org_text)
        org_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        info_layout.addRow("Organization:", org_label)
        
        # Deadline with formatting
        deadline_text = str(self.opportunity_data.get(
            'deadline', 'Not specified'))
        deadline_label = QLabel(deadline_text)
        deadline_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        if 'not specified' not in deadline_text.lower():
            deadline_label.setStyleSheet("color: red; font-weight: bold;")
        info_layout.addRow("Deadline:", deadline_label)
        
        # Status
        status_text = str(self.opportunity_data.get('status', 'Open'))
        status_label = QLabel(status_text)
        status_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        if status_text.lower() == 'open':
            status_label.setStyleSheet("color: green; font-weight: bold;")
        elif status_text.lower() == 'closed':
            status_label.setStyleSheet("color: red; font-weight: bold;")
        info_layout.addRow("Status:", status_label)
        
        # Category/Type
        category_text = str(self.opportunity_data.get('category', 'General'))
        category_label = QLabel(category_text)
        category_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        info_layout.addRow("Category:", category_label)
        
        # Estimated Funding
        funding_text = str(self.opportunity_data.get(
            'estimated_funding', 'Not specified'))
        funding_label = QLabel(funding_text)
        funding_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        if funding_text != 'Not specified':
            funding_label.setStyleSheet("color: green; font-weight: bold;")
        info_layout.addRow("Estimated Funding:", funding_label)
        
        # URL
        if self.opportunity_data.get('url'):
            url = str(self.opportunity_data["url"])
            url_html = f'<a href="{url}" style="color: blue;">{url}</a>'
            url_label = QLabel(url_html)
            url_label.setOpenExternalLinks(True)
            url_label.setWordWrap(True)
            info_layout.addRow("Website:", url_label)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Quick description
        desc_group = QGroupBox("Quick Description")
        desc_layout = QVBoxLayout()
        desc_text = QTextEdit()
        description = str(self.opportunity_data.get(
            'description', 'No description available'))
        # Truncate for overview
        if len(description) > 500:
            description = (description[:500] +
                           "... (see Details tab for full description)")
        desc_text.setPlainText(description)
        desc_text.setReadOnly(True)
        desc_text.setMaximumHeight(150)
        desc_layout.addWidget(desc_text)
        desc_group.setLayout(desc_layout)
        layout.addWidget(desc_group)
        
        # Keywords section
        keywords_group = QGroupBox("Keywords")
        keywords_layout = QVBoxLayout()
        keywords_text = str(self.opportunity_data.get(
            'keywords', 'No keywords available'))
        keywords_label = QLabel(keywords_text)
        keywords_label.setWordWrap(True)
        keywords_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        keywords_layout.addWidget(keywords_label)
        keywords_group.setLayout(keywords_layout)
        layout.addWidget(keywords_group)
        
        layout.addStretch()
        overview_widget.setLayout(layout)
        self.tab_widget.addTab(overview_widget, "📋 Overview")
    
    def setup_details_tab(self):
        """Setup the details tab with full information"""
        details_widget = QWidget()
        layout = QVBoxLayout()
        
        # Full description
        desc_group = QGroupBox("Full Description")
        desc_layout = QVBoxLayout()
        desc_text = QTextEdit()
        description = str(self.opportunity_data.get(
            'description', 'No description available'))
        desc_text.setPlainText(description)
        desc_text.setReadOnly(True)
        desc_layout.addWidget(desc_text)
        desc_group.setLayout(desc_layout)
        layout.addWidget(desc_group)
        
        # Requirements
        req_group = QGroupBox("Requirements & Eligibility")
        req_layout = QVBoxLayout()
        req_text = QTextEdit()
        requirements = str(self.opportunity_data.get(
            'requirements', 'No requirements specified'))
        req_text.setPlainText(requirements)
        req_text.setReadOnly(True)
        req_layout.addWidget(req_text)
        req_group.setLayout(req_layout)
        layout.addWidget(req_group)
        
        details_widget.setLayout(layout)
        self.tab_widget.addTab(details_widget, "📄 Details")
    
    def setup_analysis_tab(self):
        """Setup the analysis tab with matching and scoring information"""
        analysis_widget = QWidget()
        layout = QVBoxLayout()
        
        # Relevance scoring
        score_group = QGroupBox("Relevance Analysis")
        score_layout = QFormLayout()
        
        relevance_score = self.opportunity_data.get('relevance_score', 0.0)
        try:
            relevance_score = float(relevance_score)
        except (ValueError, TypeError):
            relevance_score = 0.0
        
        score_label = QLabel(f"{relevance_score:.2f}")
        if relevance_score >= 0.7:
            score_label.setStyleSheet("color: green; font-weight: bold;")
        elif relevance_score >= 0.4:
            score_label.setStyleSheet("color: orange; font-weight: bold;")
        else:
            score_label.setStyleSheet("color: red; font-weight: bold;")
        score_layout.addRow("Relevance Score:", score_label)
        
        # Match keywords
        match_keywords = str(self.opportunity_data.get(
            'match_keywords', 'No match data'))
        match_label = QLabel(match_keywords)
        match_label.setWordWrap(True)
        score_layout.addRow("Matching Keywords:", match_label)
        
        score_group.setLayout(score_layout)
        layout.addWidget(score_group)
        
        # Source information
        source_group = QGroupBox("Source Information")
        source_layout = QFormLayout()
        
        source_url = str(self.opportunity_data.get('source_url', 'Unknown'))
        source_label = QLabel(source_url)
        source_label.setWordWrap(True)
        source_layout.addRow("Source URL:", source_label)
        
        created_at = str(self.opportunity_data.get('created_at', 'Unknown'))
        created_label = QLabel(created_at)
        source_layout.addRow("Discovered On:", created_label)
        
        source_group.setLayout(source_layout)
        layout.addWidget(source_group)
        
        layout.addStretch()
        analysis_widget.setLayout(layout)
        self.tab_widget.addTab(analysis_widget, "📊 Analysis")
    
    def setup_actions_tab(self):
        """Setup the actions tab with user interaction options"""
        actions_widget = QWidget()
        layout = QVBoxLayout()
        
        # User notes
        notes_group = QGroupBox("Personal Notes")
        notes_layout = QVBoxLayout()
        self.notes_text = QTextEdit()
        self.notes_text.setPlaceholderText(
            "Add your personal notes about this opportunity...")
        notes_layout.addWidget(self.notes_text)
        
        save_notes_btn = QPushButton("💾 Save Notes")
        save_notes_btn.clicked.connect(self.save_notes)
        notes_layout.addWidget(save_notes_btn)
        
        notes_group.setLayout(notes_layout)
        layout.addWidget(notes_group)
        
        # Application tracking
        tracking_group = QGroupBox("Application Tracking")
        tracking_layout = QVBoxLayout()
        
        self.application_status = QComboBox()
        self.application_status.addItems([
            "Not Applied", "Planning to Apply", "Application in Progress",
            "Applied", "Under Review", "Accepted", "Rejected"
        ])
        tracking_layout.addWidget(QLabel("Application Status:"))
        tracking_layout.addWidget(self.application_status)
        
        update_status_btn = QPushButton("📝 Update Status")
        update_status_btn.clicked.connect(self.update_application_status)
        tracking_layout.addWidget(update_status_btn)
        
        tracking_group.setLayout(tracking_layout)
        layout.addWidget(tracking_group)
        
        layout.addStretch()
        actions_widget.setLayout(layout)
        self.tab_widget.addTab(actions_widget, "⚡ Actions")
    
    def load_additional_data(self):
        """Load additional data from database if available"""
        if self.db_manager and hasattr(self.opportunity_data, 'get'):
            opp_id = self.opportunity_data.get('id')
            if opp_id:
                # Load user notes and status if they exist
                try:
                    # This would require implementing methods in DatabaseManager
                    # For now, we'll use placeholder data
                    pass
                except Exception as e:
                    print(f"Could not load additional data: {e}")
    
    def bookmark_opportunity(self):
        """Bookmark this opportunity"""
        QMessageBox.information(self, "Bookmarked", 
                               "Opportunity has been bookmarked!")
    
    def mark_as_applied(self):
        """Mark this opportunity as applied"""
        reply = QMessageBox.question(self, "Mark as Applied", 
                                   "Mark this opportunity as applied?",
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.application_status.setCurrentText("Applied")
            QMessageBox.information(self, "Applied", 
                                   "Opportunity marked as applied!")
    
    def export_details(self):
        """Export opportunity details to file"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Opportunity Details", 
            f"{self.opportunity_data.get('name', 'opportunity')}.txt",
            "Text Files (*.txt);;All Files (*)")
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"OPPORTUNITY DETAILS\n")
                    f.write(f"=" * 50 + "\n\n")
                    f.write(f"Title: {self.opportunity_data.get('name', 'N/A')}\n")
                    f.write(f"Organization: {self.opportunity_data.get('org_name', 'N/A')}\n")
                    f.write(f"Deadline: {self.opportunity_data.get('deadline', 'N/A')}\n")
                    f.write(f"Status: {self.opportunity_data.get('status', 'N/A')}\n")
                    f.write(f"Category: {self.opportunity_data.get('category', 'N/A')}\n")
                    f.write(f"URL: {self.opportunity_data.get('url', 'N/A')}\n\n")
                    f.write(f"DESCRIPTION\n")
                    f.write(f"-" * 20 + "\n")
                    f.write(f"{self.opportunity_data.get('description', 'N/A')}\n\n")
                    f.write(f"REQUIREMENTS\n")
                    f.write(f"-" * 20 + "\n")
                    f.write(f"{self.opportunity_data.get('requirements', 'N/A')}\n\n")
                    f.write(f"KEYWORDS\n")
                    f.write(f"-" * 20 + "\n")
                    f.write(f"{self.opportunity_data.get('keywords', 'N/A')}\n")
                
                QMessageBox.information(self, "Export Successful", 
                                       f"Details exported to {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", 
                                   f"Could not export details:\n{str(e)}")
    
    def save_notes(self):
        """Save user notes"""
        notes = self.notes_text.toPlainText()
        # Here you would save to database
        QMessageBox.information(self, "Notes Saved", 
                               "Your notes have been saved!")
    
    def update_application_status(self):
        """Update application status"""
        status = self.application_status.currentText()
        # Here you would save to database
        QMessageBox.information(self, "Status Updated", 
                               f"Application status updated to: {status}")


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
        
        # Add donor management tab if available
        if DONOR_FUNCTIONALITY_AVAILABLE:
            self.donor_widget = DonorManagementWidget()
            self.tab_widget.addTab(self.donor_widget, "💰 Donors & Foundations")
        
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
        
        self.db_path_input = QLineEdit(MAIN_DATABASE_PATH)
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
        # Get discovered opportunities instead of events
        opportunities = self.db_manager.get_opportunities(100)
        
        self.opportunities_table.setRowCount(len(opportunities))
        
        for row, opp in enumerate(opportunities):
            # opp structure: (id, title, description, deadline, category, funding, type, score, url, created)
            self.opportunities_table.setItem(row, 0, QTableWidgetItem(opp[1] or ""))  # title
            self.opportunities_table.setItem(row, 1, QTableWidgetItem(opp[6] or "Unknown"))  # type/organization
            self.opportunities_table.setItem(row, 2, QTableWidgetItem(opp[3] or ""))  # deadline
            self.opportunities_table.setItem(row, 3, QTableWidgetItem("Open"))  # status
            self.opportunities_table.setItem(row, 4, QTableWidgetItem(opp[9] or ""))  # created
            
            # Store full opportunity data in the first item for later retrieval
            item = self.opportunities_table.item(row, 0)
            if item:
                item.setData(0x0100, opp)  # Qt.UserRole = 0x0100
    
    def update_discovery_results(self, opportunities_count: int):
        """Update the latest discoveries display"""
        if opportunities_count > 0:
            # Get the latest opportunities to display
            latest_opportunities = self.db_manager.get_opportunities(10)
            
            # Clear and update the discoveries list
            self.discovery_results.clear()
            
            for opp in latest_opportunities:
                title = opp[1] or "Untitled Opportunity"
                source = opp[6] or "Unknown Source"
                score = opp[7] or 0.0
                
                list_item = QListWidgetItem(f"🎯 {title[:60]}...")
                list_item.setToolTip(f"Source: {source}\\nRelevance Score: {score:.2f}")
                self.discovery_results.addItem(list_item)
    
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
        
        # Refresh data displays
        self.refresh_opportunities_table()
        self.refresh_organization_filter()
        self.update_discovery_results(count)
        
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
            event_data = item.data(0x0100)  # Qt.UserRole = 0x0100
            if event_data:
                # Convert tuple to dict for easier access with all available fields
                opportunity_dict = {
                    'id': event_data[0] if len(event_data) > 0 else None,
                    'name': event_data[1] if len(event_data) > 1 else 'No Title',
                    'org_name': event_data[10] if len(event_data) > 10 else 'Unknown',
                    'deadline': event_data[4] if len(event_data) > 4 else 'Not specified',
                    'status': event_data[8] if len(event_data) > 8 else 'Unknown',
                    'description': event_data[5] if len(event_data) > 5 else 'No description',
                    'url': event_data[6] if len(event_data) > 6 else '',
                    'requirements': event_data[7] if len(event_data) > 7 else 'No requirements',
                    'category': event_data[9] if len(event_data) > 9 else 'General',
                    'keywords': event_data[11] if len(event_data) > 11 else 'No keywords',
                    'relevance_score': event_data[12] if len(event_data) > 12 else 0.0,
                    'estimated_funding': event_data[13] if len(event_data) > 13 else 'Not specified',
                    'source_url': event_data[14] if len(event_data) > 14 else '',
                    'created_at': event_data[15] if len(event_data) > 15 else 'Unknown'
                }
                
                detail_dialog = OpportunityDetailDialog(opportunity_dict, self.db_manager)
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
