#!/usr/bin/env python3
"""
Test script to verify the reorganized src structure works
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test imports from the reorganized structure"""
    print("🧪 Testing Reorganized Source Structure")
    print("=" * 50)
    
    success_count = 0
    total_tests = 0
    
    # Test core imports
    try:
        from src.core.config import MAIN_DATABASE_PATH, DATA_DIR
        print("✅ Core config import successful")
        success_count += 1
    except Exception as e:
        print(f"❌ Core config import failed: {e}")
    total_tests += 1
    
    try:
        from src.core.database import DatabaseManager
        print("✅ Core database import successful")
        success_count += 1
    except Exception as e:
        print(f"❌ Core database import failed: {e}")
    total_tests += 1
    
    # Test donor imports
    try:
        from src.donors.donor_database import DonorDatabase
        print("✅ Donor database import successful")
        success_count += 1
    except Exception as e:
        print(f"❌ Donor database import failed: {e}")
    total_tests += 1
    
    # Test monitoring imports  
    try:
        from src.monitoring.analytics_dashboard import ProposalAnalytics
        print("✅ Analytics dashboard import successful")
        success_count += 1
    except Exception as e:
        print(f"❌ Analytics dashboard import failed: {e}")
    total_tests += 1
    
    # Test utils imports
    try:
        from src.utils.sample_data import create_sample_data
        print("✅ Utils sample_data import successful")
        success_count += 1
    except Exception as e:
        print(f"❌ Utils sample_data import failed: {e}")
    total_tests += 1
    
    print(f"\n📊 Results: {success_count}/{total_tests} imports successful")
    return success_count == total_tests

def test_database_connections():
    """Test that database connections still work"""
    print("\n🗄️ Testing Database Connections")
    print("=" * 50)
    
    try:
        from src.core.database import DatabaseManager
        db = DatabaseManager()
        print(f"✅ Main database connected: {db.db_path}")
        
        from src.donors.donor_database import DonorDatabase  
        donor_db = DonorDatabase()
        print(f"✅ Donor database connected: {donor_db.db_path}")
        
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def main():
    """Main test function"""
    print("🔧 Testing Reorganized Proposal AI Structure")
    print("=" * 60)
    
    imports_ok = test_imports()
    db_ok = test_database_connections()
    
    print(f"\n🎯 Overall Status")
    print("=" * 50)
    if imports_ok and db_ok:
        print("✅ All tests passed! Reorganization successful.")
        print("\n🚀 You can now run:")
        print("   python -m src.main")
        print("   python -m src.gui.gui")
        return 0
    else:
        print("❌ Some tests failed. Check import paths.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
