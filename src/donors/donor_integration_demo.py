#!/usr/bin/env python3
"""
Donor Integration Demo
Demonstrates how to use the donor database and matching functionality
"""

import json
import logging
from typing import Dict, List

from donor_enhanced_discovery import DonorEnhancedDiscovery

from ..core.database import DatabaseManager
from .donor_database import Donor, DonorDatabase


def demonstrate_donor_functionality():
    """Comprehensive demonstration of donor functionality"""
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    logger.info("🏁 Starting Donor Integration Demo")
    
    # Initialize components
    donor_db = DonorDatabase()
    discovery_engine = DonorEnhancedDiscovery()
    db_manager = DatabaseManager()
    
    print("\n" + "="*50)
    print("DONOR DATABASE DEMONSTRATION")
    print("="*50)
    
    # 1. Show all donors in database
    print("\n1. Current Donors in Database:")
    print("-" * 30)
    donors = donor_db.get_donors(limit=20)
    for i, donor in enumerate(donors, 1):
        print(f"{i:2d}. {donor.name}")
        print(f"    Type: {donor.type}")
        print(f"    Region: {donor.region}")
        print(f"    Focus: {', '.join(donor.focus_areas[:3])}")
        if donor.giving_amount:
            print(f"    Giving: {donor.giving_amount}")
        print(f"    Website: {donor.website}")
        print()
    
    # 2. Search for specific donors
    print("\n2. Searching for Education-Focused Donors:")
    print("-" * 40)
    education_donors = donor_db.search_donors("education", focus_area="education")
    for donor in education_donors[:5]:
        print(f"✓ {donor.name} ({donor.region})")
        print(f"  Focus: {', '.join(donor.focus_areas)}")
        print()
    
    # 3. Search for space/technology donors
    print("\n3. Searching for Space/Technology Donors:")
    print("-" * 40)
    space_donors = donor_db.search_donors("space technology aerospace")
    for donor in space_donors[:5]:
        print(f"🚀 {donor.name} ({donor.region})")
        print(f"   Focus: {', '.join(donor.focus_areas)}")
        if donor.giving_amount:
            print(f"   Giving: {donor.giving_amount}")
        print()
    
    # 4. Demonstrate opportunity-donor matching
    print("\n4. Finding Donors for Space Research Opportunity:")
    print("-" * 45)
    
    # Get some sample opportunities from the database
    opportunities = db_manager.get_opportunities(limit=10)
    if opportunities:
        # Use the first opportunity as an example
        sample_opp = opportunities[0]
        opportunity_id = sample_opp[0]  # ID is first column
        opp_title = sample_opp[1]       # Title is second column
        
        print(f"Sample Opportunity: {opp_title}")
        print(f"Opportunity ID: {opportunity_id}")
        
        # Get donor recommendations for this opportunity
        recommendations = discovery_engine.get_donor_recommendations(opportunity_id)
        
        print(f"\nFound {len(recommendations)} donor matches:")
        for i, rec in enumerate(recommendations[:5], 1):
            donor = rec['donor']
            score = rec['match_score']
            reasons = rec['recommendation_reasons']
            
            print(f"\n{i}. {donor.name} (Score: {score:.2f})")
            print(f"   Type: {donor.type}")
            print(f"   Website: {donor.website}")
            print(f"   Contact: {donor.contact_email or donor.contact_phone or 'N/A'}")
            print(f"   Reasons: {'; '.join(reasons[:2])}")
            
            # Show contact strategy
            strategy = rec['contact_strategy']
            print(f"   Approach: {strategy['approach']}")
            if strategy['key_points']:
                print(f"   Key Points: {strategy['key_points'][0]}")
    
    # 5. Demonstrate discovery with donor matching
    print("\n\n5. Discovery with Integrated Donor Matching:")
    print("-" * 45)
    
    # Discover opportunities with donor matches
    keywords = ["artificial intelligence", "space", "research"]
    matches = discovery_engine.discover_opportunities_with_donors(keywords, limit=5)
    
    print(f"Found {len(matches)} opportunities with donor matches:")
    for i, match in enumerate(matches, 1):
        opp = match.opportunity
        total_score = match.total_match_score
        top_donors = match.matching_donors[:3]
        
        print(f"\n{i}. {opp.get('title', 'Unknown Title')}")
        print(f"   Agency: {opp.get('agency', 'Unknown')}")
        print(f"   Total Donor Score: {total_score:.2f}")
        print(f"   Top Donors:")
        for donor, score in top_donors:
            print(f"     • {donor.name}: {score:.2f}")
    
    # 6. Show donor portfolio for a specific donor
    print("\n\n6. Donor Portfolio Example:")
    print("-" * 30)
    
    if donors:
        sample_donor = donors[0]
        portfolio = discovery_engine.get_donor_portfolio(sample_donor.id)
        
        if portfolio:
            print(f"Donor: {portfolio['donor'].name}")
            print(f"Matched Opportunities: {portfolio['total_opportunities']}")
            print(f"Average Match Score: {portfolio['avg_match_score']:.2f}")
            
            print("\nTop Matched Opportunities:")
            for opp in portfolio['matched_opportunities'][:3]:
                print(f"  • {opp.get('title', 'Unknown')}: {opp.get('match_score', 0):.2f}")
            
            contact_info = portfolio['contact_info']
            print(f"\nContact Information:")
            print(f"  Website: {contact_info['website']}")
            print(f"  Email: {contact_info['email']}")
            print(f"  Phone: {contact_info['phone']}")
    
    # 7. Add a custom donor
    print("\n\n7. Adding a Custom Donor:")
    print("-" * 30)
    
    custom_donor = Donor(
        name="Sample Tech Foundation",
        type="foundation",
        region="North America", 
        country="USA",
        focus_areas=["technology", "artificial intelligence", "education"],
        website="https://example-tech-foundation.org",
        contact_email="grants@example-tech-foundation.org",
        description="Supports innovative technology projects and AI research",
        giving_amount="$10-50 million annually",
        application_process="Online application, quarterly deadlines"
    )
    
    donor_id = donor_db.add_donor(custom_donor)
    if donor_id > 0:
        print(f"✅ Successfully added donor: {custom_donor.name}")
        print(f"   Assigned ID: {donor_id}")
    else:
        print("❌ Failed to add donor")
    
    # 8. Generate donor report
    print("\n\n8. Donor Database Statistics:")
    print("-" * 35)
    
    all_donors = donor_db.get_donors(limit=1000)  # Get all donors
    
    # Count by type
    type_counts = {}
    region_counts = {}
    focus_counts = {}
    
    for donor in all_donors:
        # Count by type
        type_counts[donor.type] = type_counts.get(donor.type, 0) + 1
        
        # Count by region
        region_counts[donor.region] = region_counts.get(donor.region, 0) + 1
        
        # Count focus areas
        for area in donor.focus_areas:
            focus_counts[area] = focus_counts.get(area, 0) + 1
    
    print(f"Total Donors: {len(all_donors)}")
    print(f"\nBy Type:")
    for donor_type, count in sorted(type_counts.items()):
        print(f"  {donor_type}: {count}")
    
    print(f"\nBy Region:")
    for region, count in sorted(region_counts.items()):
        print(f"  {region}: {count}")
    
    print(f"\nTop Focus Areas:")
    sorted_focus = sorted(focus_counts.items(), key=lambda x: x[1], reverse=True)
    for area, count in sorted_focus[:10]:
        print(f"  {area}: {count}")
    
    print("\n" + "="*50)
    print("INTEGRATION COMPLETE")
    print("="*50)
    
    return {
        'total_donors': len(all_donors),
        'type_distribution': type_counts,
        'region_distribution': region_counts,
        'top_focus_areas': dict(sorted_focus[:10])
    }


def export_donor_data(filename: str = "donor_export.json"):
    """Export donor data for external use"""
    donor_db = DonorDatabase()
    donors = donor_db.get_donors(limit=1000)
    
    export_data = []
    for donor in donors:
        donor_dict = {
            'name': donor.name,
            'type': donor.type,
            'region': donor.region,
            'country': donor.country,
            'focus_areas': donor.focus_areas,
            'website': donor.website,
            'contact_email': donor.contact_email,
            'contact_phone': donor.contact_phone,
            'description': donor.description,
            'giving_amount': donor.giving_amount,
            'application_process': donor.application_process
        }
        export_data.append(donor_dict)
    
    with open(filename, 'w') as f:
        json.dump(export_data, f, indent=2)
    
    print(f"✅ Exported {len(export_data)} donors to {filename}")


def generate_proposal_donor_matches(opportunity_keywords: List[str]) -> Dict:
    """Generate donor matches for proposal keywords"""
    discovery_engine = DonorEnhancedDiscovery()
    donor_db = DonorDatabase()
    
    # Find matching donors
    matches = donor_db.find_matching_donors(opportunity_keywords)
    
    # Format results
    result = {
        'keywords': opportunity_keywords,
        'total_matches': len(matches),
        'top_matches': []
    }
    
    for donor, score in matches[:10]:
        match_info = {
            'donor_name': donor.name,
            'donor_type': donor.type,
            'region': donor.region,
            'focus_areas': donor.focus_areas,
            'match_score': score,
            'website': donor.website,
            'contact_email': donor.contact_email,
            'giving_amount': donor.giving_amount
        }
        result['top_matches'].append(match_info)
    
    return result


if __name__ == "__main__":
    # Run the comprehensive demonstration
    stats = demonstrate_donor_functionality()
    
    # Export donor data
    export_donor_data()
    
    # Example of finding donors for specific proposal
    print("\n" + "="*50)
    print("PROPOSAL-SPECIFIC DONOR MATCHING")
    print("="*50)
    
    proposal_keywords = ["artificial intelligence", "healthcare", "research"]
    matches = generate_proposal_donor_matches(proposal_keywords)
    
    print(f"\nFor proposal keywords: {', '.join(proposal_keywords)}")
    print(f"Found {matches['total_matches']} potential donors")
    print("\nTop 5 matches:")
    
    for i, match in enumerate(matches['top_matches'][:5], 1):
        print(f"\n{i}. {match['donor_name']}")
        print(f"   Type: {match['donor_type']}")
        print(f"   Score: {match['match_score']:.2f}")
        print(f"   Focus: {', '.join(match['focus_areas'][:3])}")
        print(f"   Website: {match['website']}")
        if match['giving_amount']:
            print(f"   Giving: {match['giving_amount']}")
