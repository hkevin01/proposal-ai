"""
Enhanced GUI Tab for Profile Management and Opportunity Matching
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Optional

from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from database import DatabaseManager

try:
    from enhanced_discovery_engine import EnhancedOpportunityDiscoverer
    from resume_parser import ProfileManager, ResumeParser
    ENHANCED_FEATURES = True
except ImportError:
    ENHANCED_FEATURES = False
    print("Warning: Enhanced features not available. Install required packages.")


class EnhancedDiscoveryWorker(QThread):
    """Worker thread for enhanced opportunity discovery"""
    progress = pyqtSignal(str)
    opportunity_found = pyqtSignal(dict)
    finished = pyqtSignal(int)
    error = pyqtSignal(str)
    
    def __init__(self, max_per_source=10):
        super().__init__()
        self.max_per_source = max_per_source
        self.is_cancelled = False
    
    def run(self):
        try:
            if not ENHANCED_FEATURES:
                self.error.emit("Enhanced discovery features not available")
                return
            
            self.progress.emit("Initializing enhanced discovery engine...")
            discoverer = EnhancedOpportunityDiscoverer()
            
            self.progress.emit("Discovering opportunities from 50+ sources...")
            opportunities = discoverer.discover_opportunities(self.max_per_source)
            
            self.progress.emit(f"Processing {len(opportunities)} opportunities...")
            
            # Emit each opportunity for real-time updates
            for i, opp in enumerate(opportunities):
                if self.is_cancelled:
                    break
                self.opportunity_found.emit(opp)
                if i % 10 == 0:
                    self.progress.emit(f"Processed {i+1}/{len(opportunities)} opportunities")
            
            self.progress.emit("Saving opportunities to database...")
            discoverer.save_opportunities_to_database(opportunities)
            
            self.finished.emit(len(opportunities))
            
        except Exception as e:
            self.error.emit(str(e))
    
    def cancel(self):
        self.is_cancelled = True


class ProfileUploadWorker(QThread):
    """Worker thread for resume parsing"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, user_id: int, file_path: str):
        super().__init__()
        self.user_id = user_id
        self.file_path = file_path
    
    def run(self):
        try:
            if not ENHANCED_FEATURES:
                self.error.emit("Profile parsing features not available")
                return
            
            self.progress.emit("Parsing resume file...")
            profile_manager = ProfileManager()
            
            self.progress.emit("Extracting text and analyzing content...")
            result = profile_manager.upload_resume(self.user_id, self.file_path)
            
            self.progress.emit("Profile parsing complete!")
            self.finished.emit(result)
            
        except Exception as e:
            self.error.emit(str(e))


class OpportunityMatchingWorker(QThread):
    """Worker thread for matching opportunities to user profile"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    
    def __init__(self, user_id: int, profile_data: Dict, top_n: int = 50):
        super().__init__()
        self.user_id = user_id
        self.profile_data = profile_data
        self.top_n = top_n
    
    def run(self):
        try:
            if not ENHANCED_FEATURES:
                self.error.emit("Opportunity matching features not available")
                return
            
            self.progress.emit("Loading opportunities from database...")
            discoverer = EnhancedOpportunityDiscoverer()
            db_manager = DatabaseManager()
            
            # Get all opportunities from database
            conn = db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM scraped_opportunities")
            rows = cursor.fetchall()
            conn.close()
            
            # Convert to opportunity format
            opportunities = []
            for row in rows:
                try:
                    raw_data = json.loads(row[7]) if row[7] else {}
                    opp = {
                        'id': row[0],
                        'source_url': row[1],
                        'title': row[2],
                        'description': row[3],
                        'deadline': row[4],
                        'primary_category': row[5],
                        'keywords': json.loads(row[6]) if row[6] else [],
                        'relevance_score': row[9] if len(row) > 9 else 0.5,
                        **raw_data
                    }
                    opportunities.append(opp)
                except:
                    continue
            
            self.progress.emit(f"Matching {len(opportunities)} opportunities to your profile...")
            
            # Match opportunities
            matched_opportunities = discoverer.match_opportunities_to_profile(
                self.profile_data, opportunities, self.top_n
            )
            
            self.progress.emit("Saving matches to database...")
            
            # Save matches to database
            for opp in matched_opportunities:
                db_manager.add_opportunity_match(
                    user_id=self.user_id,
                    opportunity_id=opp.get('id', 0),
                    profile_match_score=opp.get('profile_match_score', 0),
                    relevance_score=opp.get('relevance_score', 0),
                    combined_score=opp.get('combined_score', 0),
                    match_keywords=json.dumps(opp.get('keywords', [])),
                    match_categories=json.dumps(opp.get('categories', []))
                )
            
            self.finished.emit(matched_opportunities)
            
        except Exception as e:
            self.error.emit(str(e))


class EnhancedDiscoveryTab(QWidget):
    """Enhanced discovery tab with profile matching"""
    
    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db_manager = db_manager
        self.current_user_id = 1  # Default user for demo
        self.discovery_worker = None
        self.profile_worker = None
        self.matching_worker = None
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Create tab widget for different sections
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # Profile Management Tab
        profile_tab = self.create_profile_tab()
        tab_widget.addTab(profile_tab, "👤 Profile")
        
        # Enhanced Discovery Tab
        discovery_tab = self.create_enhanced_discovery_tab()
        tab_widget.addTab(discovery_tab, "🔍 Enhanced Discovery")
        
        # Opportunity Matching Tab
        matching_tab = self.create_matching_tab()
        tab_widget.addTab(matching_tab, "🎯 Smart Matching")
        
        # Results Tab
        results_tab = self.create_results_tab()
        tab_widget.addTab(results_tab, "📊 Results")
    
    def create_profile_tab(self):
        """Create profile management tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Profile Upload Section
        upload_group = QGroupBox("📁 Resume/Profile Upload")
        upload_layout = QVBoxLayout()
        
        # Upload instructions
        instructions = QLabel(
            "Upload your resume (PDF, Word, or Text) to enable intelligent opportunity matching.\\n"
            "The system will extract your skills, experience, and research interests."
        )
        instructions.setWordWrap(True)
        upload_layout.addWidget(instructions)
        
        # Upload button
        upload_button = QPushButton("📁 Upload Resume File")
        upload_button.clicked.connect(self.upload_resume_file)
        upload_layout.addWidget(upload_button)
        
        # Manual text entry
        manual_label = QLabel("Or enter your profile information manually:")
        upload_layout.addWidget(manual_label)
        
        self.profile_text_edit = QTextEdit()
        self.profile_text_edit.setPlaceholderText(
            "Enter your background, skills, experience, education, research interests, etc.\\n\\n"
            "Example:\\n"
            "PhD in Computer Science with 5 years experience in machine learning and space technology.\\n"
            "Skills: Python, TensorFlow, satellite data processing, orbital mechanics.\\n"
            "Research interests: Autonomous space systems, AI for space applications."
        )
        self.profile_text_edit.setMaximumHeight(200)
        upload_layout.addWidget(self.profile_text_edit)
        
        save_text_button = QPushButton("💾 Save Profile Text")
        save_text_button.clicked.connect(self.save_profile_text)
        upload_layout.addWidget(save_text_button)
        
        # Progress bar
        self.profile_progress = QProgressBar()
        self.profile_progress.setVisible(False)
        upload_layout.addWidget(self.profile_progress)
        
        # Status label
        self.profile_status = QLabel("No profile uploaded yet")
        upload_layout.addWidget(self.profile_status)
        
        upload_group.setLayout(upload_layout)
        layout.addWidget(upload_group)
        
        # Current Profile Display
        profile_display_group = QGroupBox("📋 Current Profile Summary")
        profile_display_layout = QVBoxLayout()
        
        self.profile_summary = QTextEdit()
        self.profile_summary.setReadOnly(True)
        self.profile_summary.setMaximumHeight(300)
        profile_display_layout.addWidget(self.profile_summary)
        
        refresh_profile_button = QPushButton("🔄 Refresh Profile")
        refresh_profile_button.clicked.connect(self.load_current_profile)
        profile_display_layout.addWidget(refresh_profile_button)
        
        profile_display_group.setLayout(profile_display_layout)
        layout.addWidget(profile_display_group)
        
        layout.addStretch()
        
        # Load current profile on startup
        self.load_current_profile()
        
        return widget
    
    def create_enhanced_discovery_tab(self):
        """Create enhanced discovery tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Discovery Configuration
        config_group = QGroupBox("⚙️ Enhanced Discovery Configuration")
        config_layout = QFormLayout()
        
        self.max_per_source = QSpinBox()
        self.max_per_source.setRange(5, 100)
        self.max_per_source.setValue(20)
        config_layout.addRow("Max results per source:", self.max_per_source)
        
        self.include_sources = QComboBox()
        self.include_sources.addItems([
            "All Sources (50+)", "Government Only", "Academic Only", 
            "Private Sector Only", "International Only"
        ])
        config_layout.addRow("Source filter:", self.include_sources)
        
        config_group.setLayout(config_layout)
        layout.addWidget(config_group)
        
        # Discovery Control
        control_group = QGroupBox("🎮 Discovery Control")
        control_layout = QVBoxLayout()
        
        # Status and progress
        self.discovery_status = QLabel("Ready to discover opportunities from 50+ sources")
        control_layout.addWidget(self.discovery_status)
        
        self.discovery_progress = QProgressBar()
        self.discovery_progress.setVisible(False)
        control_layout.addWidget(self.discovery_progress)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.start_discovery_btn = QPushButton("🚀 Start Enhanced Discovery")
        self.start_discovery_btn.clicked.connect(self.start_enhanced_discovery)
        button_layout.addWidget(self.start_discovery_btn)
        
        self.stop_discovery_btn = QPushButton("⏹ Stop Discovery")
        self.stop_discovery_btn.setEnabled(False)
        self.stop_discovery_btn.clicked.connect(self.stop_discovery)
        button_layout.addWidget(self.stop_discovery_btn)
        
        button_layout.addStretch()
        
        control_layout.addLayout(button_layout)
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
        
        # Live Results Preview
        preview_group = QGroupBox("👀 Live Discovery Preview")
        preview_layout = QVBoxLayout()
        
        self.discovery_preview = QListWidget()
        preview_layout.addWidget(self.discovery_preview)
        
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        return widget
    
    def create_matching_tab(self):
        """Create opportunity matching tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Matching Configuration
        config_group = QGroupBox("🎯 Matching Configuration")
        config_layout = QFormLayout()
        
        self.match_top_n = QSpinBox()
        self.match_top_n.setRange(10, 200)
        self.match_top_n.setValue(50)
        config_layout.addRow("Number of top matches:", self.match_top_n)
        
        self.auto_match = QCheckBox("Auto-match after discovery")
        self.auto_match.setChecked(True)
        config_layout.addRow("", self.auto_match)
        
        config_group.setLayout(config_layout)
        layout.addWidget(config_group)
        
        # Matching Control
        control_group = QGroupBox("🎮 Matching Control")
        control_layout = QVBoxLayout()
        
        self.matching_status = QLabel("Upload a profile to enable smart matching")
        control_layout.addWidget(self.matching_status)
        
        self.matching_progress = QProgressBar()
        self.matching_progress.setVisible(False)
        control_layout.addWidget(self.matching_progress)
        
        self.start_matching_btn = QPushButton("🎯 Find My Best Matches")
        self.start_matching_btn.clicked.connect(self.start_opportunity_matching)
        control_layout.addWidget(self.start_matching_btn)
        
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
        
        # Matching Results Preview
        results_group = QGroupBox("📈 Top Matches Preview")
        results_layout = QVBoxLayout()
        
        self.matches_preview = QTableWidget()
        self.matches_preview.setColumnCount(4)
        self.matches_preview.setHorizontalHeaderLabels([
            "Title", "Organization", "Match Score", "Relevance"
        ])
        results_layout.addWidget(self.matches_preview)
        
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)
        
        return widget
    
    def create_results_tab(self):
        """Create results summary tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Summary Statistics
        stats_group = QGroupBox("📊 Discovery Statistics")
        stats_layout = QFormLayout()
        
        self.total_opportunities_label = QLabel("0")
        stats_layout.addRow("Total opportunities found:", self.total_opportunities_label)
        
        self.matched_opportunities_label = QLabel("0")
        stats_layout.addRow("Matched to your profile:", self.matched_opportunities_label)
        
        self.top_categories_label = QLabel("None")
        stats_layout.addRow("Top categories:", self.top_categories_label)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # Detailed Results Table
        results_group = QGroupBox("📋 All Discovered Opportunities")
        results_layout = QVBoxLayout()
        
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(6)
        self.results_table.setHorizontalHeaderLabels([
            "Title", "Organization", "Category", "Deadline", "Match Score", "Actions"
        ])
        results_layout.addWidget(self.results_table)
        
        # Export buttons
        export_layout = QHBoxLayout()
        
        export_csv_btn = QPushButton("📄 Export to CSV")
        export_csv_btn.clicked.connect(self.export_results_csv)
        export_layout.addWidget(export_csv_btn)
        
        export_json_btn = QPushButton("📄 Export to JSON")
        export_json_btn.clicked.connect(self.export_results_json)
        export_layout.addWidget(export_json_btn)
        
        export_layout.addStretch()
        
        results_layout.addLayout(export_layout)
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)
        
        return widget
    
    def upload_resume_file(self):
        """Handle resume file upload"""
        if not ENHANCED_FEATURES:
            QMessageBox.warning(self, "Feature Unavailable", 
                              "Resume parsing requires additional packages.\\n"
                              "Install with: pip install PyPDF2 python-docx")
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Resume File", "", 
            "All Supported (*.pdf *.docx *.doc *.txt);;PDF Files (*.pdf);;"
            "Word Documents (*.docx *.doc);;Text Files (*.txt)"
        )
        
        if file_path:
            self.profile_progress.setVisible(True)
            self.profile_progress.setRange(0, 0)  # Indeterminate
            self.profile_status.setText("Uploading and parsing resume...")
            
            # Start worker thread
            self.profile_worker = ProfileUploadWorker(self.current_user_id, file_path)
            self.profile_worker.progress.connect(self.profile_status.setText)
            self.profile_worker.finished.connect(self.profile_upload_finished)
            self.profile_worker.error.connect(self.profile_upload_error)
            self.profile_worker.start()
    
    def save_profile_text(self):
        """Save manually entered profile text"""
        text = self.profile_text_edit.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "No Content", "Please enter some profile information.")
            return
        
        if not ENHANCED_FEATURES:
            QMessageBox.warning(self, "Feature Unavailable", 
                              "Profile parsing requires additional packages.")
            return
        
        try:
            profile_manager = ProfileManager()
            profile_id = profile_manager.update_profile_text(self.current_user_id, text)
            
            self.profile_status.setText("Profile text saved successfully!")
            self.load_current_profile()
            
            QMessageBox.information(self, "Success", 
                                  f"Profile saved with ID: {profile_id}")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save profile: {e}")
    
    def load_current_profile(self):
        """Load and display current user profile"""
        if not ENHANCED_FEATURES:
            self.profile_summary.setText("Profile features require additional packages.")
            return
        
        try:
            profile_manager = ProfileManager()
            profile = profile_manager.get_profile(self.current_user_id)
            
            if profile:
                summary_parts = []
                
                if profile.get('specialization'):
                    summary_parts.append(f"🎯 Specialization: {profile['specialization']}")
                
                if profile.get('industry'):
                    summary_parts.append(f"🏢 Industry: {profile['industry']}")
                
                if profile.get('skills'):
                    summary_parts.append(f"🛠️ Skills: {profile['skills'][:200]}...")
                
                if profile.get('experience'):
                    summary_parts.append(f"💼 Experience: {profile['experience'][:200]}...")
                
                if profile.get('education'):
                    summary_parts.append(f"🎓 Education: {profile['education'][:200]}...")
                
                if profile.get('research_interests'):
                    summary_parts.append(f"🔬 Research: {profile['research_interests'][:200]}...")
                
                self.profile_summary.setText("\\n\\n".join(summary_parts))
                self.profile_status.setText("Profile loaded successfully")
                
                # Enable matching
                self.matching_status.setText("Profile loaded - ready for smart matching!")
                self.start_matching_btn.setEnabled(True)
                
            else:
                self.profile_summary.setText("No profile found. Please upload a resume or enter profile information.")
                self.profile_status.setText("No profile found")
                self.start_matching_btn.setEnabled(False)
        
        except Exception as e:
            self.profile_summary.setText(f"Error loading profile: {e}")
            self.profile_status.setText("Error loading profile")
    
    def profile_upload_finished(self, result: Dict):
        """Handle successful profile upload"""
        self.profile_progress.setVisible(False)
        self.profile_status.setText(f"Resume parsed successfully! Profile ID: {result['profile_id']}")
        
        # Refresh profile display
        self.load_current_profile()
        
        # Show success message
        QMessageBox.information(self, "Success", 
                              "Resume uploaded and parsed successfully!\\n"
                              f"File saved to: {result['file_path']}")
    
    def profile_upload_error(self, error_message: str):
        """Handle profile upload error"""
        self.profile_progress.setVisible(False)
        self.profile_status.setText(f"Error: {error_message}")
        QMessageBox.critical(self, "Upload Error", f"Failed to upload resume:\\n{error_message}")
    
    def start_enhanced_discovery(self):
        """Start enhanced opportunity discovery"""
        if not ENHANCED_FEATURES:
            QMessageBox.warning(self, "Feature Unavailable", 
                              "Enhanced discovery requires additional packages.\\n"
                              "Install with: pip install requests beautifulsoup4 scikit-learn")
            return
        
        self.start_discovery_btn.setEnabled(False)
        self.stop_discovery_btn.setEnabled(True)
        self.discovery_progress.setVisible(True)
        self.discovery_progress.setRange(0, 0)  # Indeterminate
        self.discovery_preview.clear()
        
        # Start worker thread
        max_per_source = self.max_per_source.value()
        self.discovery_worker = EnhancedDiscoveryWorker(max_per_source)
        self.discovery_worker.progress.connect(self.discovery_status.setText)
        self.discovery_worker.opportunity_found.connect(self.add_opportunity_to_preview)
        self.discovery_worker.finished.connect(self.discovery_finished)
        self.discovery_worker.error.connect(self.discovery_error)
        self.discovery_worker.start()
    
    def stop_discovery(self):
        """Stop ongoing discovery"""
        if self.discovery_worker:
            self.discovery_worker.cancel()
            self.discovery_worker.wait()
        
        self.start_discovery_btn.setEnabled(True)
        self.stop_discovery_btn.setEnabled(False)
        self.discovery_progress.setVisible(False)
        self.discovery_status.setText("Discovery stopped by user")
    
    def add_opportunity_to_preview(self, opportunity: Dict):
        """Add newly discovered opportunity to preview"""
        title = opportunity.get('title', 'Unknown')[:80]
        org = opportunity.get('organization', 'Unknown')
        score = opportunity.get('relevance_score', 0)
        
        item_text = f"[{score:.2f}] {title} - {org}"
        self.discovery_preview.addItem(item_text)
        
        # Keep only last 50 items
        if self.discovery_preview.count() > 50:
            self.discovery_preview.takeItem(0)
    
    def discovery_finished(self, count: int):
        """Handle discovery completion"""
        self.start_discovery_btn.setEnabled(True)
        self.stop_discovery_btn.setEnabled(False)
        self.discovery_progress.setVisible(False)
        
        self.discovery_status.setText(f"Discovery completed! Found {count} opportunities.")
        self.total_opportunities_label.setText(str(count))
        
        # Auto-start matching if enabled and profile exists
        if self.auto_match.isChecked() and self.start_matching_btn.isEnabled():
            self.start_opportunity_matching()
        
        # Show completion message
        QMessageBox.information(self, "Discovery Complete", 
                              f"Successfully discovered {count} opportunities from 50+ sources!\\n"
                              "Check the Results tab for detailed information.")
    
    def discovery_error(self, error_message: str):
        """Handle discovery error"""
        self.start_discovery_btn.setEnabled(True)
        self.stop_discovery_btn.setEnabled(False)
        self.discovery_progress.setVisible(False)
        
        self.discovery_status.setText(f"Error: {error_message}")
        QMessageBox.critical(self, "Discovery Error", 
                           f"An error occurred during discovery:\\n{error_message}")
    
    def start_opportunity_matching(self):
        """Start opportunity matching"""
        if not ENHANCED_FEATURES:
            QMessageBox.warning(self, "Feature Unavailable", 
                              "Opportunity matching requires additional packages.")
            return
        
        # Get current profile
        try:
            profile_manager = ProfileManager()
            profile = profile_manager.get_profile(self.current_user_id)
            
            if not profile:
                QMessageBox.warning(self, "No Profile", 
                                  "Please upload a resume or enter profile information first.")
                return
            
            # Convert profile to dict for matching
            profile_data = {
                'skills': profile.get('skills', ''),
                'experience': profile.get('experience', ''),
                'education': profile.get('education', ''),
                'research_interests': profile.get('research_interests', ''),
                'expertise': profile.get('expertise', ''),
                'keywords': profile.get('keywords', ''),
                'specialization': profile.get('specialization', ''),
                'industry': profile.get('industry', ''),
                'technologies': profile.get('technologies', ''),
            }
            
            self.matching_progress.setVisible(True)
            self.matching_progress.setRange(0, 0)
            self.start_matching_btn.setEnabled(False)
            
            # Start matching worker
            top_n = self.match_top_n.value()
            self.matching_worker = OpportunityMatchingWorker(
                self.current_user_id, profile_data, top_n
            )
            self.matching_worker.progress.connect(self.matching_status.setText)
            self.matching_worker.finished.connect(self.matching_finished)
            self.matching_worker.error.connect(self.matching_error)
            self.matching_worker.start()
        
        except Exception as e:
            QMessageBox.critical(self, "Matching Error", f"Failed to start matching: {e}")
    
    def matching_finished(self, matched_opportunities: List[Dict]):
        """Handle matching completion"""
        self.matching_progress.setVisible(False)
        self.start_matching_btn.setEnabled(True)
        
        count = len(matched_opportunities)
        self.matching_status.setText(f"Found {count} relevant opportunities!")
        self.matched_opportunities_label.setText(str(count))
        
        # Update preview table
        self.matches_preview.setRowCount(min(count, 10))  # Show top 10
        
        for i, opp in enumerate(matched_opportunities[:10]):
            self.matches_preview.setItem(i, 0, QTableWidgetItem(opp.get('title', '')[:50]))
            self.matches_preview.setItem(i, 1, QTableWidgetItem(opp.get('organization', '')))
            self.matches_preview.setItem(i, 2, QTableWidgetItem(f"{opp.get('profile_match_score', 0):.3f}"))
            self.matches_preview.setItem(i, 3, QTableWidgetItem(f"{opp.get('relevance_score', 0):.3f}"))
        
        # Show success message
        QMessageBox.information(self, "Matching Complete", 
                              f"Found {count} opportunities matched to your profile!\\n"
                              "Check the Results tab for detailed information.")
    
    def matching_error(self, error_message: str):
        """Handle matching error"""
        self.matching_progress.setVisible(False)
        self.start_matching_btn.setEnabled(True)
        
        self.matching_status.setText(f"Error: {error_message}")
        QMessageBox.critical(self, "Matching Error", 
                           f"An error occurred during matching:\\n{error_message}")
    
    def export_results_csv(self):
        """Export results to CSV"""
        QMessageBox.information(self, "Export", "CSV export feature coming soon!")
    
    def export_results_json(self):
        """Export results to JSON"""
        QMessageBox.information(self, "Export", "JSON export feature coming soon!")
