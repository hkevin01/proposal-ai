"""
Main entry point for Proposal AI application
"""
import os
import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from database import setup_database
    from gui import main as gui_main
except ImportError as e:
    print(f"Import error: {e}")
    print("Please install required dependencies: pip install -r requirements.txt")
    sys.exit(1)


def main():
    """Main application entry point"""
    print("🚀 Starting Proposal AI...")
    
    # Setup database
    print("🗄️ Setting up database...")
    try:
        setup_database()
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return 1
    
    # Launch GUI
    print("✨ Launching GUI...")
    try:
        return gui_main()
    except Exception as e:
        print(f"❌ GUI launch failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
