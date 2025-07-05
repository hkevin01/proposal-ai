"""
Test script for Enhanced Proposal AI Discovery System
Demonstrates the new capabilities:
- Enhanced discovery from 50+ sources
- Resume parsing and profile management
- Intelligent opportunity matching
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from database import DatabaseManager, setup_database
from enhanced_discovery_engine import EnhancedOpportunityDiscoverer
from resume_parser import ProfileManager, ResumeParser


def test_enhanced_discovery():
    """Test the enhanced discovery engine"""
    print("🚀 Testing Enhanced Discovery Engine")
    print("=" * 50)
    
    discoverer = EnhancedOpportunityDiscoverer()
    
    print(f"📡 Configured sources: {len(discoverer.opportunity_sources)}")
    print("🔍 Starting discovery from sample sources...")
    
    # Test with limited sources for speed
    sample_sources = ['NASA', 'NSF', 'IEEE', 'Google']
    limited_sources = {k: v for k, v in discoverer.opportunity_sources.items() 
                      if k in sample_sources}
    
    discoverer.opportunity_sources = limited_sources
    
    opportunities = discoverer.discover_opportunities(max_per_source=3)
    
    print(f"✅ Found {len(opportunities)} opportunities")
    
    if opportunities:
        print("\\n📋 Sample opportunities:")
        for i, opp in enumerate(opportunities[:3], 1):
            print(f"  {i}. {opp['title'][:80]}...")
            print(f"     Organization: {opp.get('organization', 'Unknown')}")
            print(f"     Relevance: {opp.get('relevance_score', 0):.3f}")
            print(f"     Categories: {', '.join(opp.get('categories', [])[:3])}")
            print()
    
    return opportunities


def test_resume_parsing():
    """Test resume parsing capabilities"""
    print("📄 Testing Resume Parsing")
    print("=" * 50)
    
    parser = ResumeParser()
    
    # Test with sample resume text
    sample_resume = """
    Dr. Jane Smith
    jane.smith@university.edu
    (555) 123-4567
    
    EDUCATION
    PhD in Aerospace Engineering, MIT, 2018
    MS in Computer Science, Stanford, 2015
    BS in Mechanical Engineering, UC Berkeley, 2013
    
    EXPERIENCE
    Senior Research Scientist, NASA Jet Propulsion Laboratory (2018-present)
    - Lead researcher on Mars sample return mission planning
    - Developed autonomous navigation algorithms for rovers
    - Published 15 papers on planetary robotics and AI
    
    Research Assistant, MIT Space Systems Lab (2015-2018)
    - Worked on CubeSat constellation design and optimization
    - Developed machine learning models for satellite data processing
    
    SKILLS
    Programming: Python, C++, MATLAB, ROS
    Machine Learning: TensorFlow, PyTorch, scikit-learn
    Space Technology: Mission planning, orbital mechanics, spacecraft design
    Tools: Git, Docker, Linux, SOLIDWORKS
    
    RESEARCH INTERESTS
    Autonomous space systems, planetary exploration, machine learning for space applications,
    multi-agent robotics, satellite constellation optimization
    
    PUBLICATIONS
    "Autonomous Navigation for Mars Sample Return Missions", Nature Robotics, 2023
    "Machine Learning in Deep Space Communications", IEEE Aerospace, 2022
    "CubeSat Swarm Coordination Using Distributed AI", AIAA Journal, 2021
    """
    
    print("🔍 Parsing sample resume...")
    profile_data = parser.parse_resume_text(sample_resume)
    
    print("✅ Parsing complete! Extracted information:")
    print(f"   🎯 Specialization: {profile_data.get('specialization', 'Unknown')}")
    print(f"   🏢 Industry: {profile_data.get('industry', 'Unknown')}")
    print(f"   🛠️ Skills: {profile_data.get('skills', 'None')[:100]}...")
    print(f"   🎓 Education: {profile_data.get('education', 'None')[:100]}...")
    print(f"   🔬 Research: {profile_data.get('research_interests', 'None')[:100]}...")
    print(f"   📚 Technologies: {profile_data.get('technologies', 'None')[:100]}...")
    
    return profile_data


def test_opportunity_matching(profile_data, opportunities):
    """Test opportunity matching"""
    print("🎯 Testing Opportunity Matching")
    print("=" * 50)
    
    if not opportunities or not profile_data:
        print("❌ Need both profile data and opportunities for matching")
        return
    
    discoverer = EnhancedOpportunityDiscoverer()
    
    print(f"🔍 Matching {len(opportunities)} opportunities to profile...")
    matched_opportunities = discoverer.match_opportunities_to_profile(
        profile_data, opportunities, top_n=10
    )
    
    print(f"✅ Found {len(matched_opportunities)} matches")
    
    if matched_opportunities:
        print("\\n🏆 Top 5 matches:")
        for i, opp in enumerate(matched_opportunities[:5], 1):
            print(f"  {i}. {opp['title'][:70]}...")
            print(f"     Organization: {opp.get('organization', 'Unknown')}")
            print(f"     Match Score: {opp.get('profile_match_score', 0):.3f}")
            print(f"     Combined Score: {opp.get('combined_score', 0):.3f}")
            print(f"     Categories: {', '.join(opp.get('categories', [])[:2])}")
            print()
    
    return matched_opportunities


def test_database_integration():
    """Test database operations"""
    print("🗄️ Testing Database Integration")
    print("=" * 50)
    
    # Setup database
    setup_database()
    db_manager = DatabaseManager()
    
    # Test profile management
    profile_manager = ProfileManager()
    
    print("✅ Database setup complete")
    print("✅ Profile manager initialized")
    
    return db_manager


def main():
    """Run all tests"""
    print("🧪 Enhanced Proposal AI Test Suite")
    print("=" * 60)
    
    try:
        # Test database
        db_manager = test_database_integration()
        
        print("\\n")
        
        # Test resume parsing
        profile_data = test_resume_parsing()
        
        print("\\n")
        
        # Test discovery
        opportunities = test_enhanced_discovery()
        
        print("\\n")
        
        # Test matching
        if opportunities and profile_data:
            matched_opportunities = test_opportunity_matching(profile_data, opportunities)
        
        print("\\n" + "=" * 60)
        print("✅ All tests completed successfully!")
        print("🚀 Enhanced Proposal AI is ready for use!")
        
        print("\\n🎯 Next steps:")
        print("1. Run the GUI: python src/main.py")
        print("2. Upload your resume in the Profile tab")
        print("3. Start Enhanced Discovery to find opportunities")
        print("4. Use Smart Matching to find relevant opportunities")
        print("5. Generate AI proposals for your best matches")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        print("\\n🔧 Install missing dependencies:")
        print("pip install -r requirements.txt")
        print("python -m spacy download en_core_web_sm")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
