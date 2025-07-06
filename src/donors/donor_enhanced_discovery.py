#!/usr/bin/env python3
"""
Donor-Enhanced Discovery Engine
Integrates donor/foundation matching with opportunity discovery
"""

import json
import logging
import sqlite3
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from .config import MAIN_DATABASE_PATH
from .donor_database import Donor, DonorDatabase
from .enhanced_discovery_engine import EnhancedDiscoveryEngine


@dataclass
class OpportunityMatch:
    """Represents an opportunity with matched donors"""
    opportunity: Dict
    matching_donors: List[Tuple[Donor, float]]
    total_match_score: float


class DonorEnhancedDiscovery:
    """Enhanced discovery engine with donor matching capabilities"""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or MAIN_DATABASE_PATH
        self.logger = logging.getLogger(__name__)
        self.discovery_engine = EnhancedDiscoveryEngine(db_path)
        self.donor_db = DonorDatabase()
    
    def discover_opportunities_with_donors(self, 
                                         keywords: List[str],
                                         limit: int = 50) -> List[OpportunityMatch]:
        """
        Discover opportunities and match them with potential donors
        """
        try:
            # Get opportunities from the enhanced discovery engine
            opportunities = self.discovery_engine.discover_opportunities(
                keywords, limit=limit)
            
            opportunity_matches = []
            
            for opp in opportunities:
                # Extract keywords from opportunity for donor matching
                opp_keywords = self._extract_opportunity_keywords(opp)
                opp_type = self._determine_opportunity_type(opp)
                
                # Find matching donors
                matching_donors = self.donor_db.find_matching_donors(
                    opp_keywords, opp_type)
                
                # Calculate total match score
                total_score = sum(score for _, score in matching_donors)
                
                match = OpportunityMatch(
                    opportunity=opp,
                    matching_donors=matching_donors,
                    total_match_score=total_score
                )
                opportunity_matches.append(match)
            
            # Sort by total match score (opportunities with better donor matches first)
            opportunity_matches.sort(key=lambda x: x.total_match_score, reverse=True)
            
            return opportunity_matches
            
        except Exception as e:
            self.logger.error(f"Error discovering opportunities with donors: {e}")
            return []
    
    def _extract_opportunity_keywords(self, opportunity: Dict) -> List[str]:
        """Extract relevant keywords from an opportunity for donor matching"""
        keywords = []
        
        # Get text from opportunity fields
        text_fields = ['title', 'description', 'requirements', 'agency']
        for field in text_fields:
            if field in opportunity and opportunity[field]:
                text = str(opportunity[field]).lower()
                # Simple keyword extraction (could be enhanced with NLP)
                words = text.split()
                keywords.extend([w.strip('.,!?;:') for w in words if len(w) > 3])
        
        # Remove duplicates and return unique keywords
        return list(set(keywords))
    
    def _determine_opportunity_type(self, opportunity: Dict) -> Optional[str]:
        """Determine the type/category of an opportunity"""
        title = str(opportunity.get('title', '')).lower()
        description = str(opportunity.get('description', '')).lower()
        text = f"{title} {description}"
        
        # Define type keywords
        type_mapping = {
            'space': ['space', 'aerospace', 'satellite', 'orbit', 'rocket', 'nasa'],
            'research': ['research', 'study', 'investigation', 'analysis', 'science'],
            'education': ['education', 'learning', 'student', 'school', 'training'],
            'health': ['health', 'medical', 'healthcare', 'medicine', 'clinical'],
            'environment': ['environment', 'climate', 'sustainability', 'green', 'carbon'],
            'technology': ['technology', 'software', 'ai', 'machine learning', 'digital'],
            'energy': ['energy', 'renewable', 'solar', 'wind', 'battery']
        }
        
        # Count matches for each type
        type_scores = {}
        for opp_type, keywords in type_mapping.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                type_scores[opp_type] = score
        
        # Return type with highest score
        if type_scores:
            return max(type_scores, key=type_scores.get)
        
        return 'general'
    
    def get_donor_recommendations(self, opportunity_id: int) -> List[Dict]:
        """Get donor recommendations for a specific opportunity"""
        try:
            # Get opportunity details
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM opportunities WHERE id = ?
            ''', (opportunity_id,))
            
            opp_row = cursor.fetchone()
            conn.close()
            
            if not opp_row:
                return []
            
            # Convert to dictionary
            opportunity = {
                'id': opp_row[0],
                'title': opp_row[1],
                'description': opp_row[2],
                'agency': opp_row[3],
                'deadline': opp_row[4],
                'amount': opp_row[5],
                'url': opp_row[6],
                'requirements': opp_row[7],
                'type': opp_row[8]
            }
            
            # Extract keywords and find matching donors
            keywords = self._extract_opportunity_keywords(opportunity)
            opp_type = self._determine_opportunity_type(opportunity)
            
            matching_donors = self.donor_db.find_matching_donors(keywords, opp_type)
            
            # Format recommendations
            recommendations = []
            for donor, score in matching_donors:
                rec = {
                    'donor': donor,
                    'match_score': score,
                    'recommendation_reasons': self._generate_recommendation_reasons(
                        donor, opportunity, keywords),
                    'contact_strategy': self._suggest_contact_strategy(donor, opportunity)
                }
                recommendations.append(rec)
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error getting donor recommendations: {e}")
            return []
    
    def _generate_recommendation_reasons(self, donor: Donor, 
                                       opportunity: Dict, 
                                       keywords: List[str]) -> List[str]:
        """Generate reasons why a donor is recommended for an opportunity"""
        reasons = []
        
        # Check focus area alignment
        donor_focus = ' '.join(donor.focus_areas).lower()
        opp_text = f"{opportunity.get('title', '')} {opportunity.get('description', '')}".lower()
        
        matching_areas = []
        for area in donor.focus_areas:
            if any(keyword in area.lower() for keyword in keywords):
                matching_areas.append(area)
        
        if matching_areas:
            reasons.append(f"Focus areas align: {', '.join(matching_areas)}")
        
        # Check giving capacity
        if donor.giving_amount:
            reasons.append(f"Giving capacity: {donor.giving_amount}")
        
        # Check geographic alignment
        if donor.region and opportunity.get('agency'):
            agency = opportunity['agency'].lower()
            if 'nasa' in agency or 'nsf' in agency:
                reasons.append("Aligns with government/research funding")
        
        # Check past giving patterns
        if 'research' in donor_focus and 'research' in opp_text:
            reasons.append("History of supporting research initiatives")
        
        if not reasons:
            reasons.append("General philanthropic interests align")
        
        return reasons
    
    def _suggest_contact_strategy(self, donor: Donor, opportunity: Dict) -> Dict:
        """Suggest a contact strategy for approaching the donor"""
        strategy = {
            'approach': 'formal',
            'key_points': [],
            'timing': 'immediate',
            'follow_up': 'standard'
        }
        
        # Determine approach based on donor type
        if donor.type == 'individual':
            strategy['approach'] = 'personal'
            strategy['key_points'].append("Emphasize personal impact and recognition")
        elif donor.type == 'foundation':
            strategy['approach'] = 'formal'
            strategy['key_points'].append("Follow formal application process")
        elif donor.type == 'corporation':
            strategy['approach'] = 'business'
            strategy['key_points'].append("Highlight business benefits and partnerships")
        
        # Add opportunity-specific points
        if opportunity.get('deadline'):
            strategy['timing'] = 'urgent'
            strategy['key_points'].append(f"Deadline: {opportunity['deadline']}")
        
        # Add donor-specific points
        if donor.focus_areas:
            strategy['key_points'].append(f"Emphasize alignment with: {', '.join(donor.focus_areas[:2])}")
        
        if donor.application_process:
            strategy['key_points'].append(f"Process: {donor.application_process}")
        
        return strategy
    
    def save_donor_opportunity_match(self, opportunity_id: int, 
                                   donor_id: int, score: float):
        """Save a donor-opportunity match to the database"""
        try:
            reasons = f"Automated match with score {score:.2f}"
            self.donor_db.save_donor_match(donor_id, opportunity_id, score, reasons)
            
        except Exception as e:
            self.logger.error(f"Error saving donor-opportunity match: {e}")
    
    def get_donor_portfolio(self, donor_id: int) -> Dict:
        """Get a comprehensive portfolio for a donor including matched opportunities"""
        try:
            donor = self.donor_db.get_donor_by_id(donor_id)
            if not donor:
                return {}
            
            # Get matched opportunities
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT o.*, dm.match_score 
                FROM opportunities o
                JOIN donor_matches dm ON o.id = dm.opportunity_id
                WHERE dm.donor_id = ?
                ORDER BY dm.match_score DESC
            ''', (donor_id,))
            
            matched_opps = cursor.fetchall()
            conn.close()
            
            opportunities = []
            for row in matched_opps:
                opp = {
                    'id': row[0],
                    'title': row[1], 
                    'description': row[2],
                    'agency': row[3],
                    'deadline': row[4],
                    'amount': row[5],
                    'url': row[6],
                    'match_score': row[-1]
                }
                opportunities.append(opp)
            
            portfolio = {
                'donor': donor,
                'matched_opportunities': opportunities,
                'total_opportunities': len(opportunities),
                'avg_match_score': sum(o['match_score'] for o in opportunities) / len(opportunities) if opportunities else 0,
                'contact_info': {
                    'website': donor.website,
                    'email': donor.contact_email,
                    'phone': donor.contact_phone
                }
            }
            
            return portfolio
            
        except Exception as e:
            self.logger.error(f"Error getting donor portfolio: {e}")
            return {}


def main():
    """Test the donor-enhanced discovery system"""
    logging.basicConfig(level=logging.INFO)
    
    # Initialize the enhanced discovery engine
    discovery = DonorEnhancedDiscovery()
    
    # Test discovery with donor matching
    keywords = ["space", "research", "technology"]
    matches = discovery.discover_opportunities_with_donors(keywords, limit=10)
    
    print(f"Found {len(matches)} opportunities with donor matches:")
    for match in matches[:3]:
        print(f"\nOpportunity: {match.opportunity.get('title', 'Unknown')}")
        print(f"Total donor match score: {match.total_match_score:.2f}")
        print(f"Top donors:")
        for donor, score in match.matching_donors[:3]:
            print(f"  - {donor.name}: {score:.2f}")


if __name__ == "__main__":
    main()
