#!/usr/bin/env python3
"""
Test script to verify imports work from project root
"""

import sys
import os

def test_imports():
    """Test that main modules can be imported from project root"""
    print("🧪 Testing Module Imports from Project Root")
    print("=" * 50)
    
    try:
        from src.database import DatabaseManager
        print("✅ DatabaseManager imported successfully")
        
        # Test database connection
        db = DatabaseManager()
        print(f"✅ Database Manager: Connected to {db.db_path}")
        
    except Exception as e:
        print(f"❌ DatabaseManager import failed: {e}")
    
    try:
        from src.config import MAIN_DATABASE_PATH, DATA_DIR, CONFIG_DIR
        print("✅ Config module imported successfully")
        print(f"   - Main DB: {MAIN_DATABASE_PATH}")
        print(f"   - Data dir: {DATA_DIR}")
        print(f"   - Config dir: {CONFIG_DIR}")
        
    except Exception as e:
        print(f"❌ Config module import failed: {e}")
    
    try:
        from src.donor_database import DonorDatabase
        print("✅ DonorDatabase imported successfully")
        
        # Test database connection
        donor_db = DonorDatabase()
        print(f"✅ Donor Database: Connected to {donor_db.db_path}")
        
    except Exception as e:
        print(f"❌ DonorDatabase import failed: {e}")
    
    try:
        from src.opportunity_monitor import OpportunityMonitor
        print("✅ OpportunityMonitor imported successfully")
        
    except Exception as e:
        print(f"❌ OpportunityMonitor import failed: {e}")
    
    try:
        from src.analytics_dashboard import ProposalAnalytics
        print("✅ ProposalAnalytics imported successfully")
        
    except Exception as e:
        print(f"❌ ProposalAnalytics import failed: {e}")

def test_directory_structure():
    """Verify directory structure"""
    print("\n📁 Directory Structure Verification")
    print("=" * 50)
    
    directories = [
        "src",
        "tests", 
        "data",
        "config",
        "docs",
        "scripts"
    ]
    
    for directory in directories:
        if os.path.exists(directory):
            print(f"✅ {directory}/ exists")
        else:
            print(f"❌ {directory}/ missing")
    
    # Check key files
    key_files = [
        "src/config.py",
        "src/database.py", 
        "src/gui.py",
        "data/proposal_ai.db",
        "config/monitoring_config.json",
        "README.md"
    ]
    
    for file_path in key_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} missing")

if __name__ == "__main__":
    test_directory_structure()
    test_imports()
    
    print("\n🎯 Summary")
    print("=" * 50)
    print("If all imports passed, the reorganization is successful!")
    print("You can now run the application with: python -m src.gui")
