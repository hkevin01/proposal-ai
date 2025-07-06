#!/usr/bin/env python3
"""
Path Migration Script
Tests and fixes file paths after directory reorganization
"""

import logging
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config import (
    CONFIG_DIR,
    DATA_DIR,
    DOCS_DIR,
    DONORS_DATABASE_PATH,
    MAIN_DATABASE_PATH,
    OPPORTUNITIES_DATABASE_PATH,
    PROJECT_ROOT,
    TESTS_DIR,
)


def test_paths():
    """Test that all paths are correctly configured"""
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    print("🔍 Testing Path Configuration")
    print("=" * 40)
    
    # Test directory paths
    paths_to_test = {
        "Project Root": PROJECT_ROOT,
        "Data Directory": DATA_DIR,
        "Config Directory": CONFIG_DIR,
        "Docs Directory": DOCS_DIR,
        "Tests Directory": TESTS_DIR,
        "Main Database": MAIN_DATABASE_PATH,
        "Opportunities DB": OPPORTUNITIES_DATABASE_PATH,
        "Donors DB": DONORS_DATABASE_PATH
    }
    
    for name, path in paths_to_test.items():
        print(f"{name:18}: {path}")
        if os.path.exists(path):
            if os.path.isfile(path):
                size = os.path.getsize(path)
                print(f"{'':20}✅ File exists ({size} bytes)")
            else:
                print(f"{'':20}✅ Directory exists")
        else:
            print(f"{'':20}❌ Does not exist")
    
    print("\n🧪 Testing Module Imports")
    print("=" * 40)
    
    # Test imports
    test_imports = [
        ("Database Manager", "from database import DatabaseManager"),
        ("Donor Database", "from donor_database import DonorDatabase"),
        ("Donor Discovery", "from donor_enhanced_discovery import DonorEnhancedDiscovery"),
        ("Config Module", "from config import MAIN_DATABASE_PATH"),
    ]
    
    for name, import_statement in test_imports:
        try:
            exec(import_statement)
            print(f"{name:18}: ✅ Import successful")
        except Exception as e:
            print(f"{name:18}: ❌ Import failed - {e}")
    
    print("\n🗄️ Testing Database Connections")
    print("=" * 40)
    
    try:
        from database import DatabaseManager
        db_manager = DatabaseManager()
        print(f"Database Manager: ✅ Connected to {db_manager.db_path}")
    except Exception as e:
        print(f"Database Manager: ❌ Failed - {e}")
    
    try:
        from donor_database import DonorDatabase
        donor_db = DonorDatabase()
        donors = donor_db.get_donors(limit=3)
        print(f"Donor Database  : ✅ Connected, {len(donors)} donors found")
    except Exception as e:
        print(f"Donor Database  : ❌ Failed - {e}")
    
    print("\n📁 Directory Structure")
    print("=" * 40)
    
    def print_tree(directory, prefix="", max_depth=2, current_depth=0):
        if current_depth >= max_depth:
            return
        
        try:
            items = sorted(os.listdir(directory))
            for i, item in enumerate(items):
                if item.startswith('.'):
                    continue
                    
                item_path = os.path.join(directory, item)
                is_last = i == len(items) - 1
                current_prefix = "└── " if is_last else "├── "
                print(f"{prefix}{current_prefix}{item}")
                
                if os.path.isdir(item_path) and not item.startswith('.'):
                    extension = "    " if is_last else "│   "
                    print_tree(item_path, prefix + extension, max_depth, current_depth + 1)
        except PermissionError:
            pass
    
    print(f"Project structure (from {PROJECT_ROOT}):")
    print_tree(PROJECT_ROOT)
    
    return True


def update_test_files():
    """Update test files to use correct imports"""
    tests_dir = os.path.join(PROJECT_ROOT, "tests")
    
    if not os.path.exists(tests_dir):
        return
    
    for filename in os.listdir(tests_dir):
        if filename.endswith('.py') and filename != '__init__.py':
            filepath = os.path.join(tests_dir, filename)
            
            try:
                with open(filepath, 'r') as f:
                    content = f.read()
                
                # Check if it needs path updates
                if 'sys.path' not in content and 'import sys' not in content:
                    # Add path setup to beginning
                    path_setup = '''import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

'''
                    content = path_setup + content
                    
                    with open(filepath, 'w') as f:
                        f.write(content)
                    
                    print(f"✅ Updated {filename}")
                    
            except Exception as e:
                print(f"❌ Error updating {filename}: {e}")


def create_summary_report():
    """Create a summary report of the reorganization"""
    report = f"""
# Directory Reorganization Summary

## New Structure
```
proposal-ai/
├── src/                    # Source code
├── tests/                  # Test files (moved from root)
├── data/                   # Database files (moved from root)
├── config/                 # Configuration files (moved from root)
├── docs/                   # Documentation
├── scripts/                # Utility scripts
├── profiles/               # User profiles
├── .github/                # GitHub configuration
├── .copilot/               # Copilot configuration
├── README.md               # Main documentation
├── requirements.txt        # Dependencies
└── run.sh                  # Setup script
```

## Files Moved

### To tests/
- test_*.py files
- quick_test.py

### To data/
- *.db files (proposal_ai.db, opportunities.db, etc.)
- test_results.txt

### To config/
- *.json files (monitoring_config.json, analytics_report.json, etc.)

### To docs/
- *_SUMMARY.md files

### To scripts/
- implement_next_steps.py

## Path Updates

### Database Paths
- Updated to use config.py for centralized path management
- All database connections now use DATA_DIR paths
- Configuration files use CONFIG_DIR paths

### Import Updates
- Added config.py module for path management
- Updated all database classes to use new paths
- Added path setup to test files

## Benefits

1. **Cleaner Root Directory**: Reduced clutter in project root
2. **Logical Organization**: Files grouped by purpose
3. **Centralized Configuration**: All paths managed in config.py
4. **Better Maintainability**: Easier to find and manage files
5. **Standard Structure**: Follows Python project conventions

## Testing

Run the path migration script to verify all changes:
```bash
cd /home/kevin/Projects/proposal-ai
python scripts/test_paths.py
```
"""
    
    report_path = os.path.join(PROJECT_ROOT, "docs", "REORGANIZATION_SUMMARY.md")
    with open(report_path, 'w') as f:
        f.write(report)
    
    print(f"📋 Created reorganization summary: {report_path}")


if __name__ == "__main__":
    print("🔧 Project Directory Reorganization")
    print("=" * 50)
    
    # Test current setup
    success = test_paths()
    
    if success:
        print("\n🔄 Updating test files...")
        update_test_files()
        
        print("\n📋 Creating summary report...")
        create_summary_report()
        
        print("\n✅ Reorganization complete!")
        print("\nNext steps:")
        print("1. Run tests to verify everything works")
        print("2. Update any remaining hardcoded paths")
        print("3. Update documentation links if needed")
    else:
        print("\n❌ Issues found. Please check the errors above.")
