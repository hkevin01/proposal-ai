#!/usr/bin/env python3
"""
Comprehensive test for Proposal AI components
"""
import os
import sys
import traceback

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_spacy():
    """Test spaCy model installation"""
    print("=" * 50)
    print("Testing spaCy model...")
    try:
        import spacy
        print(f"spaCy version: {spacy.__version__}")
        
        nlp = spacy.load('en_core_web_sm')
        print("✅ spaCy model loaded successfully!")
        
        # Test basic functionality
        text = "NASA is developing space technology for future missions."
        doc = nlp(text)
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        print(f"Found entities: {entities}")
        
        return True
    except Exception as e:
        print(f"❌ spaCy error: {e}")
        traceback.print_exc()
        return False

def test_discovery_engine():
    """Test discovery engine initialization"""
    print("=" * 50)
    print("Testing discovery engine...")
    try:
        from enhanced_discovery_engine import EnhancedOpportunityDiscoverer
        discoverer = EnhancedOpportunityDiscoverer()
        
        print("✅ Discovery engine initialized successfully!")
        print(f"spaCy available: {discoverer.nlp is not None}")
        print(f"Sources count: {len(discoverer.opportunity_sources)}")
        
        return True
    except Exception as e:
        print(f"❌ Discovery engine error: {e}")
        traceback.print_exc()
        return False

def test_database():
    """Test database setup"""
    print("=" * 50)
    print("Testing database...")
    try:
        from database import DatabaseManager
        db = DatabaseManager()
        
        print("✅ Database manager initialized successfully!")
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        traceback.print_exc()
        return False

def test_gui_import():
    """Test GUI imports"""
    print("=" * 50)
    print("Testing GUI imports...")
    try:
        from PyQt5.QtWidgets import QApplication
        print("✅ PyQt5 imported successfully!")
        
        # Don't actually create the GUI in headless environment
        return True
    except Exception as e:
        print(f"❌ GUI import error: {e}")
        traceback.print_exc()
        return False

def main():
    print("🧪 Running comprehensive Proposal AI tests...")
    
    results = []
    results.append(("spaCy", test_spacy()))
    results.append(("Discovery Engine", test_discovery_engine()))
    results.append(("Database", test_database()))
    results.append(("GUI", test_gui_import()))
    
    print("=" * 50)
    print("📊 TEST RESULTS:")
    print("=" * 50)
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{name:20}: {status}")
        if not passed:
            all_passed = False
    
    print("=" * 50)
    if all_passed:
        print("🎉 All tests passed! The system is ready to run.")
    else:
        print("⚠️ Some tests failed. Check the errors above.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
