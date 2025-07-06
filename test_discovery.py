#!/usr/bin/env python3
"""
Test script for the enhanced discovery and API integrations
"""

import os
import sys

sys.path.append('src')

from api_integrations import APIIntegrationManager
from database import DatabaseManager, setup_database


def test_api_discovery():
    """Test the API integration discovery"""
    print("🧪 Testing API Discovery Integration...")
    
    # Setup database
    setup_database()
    
    # Test API manager
    api_manager = APIIntegrationManager()
    
    # Test with AI/space keywords
    keywords = ['artificial intelligence', 'machine learning', 'space', 'aerospace']
    
    print(f"🔍 Searching with keywords: {keywords}")
    
    try:
        opportunities = api_manager.get_all_api_opportunities(keywords, max_per_source=5)
        print(f"✅ Found {len(opportunities)} total opportunities")
        
        # Display first few opportunities
        for i, opp in enumerate(opportunities[:3]):
            print(f"\n📄 Opportunity {i+1}:")
            print(f"   Title: {opp['title'][:80]}...")
            print(f"   Source: {opp['source']}")
            print(f"   Category: {opp['category']}")
            print(f"   AI Relevance: {opp['ai_relevance_score']:.2f}")
        
        # Test database save
        db_manager = DatabaseManager()
        saved_count = 0
        
        for opp in opportunities:
            try:
                db_manager.save_opportunity(opp)
                saved_count += 1
            except Exception as e:
                print(f"⚠️ Error saving opportunity: {e}")
        
        print(f"\n💾 Saved {saved_count} opportunities to database")
        
        # Test retrieval
        retrieved_opps = db_manager.get_opportunities(10)
        print(f"📤 Retrieved {len(retrieved_opps)} opportunities from database")
        
        return True
        
    except Exception as e:
        print(f"❌ API Discovery test failed: {e}")
        return False

def test_gui_integration():
    """Test GUI integration"""
    print("\n🧪 Testing GUI Integration...")
    
    try:
        from PyQt5.QtWidgets import QApplication

        from gui import ProposalAIApp

        # Create minimal Qt application for testing
        app = QApplication([])
        
        # Test GUI creation
        gui = ProposalAIApp()
        print("✅ GUI created successfully")
        
        # Test discovery worker creation
        from gui import ScrapingWorker
        worker = ScrapingWorker()
        print("✅ ScrapingWorker created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ GUI integration test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Enhanced Proposal AI Discovery...")
    print("=" * 50)
    
    # Run API discovery test
    api_success = test_api_discovery()
    
    # Run GUI integration test  
    gui_success = test_gui_integration()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"   API Discovery: {'✅ PASS' if api_success else '❌ FAIL'}")
    print(f"   GUI Integration: {'✅ PASS' if gui_success else '❌ FAIL'}")
    
    if api_success and gui_success:
        print("\n🎉 All tests passed! The enhanced discovery system is ready.")
        print("\n💡 You can now run the application with:")
        print("   python src/main.py")
        print("\n🔍 Features available:")
        print("   • API-based discovery from Grants.gov, NASA, NSF, arXiv")
        print("   • Enhanced web scraping from 50+ sources") 
        print("   • AI relevance scoring and categorization")
        print("   • Real-time GUI updates and progress tracking")
    else:
        print("\n⚠️ Some tests failed. Check the error messages above.")
