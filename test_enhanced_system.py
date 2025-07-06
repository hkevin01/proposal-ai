#!/usr/bin/env python3
"""
Quick test to verify the enhanced discovery system works
"""

import os
import sys

sys.path.append('src')

def test_spacy():
    """Test spaCy model loading"""
    try:
        import spacy
        nlp = spacy.load('en_core_web_sm')
        print("✅ spaCy model loaded successfully")
        return True
    except Exception as e:
        print(f"❌ spaCy error: {e}")
        return False

def test_api_discovery():
    """Test API integration"""
    try:
        from api_integrations import APIIntegrationManager
        api_manager = APIIntegrationManager()
        print("✅ API integration module loaded")
        
        # Test a simple API call
        keywords = ['artificial intelligence', 'space']
        opportunities = api_manager.search_nsf_opportunities(keywords, max_results=3)
        print(f"✅ Found {len(opportunities)} NSF opportunities")
        
        return True
    except Exception as e:
        print(f"❌ API integration error: {e}")
        return False

def test_database():
    """Test database operations"""
    try:
        from database import DatabaseManager, setup_database

        # Setup database
        setup_database()
        db_manager = DatabaseManager()
        
        # Test opportunity save/retrieve
        test_opp = {
            'title': 'Test AI Opportunity',
            'description': 'Test description',
            'organization': 'Test Org',
            'deadline': '2025-12-31',
            'funding_amount': '$100K',
            'url': 'https://example.com',
            'source': 'Test',
            'category': 'AI Research',
            'ai_relevance_score': 0.8
        }
        
        opp_id = db_manager.save_opportunity(test_opp)
        print(f"✅ Saved test opportunity with ID: {opp_id}")
        
        opportunities = db_manager.get_opportunities(5)
        print(f"✅ Retrieved {len(opportunities)} opportunities from database")
        
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_gui_imports():
    """Test GUI component imports"""
    try:
        from PyQt5.QtWidgets import QApplication

        from gui import ProposalAIApp, ScrapingWorker
        print("✅ GUI components imported successfully")
        return True
    except Exception as e:
        print(f"❌ GUI import error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Enhanced Proposal AI Components...")
    print("=" * 50)
    
    tests = [
        ("spaCy Model", test_spacy),
        ("API Integration", test_api_discovery),
        ("Database Operations", test_database),
        ("GUI Components", test_gui_imports)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    all_passed = True
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if not success:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("\n💡 The enhanced discovery system is ready!")
        print("🚀 You can now run: python src/main.py")
        print("\n🔍 Expected improvements:")
        print("   • 50-200+ opportunities instead of 6")
        print("   • Real API integration from Grants.gov, NASA, NSF, arXiv")
        print("   • AI relevance scoring (0.0 - 1.0)")
        print("   • Live progress tracking during discovery")
        print("   • Enhanced categorization and classification")
    else:
        print("⚠️ Some tests failed. Check the errors above.")
        print("💡 Try running ./run.sh to set up the environment properly.")
