#!/usr/bin/env python3
"""
Test script to verify GUI handles different data types properly
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from PyQt5.QtWidgets import QApplication

from src.gui.gui import OpportunityDetailDialog


def test_opportunity_dialog_types():
    """Test that OpportunityDetailDialog can handle various data types"""
    
    # Test data with mixed types (including problematic float for requirements)
    test_opportunity = {
        'name': 'Test Opportunity',
        'org_name': 'Test Organization', 
        'deadline': '2024-12-31',
        'status': 'Open',
        'url': 'https://example.com',
        'description': 'This is a test description',
        'requirements': 1.5,  # This was causing the error - float instead of string
    }
    
    print("Creating test opportunity dialog with mixed data types...")
    
    try:
        app = QApplication(sys.argv)
        dialog = OpportunityDetailDialog(test_opportunity)
        dialog.show()
        print("✅ Dialog created successfully - type conversion working!")
        app.quit()
        return True
    except Exception as e:
        print(f"❌ Error creating dialog: {e}")
        return False

if __name__ == "__main__":
    success = test_opportunity_dialog_types()
    sys.exit(0 if success else 1)
