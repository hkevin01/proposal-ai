#!/usr/bin/env python3
"""
Donor Management GUI Component
GUI for managing donors and viewing donor-opportunity matches
"""

import logging
import sys
from typing import Dict, List

from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from donor_enhanced_discovery import DonorEnhancedDiscovery

from .donor_database import Donor, DonorDatabase


class DonorSearchThread(QThread):
    """Thread for searching donors without blocking the UI"""
    results_ready = pyqtSignal(list)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, donor_db: DonorDatabase, query: str, 
                 focus_area: str = None, region: str = None):
        super().__init__()
        self.donor_db = donor_db
        self.query = query
        self.focus_area = focus_area
        self.region = region
    
    def run(self):
        try:
            results = self.donor_db.search_donors(
                self.query, self.focus_area, self.region)
            self.results_ready.emit(results)
        except Exception as e:
            self.error_occurred.emit(str(e))


class DonorMatchThread(QThread):
    """Thread for finding donor matches for opportunities"""
    matches_ready = pyqtSignal(list)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, discovery_engine: DonorEnhancedDiscovery, 
                 opportunity_id: int):
        super().__init__()
        self.discovery_engine = discovery_engine
        self.opportunity_id = opportunity_id
    
    def run(self):
        try:
            matches = self.discovery_engine.get_donor_recommendations(
                self.opportunity_id)
            self.matches_ready.emit(matches)
        except Exception as e:
            self.error_occurred.emit(str(e))


class DonorDetailDialog(QDialog):
    """Dialog for viewing and editing donor details"""
    
    def __init__(self, donor: Donor = None, parent=None):
        super().__init__(parent)
        self.donor = donor or Donor()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Donor Details")
        self.setModal(True)
        self.resize(600, 800)
        
        layout = QVBoxLayout()
        
        # Create form
        form_layout = QFormLayout()
        
        self.name_edit = QLineEdit(self.donor.name)
        form_layout.addRow("Name:", self.name_edit)
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(["individual", "foundation", "corporation", "government"])
        if self.donor.type:
            index = self.type_combo.findText(self.donor.type)
            if index >= 0:
                self.type_combo.setCurrentIndex(index)
        form_layout.addRow("Type:", self.type_combo)
        
        self.region_edit = QLineEdit(self.donor.region)
        form_layout.addRow("Region:", self.region_edit)
        
        self.country_edit = QLineEdit(self.donor.country)
        form_layout.addRow("Country:", self.country_edit)
        
        self.website_edit = QLineEdit(self.donor.website)
        form_layout.addRow("Website:", self.website_edit)
        
        self.email_edit = QLineEdit(self.donor.contact_email)
        form_layout.addRow("Email:", self.email_edit)
        
        self.phone_edit = QLineEdit(self.donor.contact_phone)
        form_layout.addRow("Phone:", self.phone_edit)
        
        self.giving_edit = QLineEdit(self.donor.giving_amount)
        form_layout.addRow("Giving Amount:", self.giving_edit)
        
        self.focus_edit = QLineEdit(", ".join(self.donor.focus_areas))
        form_layout.addRow("Focus Areas:", self.focus_edit)
        
        self.description_edit = QTextEdit(self.donor.description)
        self.description_edit.setMaximumHeight(100)
        form_layout.addRow("Description:", self.description_edit)
        
        self.process_edit = QTextEdit(self.donor.application_process)
        self.process_edit.setMaximumHeight(80)
        form_layout.addRow("Application Process:", self.process_edit)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def get_donor(self) -> Donor:
        """Get the donor with updated information from the form"""
        donor = Donor(
            id=self.donor.id,
            name=self.name_edit.text(),
            type=self.type_combo.currentText(),
            region=self.region_edit.text(),
            country=self.country_edit.text(),
            website=self.website_edit.text(),
            contact_email=self.email_edit.text(),
            contact_phone=self.phone_edit.text(),
            giving_amount=self.giving_edit.text(),
            focus_areas=[area.strip() for area in self.focus_edit.text().split(",") if area.strip()],
            description=self.description_edit.toPlainText(),
            application_process=self.process_edit.toPlainText()
        )
        return donor


class DonorManagementWidget(QWidget):
    """Widget for managing donors and viewing donor-opportunity matches"""
    
    def __init__(self):
        super().__init__()
        self.donor_db = DonorDatabase()
        self.discovery_engine = DonorEnhancedDiscovery()
        self.logger = logging.getLogger(__name__)
        self.init_ui()
        self.load_donors()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Search section
        search_group = QGroupBox("Search Donors")
        search_layout = QVBoxLayout()
        
        search_form = QHBoxLayout()
        search_form.addWidget(QLabel("Search:"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Enter keywords...")
        self.search_edit.returnPressed.connect(self.search_donors)
        search_form.addWidget(self.search_edit)
        
        search_form.addWidget(QLabel("Focus Area:"))
        self.focus_combo = QComboBox()
        self.focus_combo.addItems(["", "education", "health", "environment", 
                                  "technology", "space", "research"])
        search_form.addWidget(self.focus_combo)
        
        search_form.addWidget(QLabel("Region:"))
        self.region_combo = QComboBox()
        self.region_combo.addItems(["", "North America", "Europe", "Asia", 
                                   "Africa", "South America", "Global"])
        search_form.addWidget(self.region_combo)
        
        self.search_btn = QPushButton("Search")
        self.search_btn.clicked.connect(self.search_donors)
        search_form.addWidget(self.search_btn)
        
        search_layout.addLayout(search_form)
        search_group.setLayout(search_layout)
        layout.addWidget(search_group)
        
        # Main content splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Donor list section
        donor_section = QWidget()
        donor_layout = QVBoxLayout()
        
        donor_header = QHBoxLayout()
        donor_header.addWidget(QLabel("Donors"))
        
        self.add_donor_btn = QPushButton("Add Donor")
        self.add_donor_btn.clicked.connect(self.add_donor)
        donor_header.addWidget(self.add_donor_btn)
        
        self.edit_donor_btn = QPushButton("Edit Donor")
        self.edit_donor_btn.clicked.connect(self.edit_donor)
        donor_header.addWidget(self.edit_donor_btn)
        
        donor_layout.addLayout(donor_header)
        
        # Donor table
        self.donor_table = QTableWidget()
        self.donor_table.setColumnCount(6)
        self.donor_table.setHorizontalHeaderLabels([
            "Name", "Type", "Region", "Focus Areas", "Giving Amount", "Contact"
        ])
        self.donor_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.donor_table.itemSelectionChanged.connect(self.on_donor_selected)
        donor_layout.addWidget(self.donor_table)
        
        donor_section.setLayout(donor_layout)
        splitter.addWidget(donor_section)
        
        # Donor details section
        details_section = QWidget()
        details_layout = QVBoxLayout()
        
        details_layout.addWidget(QLabel("Donor Details"))
        
        self.details_scroll = QScrollArea()
        self.details_widget = QWidget()
        self.details_layout = QVBoxLayout()
        self.details_widget.setLayout(self.details_layout)
        self.details_scroll.setWidget(self.details_widget)
        self.details_scroll.setWidgetResizable(True)
        details_layout.addWidget(self.details_scroll)
        
        # Opportunity matches section
        matches_group = QGroupBox("Opportunity Matches")
        matches_layout = QVBoxLayout()
        
        self.matches_table = QTableWidget()
        self.matches_table.setColumnCount(4)
        self.matches_table.setHorizontalHeaderLabels([
            "Opportunity", "Agency", "Match Score", "Deadline"
        ])
        matches_layout.addWidget(self.matches_table)
        
        matches_group.setLayout(matches_layout)
        details_layout.addWidget(matches_group)
        
        details_section.setLayout(details_layout)
        splitter.addWidget(details_section)
        
        layout.addWidget(splitter)
        self.setLayout(layout)
    
    def load_donors(self):
        """Load all donors into the table"""
        try:
            donors = self.donor_db.get_donors(limit=100)
            self.populate_donor_table(donors)
        except Exception as e:
            self.logger.error(f"Error loading donors: {e}")
    
    def populate_donor_table(self, donors: List[Donor]):
        """Populate the donor table with donor data"""
        self.donor_table.setRowCount(len(donors))
        
        for row, donor in enumerate(donors):
            self.donor_table.setItem(row, 0, QTableWidgetItem(donor.name))
            self.donor_table.setItem(row, 1, QTableWidgetItem(donor.type))
            self.donor_table.setItem(row, 2, QTableWidgetItem(donor.region))
            self.donor_table.setItem(row, 3, QTableWidgetItem(", ".join(donor.focus_areas[:2])))
            self.donor_table.setItem(row, 4, QTableWidgetItem(donor.giving_amount))
            
            contact = donor.contact_email or donor.contact_phone or "N/A"
            self.donor_table.setItem(row, 5, QTableWidgetItem(contact))
            
            # Store donor ID in first item
            item = self.donor_table.item(row, 0)
            item.setData(Qt.UserRole, donor.id)
        
        self.donor_table.resizeColumnsToContents()
    
    def search_donors(self):
        """Search for donors based on the search criteria"""
        query = self.search_edit.text()
        focus_area = self.focus_combo.currentText() if self.focus_combo.currentText() else None
        region = self.region_combo.currentText() if self.region_combo.currentText() else None
        
        # Start search thread
        self.search_thread = DonorSearchThread(self.donor_db, query, focus_area, region)
        self.search_thread.results_ready.connect(self.populate_donor_table)
        self.search_thread.error_occurred.connect(self.handle_error)
        self.search_thread.start()
        
        self.search_btn.setText("Searching...")
        self.search_btn.setEnabled(False)
        self.search_thread.finished.connect(lambda: self.search_btn.setText("Search"))
        self.search_thread.finished.connect(lambda: self.search_btn.setEnabled(True))
    
    def on_donor_selected(self):
        """Handle donor selection in the table"""
        current_row = self.donor_table.currentRow()
        if current_row < 0:
            return
        
        item = self.donor_table.item(current_row, 0)
        donor_id = item.data(Qt.UserRole)
        
        if donor_id:
            self.show_donor_details(donor_id)
    
    def show_donor_details(self, donor_id: int):
        """Show detailed information about a donor"""
        try:
            donor = self.donor_db.get_donor_by_id(donor_id)
            if not donor:
                return
            
            # Clear previous details
            for i in reversed(range(self.details_layout.count())):
                self.details_layout.itemAt(i).widget().setParent(None)
            
            # Add donor information
            info_label = QLabel(f"<h3>{donor.name}</h3>")
            self.details_layout.addWidget(info_label)
            
            details = [
                ("Type", donor.type),
                ("Region", donor.region),
                ("Country", donor.country),
                ("Focus Areas", ", ".join(donor.focus_areas)),
                ("Giving Amount", donor.giving_amount),
                ("Website", donor.website),
                ("Email", donor.contact_email),
                ("Phone", donor.contact_phone)
            ]
            
            for label, value in details:
                if value:
                    detail_label = QLabel(f"<b>{label}:</b> {value}")
                    detail_label.setWordWrap(True)
                    self.details_layout.addWidget(detail_label)
            
            if donor.description:
                desc_label = QLabel(f"<b>Description:</b><br>{donor.description}")
                desc_label.setWordWrap(True)
                self.details_layout.addWidget(desc_label)
            
            # Load opportunity matches
            self.load_donor_matches(donor_id)
            
        except Exception as e:
            self.logger.error(f"Error showing donor details: {e}")
    
    def load_donor_matches(self, donor_id: int):
        """Load opportunity matches for a donor"""
        try:
            portfolio = self.discovery_engine.get_donor_portfolio(donor_id)
            opportunities = portfolio.get('matched_opportunities', [])
            
            self.matches_table.setRowCount(len(opportunities))
            
            for row, opp in enumerate(opportunities):
                self.matches_table.setItem(row, 0, QTableWidgetItem(opp.get('title', 'N/A')))
                self.matches_table.setItem(row, 1, QTableWidgetItem(opp.get('agency', 'N/A')))
                self.matches_table.setItem(row, 2, QTableWidgetItem(f"{opp.get('match_score', 0):.2f}"))
                self.matches_table.setItem(row, 3, QTableWidgetItem(opp.get('deadline', 'N/A')))
            
            self.matches_table.resizeColumnsToContents()
            
        except Exception as e:
            self.logger.error(f"Error loading donor matches: {e}")
    
    def add_donor(self):
        """Add a new donor"""
        dialog = DonorDetailDialog(parent=self)
        if dialog.exec_() == QDialog.Accepted:
            donor = dialog.get_donor()
            try:
                self.donor_db.add_donor(donor)
                self.load_donors()  # Refresh the table
            except Exception as e:
                self.logger.error(f"Error adding donor: {e}")
    
    def edit_donor(self):
        """Edit the selected donor"""
        current_row = self.donor_table.currentRow()
        if current_row < 0:
            return
        
        item = self.donor_table.item(current_row, 0)
        donor_id = item.data(Qt.UserRole)
        
        if donor_id:
            donor = self.donor_db.get_donor_by_id(donor_id)
            if donor:
                dialog = DonorDetailDialog(donor, parent=self)
                if dialog.exec_() == QDialog.Accepted:
                    updated_donor = dialog.get_donor()
                    try:
                        self.donor_db.add_donor(updated_donor)  # This will update existing
                        self.load_donors()  # Refresh the table
                        self.show_donor_details(donor_id)  # Refresh details
                    except Exception as e:
                        self.logger.error(f"Error updating donor: {e}")
    
    def handle_error(self, error_message: str):
        """Handle errors from background threads"""
        self.logger.error(f"Background operation error: {error_message}")


def main():
    """Test the donor management widget"""
    import sys

    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    widget = DonorManagementWidget()
    widget.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
