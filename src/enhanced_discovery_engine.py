"""
Enhanced Discovery Engine for Proposal AI
- Expanded opportunity sources (50+ websites)
- Resume/profile matching 
- Intelligent proposal-opportunity matching
- Advanced NLP and keyword extraction
"""

import json
import re
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse

import numpy as np
import requests
import spacy
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from database import DatabaseManager


class EnhancedOpportunityDiscoverer:
    """Enhanced opportunity discovery with multiple sources and intelligent matching"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.nlp = spacy.load('en_core_web_sm')
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        
        # Comprehensive list of opportunity sources
        self.opportunity_sources = {
            # Government Agencies
            'NASA': {
                'urls': [
                    'https://sbir.nasa.gov/',
                    'https://nspires.nasaprs.com/',
                    'https://solicitation.nasa.gov/',
                    'https://www.nasa.gov/news/releases/',
                ],
                'keywords': ['sbir', 'sttr', 'nspires', 'solicitation', 'announcement']
            },
            'ESA': {
                'urls': [
                    'https://www.esa.int/Applications/Telecommunications_Integrated_Applications',
                    'https://www.esa.int/Enabling_Support/Space_Engineering_Technology',
                    'https://business.esa.int/funding',
                    'https://www.esa.int/About_Us/Business_with_ESA/Small_and_Medium_Sized_Enterprises',
                ],
                'keywords': ['call', 'tender', 'invitation', 'proposal']
            },
            'NSF': {
                'urls': [
                    'https://www.nsf.gov/funding/',
                    'https://www.nsf.gov/publications/pub_summ.jsp?ods_key=nsf23001',
                    'https://beta.nsf.gov/funding/opportunities',
                ],
                'keywords': ['program solicitation', 'dear colleague', 'funding opportunity']
            },
            'NIH': {
                'urls': [
                    'https://grants.nih.gov/',
                    'https://grants.nih.gov/grants/guide/',
                    'https://www.sbir.gov/opportunities',
                ],
                'keywords': ['rfa', 'par', 'not', 'funding opportunity']
            },
            'DOE': {
                'urls': [
                    'https://www.energy.gov/science/grants-and-contracts',
                    'https://science.osti.gov/grants',
                    'https://www.sbir.gov/opportunities?agency=department-of-energy',
                ],
                'keywords': ['funding opportunity', 'lab call', 'solicitation']
            },
            'DARPA': {
                'urls': [
                    'https://www.darpa.mil/work-with-us/opportunities',
                    'https://www.darpa.mil/news-events/solicitations',
                ],
                'keywords': ['broad agency announcement', 'baa', 'solicitation']
            },
            'Air Force': {
                'urls': [
                    'https://www.afrl.af.mil/Funding/',
                    'https://www.sbir.gov/opportunities?agency=department-of-defense',
                ],
                'keywords': ['sbir', 'sttr', 'baa', 'funding opportunity']
            },
            
            # International Space Agencies
            'JAXA': {
                'urls': [
                    'https://global.jaxa.jp/',
                    'https://humans-in-space.jaxa.jp/',
                ],
                'keywords': ['opportunity', 'collaboration', 'call']
            },
            'CSA': {
                'urls': [
                    'https://www.asc-csa.gc.ca/eng/',
                    'https://www.asc-csa.gc.ca/eng/funding-programs/',
                ],
                'keywords': ['funding', 'program', 'opportunity']
            },
            'DLR': {
                'urls': [
                    'https://www.dlr.de/en',
                    'https://www.dlr.de/en/research-and-transfer',
                ],
                'keywords': ['ausschreibung', 'call', 'funding']
            },
            'CNES': {
                'urls': [
                    'https://cnes.fr/en',
                    'https://cnes.fr/en/innovation-and-industry',
                ],
                'keywords': ['appel', 'call', 'opportunity']
            },
            'ISRO': {
                'urls': [
                    'https://www.isro.gov.in/',
                ],
                'keywords': ['announcement', 'call', 'opportunity']
            },
            
            # Academic and Research Foundations
            'IEEE': {
                'urls': [
                    'https://www.ieee.org/conferences/',
                    'https://www.ieee.org/membership/students/competitions/',
                ],
                'keywords': ['call for papers', 'cfp', 'competition', 'conference']
            },
            'IAC': {
                'urls': [
                    'https://www.iafastro.org/',
                    'https://www.iafastro.org/events/',
                ],
                'keywords': ['call for papers', 'abstract submission', 'conference']
            },
            'AIAA': {
                'urls': [
                    'https://www.aiaa.org/events-learning/events',
                    'https://www.aiaa.org/students-and-educators/university-students/design-competitions',
                ],
                'keywords': ['call for papers', 'competition', 'conference']
            },
            'AGU': {
                'urls': [
                    'https://www.agu.org/',
                    'https://www.agu.org/Fall-Meeting',
                ],
                'keywords': ['call for abstracts', 'submission', 'conference']
            },
            
            # Private Sector and Competitions
            'Google': {
                'urls': [
                    'https://research.google/programs/',
                    'https://research.google/outreach/',
                ],
                'keywords': ['research awards', 'faculty award', 'funding']
            },
            'Microsoft': {
                'urls': [
                    'https://www.microsoft.com/en-us/research/academic-program/',
                    'https://www.microsoft.com/en-us/research/collaboration/awards/',
                ],
                'keywords': ['research grant', 'award', 'funding']
            },
            'Amazon': {
                'urls': [
                    'https://www.amazon.science/research-awards',
                    'https://aws.amazon.com/research-and-academic-program/',
                ],
                'keywords': ['research award', 'grant', 'funding']
            },
            'Facebook/Meta': {
                'urls': [
                    'https://research.facebook.com/programs/',
                ],
                'keywords': ['research award', 'rfp', 'proposal']
            },
            'SpaceX': {
                'urls': [
                    'https://www.spacex.com/',
                ],
                'keywords': ['opportunity', 'collaboration', 'partnership']
            },
            'Blue Origin': {
                'urls': [
                    'https://www.blueorigin.com/',
                ],
                'keywords': ['opportunity', 'collaboration', 'partnership']
            },
            
            # Foundations and NGOs
            'Gates Foundation': {
                'urls': [
                    'https://www.gatesfoundation.org/about/how-we-work/general-information/grant-opportunities',
                ],
                'keywords': ['request for proposals', 'rfp', 'funding opportunity']
            },
            'Wellcome Trust': {
                'urls': [
                    'https://wellcome.org/grant-funding',
                ],
                'keywords': ['funding', 'grant', 'application']
            },
            'Howard Hughes': {
                'urls': [
                    'https://www.hhmi.org/programs',
                ],
                'keywords': ['competition', 'award', 'program']
            },
            
            # Startup and Innovation
            'Y Combinator': {
                'urls': [
                    'https://www.ycombinator.com/apply',
                    'https://www.ycombinator.com/blog',
                ],
                'keywords': ['application', 'startup', 'funding']
            },
            'Techstars': {
                'urls': [
                    'https://www.techstars.com/accelerators',
                ],
                'keywords': ['accelerator', 'application', 'program']
            },
            'XPRIZE': {
                'urls': [
                    'https://www.xprize.org/prizes',
                ],
                'keywords': ['competition', 'prize', 'challenge']
            },
            
            # European Funding
            'Horizon Europe': {
                'urls': [
                    'https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen/programmes/horizon',
                    'https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen/home',
                ],
                'keywords': ['call', 'proposal', 'funding opportunity', 'tender']
            },
            'ERC': {
                'urls': [
                    'https://erc.europa.eu/apply-grant',
                ],
                'keywords': ['call', 'grant', 'application']
            },
            'Marie Curie': {
                'urls': [
                    'https://marie-sklodowska-curie-actions.ec.europa.eu/',
                ],
                'keywords': ['call', 'fellowship', 'application']
            },
            
            # General Grant Databases
            'Grants.gov': {
                'urls': [
                    'https://www.grants.gov/',
                    'https://www.grants.gov/search-grants',
                ],
                'keywords': ['funding opportunity', 'grant', 'application']
            },
            'GrantSpace': {
                'urls': [
                    'https://grantspace.org/',
                ],
                'keywords': ['grant', 'funding', 'opportunity']
            },
            'Pivot': {
                'urls': [
                    'https://pivot.proquest.com/',
                ],
                'keywords': ['funding opportunity', 'sponsor', 'grant']
            }
        }
        
        # Enhanced keyword categories for better matching
        self.keyword_categories = {
            'space_technology': ['satellite', 'spacecraft', 'orbital', 'space', 'aerospace', 'astronaut', 'mission', 'launch', 'rocket'],
            'ai_ml': ['artificial intelligence', 'machine learning', 'neural network', 'deep learning', 'computer vision', 'nlp', 'robotics'],
            'energy': ['renewable energy', 'solar', 'wind', 'battery', 'energy storage', 'fuel cell', 'nuclear', 'clean energy'],
            'biotech': ['biotechnology', 'genomics', 'bioinformatics', 'pharmaceutical', 'medical device', 'drug discovery'],
            'materials': ['advanced materials', 'nanotechnology', 'composites', 'metamaterials', 'smart materials'],
            'defense': ['defense', 'security', 'cybersecurity', 'surveillance', 'military', 'homeland security'],
            'climate': ['climate change', 'environmental', 'sustainability', 'carbon capture', 'green technology'],
            'quantum': ['quantum computing', 'quantum communication', 'quantum sensing', 'quantum cryptography'],
            'education': ['education', 'outreach', 'stem', 'workforce development', 'training'],
            'healthcare': ['healthcare', 'medical', 'clinical', 'therapy', 'diagnostic', 'patient care']
        }

    def discover_opportunities(self, max_per_source: int = 20) -> List[Dict]:
        """Discover opportunities from all sources"""
        all_opportunities = []
        
        for org_name, source_info in self.opportunity_sources.items():
            print(f"🔍 Discovering opportunities from {org_name}...")
            
            for url in source_info['urls']:
                try:
                    opportunities = self._scrape_website(url, source_info['keywords'], org_name)
                    all_opportunities.extend(opportunities[:max_per_source])
                except Exception as e:
                    print(f"❌ Error scraping {url}: {e}")
                    continue
        
        # Process and classify opportunities
        classified_opportunities = []
        for opp in all_opportunities:
            classified_opp = self._classify_opportunity(opp)
            classified_opportunities.append(classified_opp)
        
        print(f"✅ Discovered {len(classified_opportunities)} opportunities total")
        return classified_opportunities

    def _scrape_website(self, url: str, keywords: List[str], organization: str) -> List[Dict]:
        """Scrape a single website for opportunities"""
        opportunities = []
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; ProposalAI/1.0; Research)'
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find potential opportunity elements
            opportunity_elements = self._find_opportunity_elements(soup, keywords)
            
            for element in opportunity_elements:
                opportunity = self._extract_opportunity_data(element, url, organization)
                if opportunity and self._is_valid_opportunity(opportunity):
                    opportunities.append(opportunity)
                    
        except Exception as e:
            print(f"⚠️ Failed to scrape {url}: {e}")
        
        return opportunities

    def _find_opportunity_elements(self, soup: BeautifulSoup, keywords: List[str]) -> List:
        """Find HTML elements that likely contain opportunities"""
        elements = []
        
        # Look for various selectors that might contain opportunities
        selectors = [
            'article', 'div.opportunity', 'div.call', 'div.funding',
            'div.grant', 'div.proposal', 'div.competition', 'li.opportunity',
            'tr', 'div.content', 'div.announcement', 'div.news-item'
        ]
        
        for selector in selectors:
            found_elements = soup.select(selector)
            for element in found_elements:
                text = element.get_text().lower()
                if any(keyword.lower() in text for keyword in keywords):
                    elements.append(element)
        
        # Also look for links with opportunity-related text
        links = soup.find_all('a')
        for link in links:
            link_text = link.get_text().lower()
            if any(keyword.lower() in link_text for keyword in keywords):
                elements.append(link)
        
        return elements[:50]  # Limit to prevent excessive processing

    def _extract_opportunity_data(self, element, base_url: str, organization: str) -> Optional[Dict]:
        """Extract opportunity data from an HTML element"""
        try:
            # Extract title
            title = self._extract_title_from_element(element)
            
            # Extract description
            description = element.get_text().strip()[:2000]
            
            # Extract link
            link = self._extract_link_from_element(element, base_url)
            
            # Extract deadline (if visible in the element)
            deadline = self._extract_deadline_from_text(description)
            
            if title and len(description) > 50:
                return {
                    'title': title,
                    'description': description,
                    'organization': organization,
                    'url': link or base_url,
                    'deadline': deadline,
                    'source_url': base_url,
                    'extracted_at': datetime.now().isoformat(),
                    'keywords': self._extract_keywords_from_text(description)
                }
        
        except Exception as e:
            print(f"⚠️ Error extracting opportunity data: {e}")
        
        return None

    def _extract_title_from_element(self, element) -> Optional[str]:
        """Extract title from an element"""
        # Try different title selectors
        title_selectors = ['h1', 'h2', 'h3', 'h4', '.title', '.heading', 'strong', 'b']
        
        for selector in title_selectors:
            title_element = element.select_one(selector)
            if title_element:
                title = title_element.get_text().strip()
                if 10 <= len(title) <= 200:  # Reasonable title length
                    return title
        
        # Fallback: use link text if it's a link
        if element.name == 'a':
            return element.get_text().strip()[:200]
        
        return None

    def _extract_link_from_element(self, element, base_url: str) -> Optional[str]:
        """Extract link from an element"""
        if element.name == 'a' and element.get('href'):
            return urljoin(base_url, element.get('href'))
        
        # Look for links within the element
        link = element.find('a')
        if link and link.get('href'):
            return urljoin(base_url, link.get('href'))
        
        return None

    def _extract_deadline_from_text(self, text: str) -> Optional[str]:
        """Extract deadline from text using regex patterns"""
        text_lower = text.lower()
        
        # Common deadline patterns
        patterns = [
            r'deadline[:\s]*([^.]+)',
            r'due[:\s]*([^.]+)',
            r'closes?[:\s]*([^.]+)',
            r'submit by[:\s]*([^.]+)',
            r'application deadline[:\s]*([^.]+)',
            r'proposal due[:\s]*([^.]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                deadline_text = match.group(1).strip()
                # Look for actual dates
                date_patterns = [
                    r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',
                    r'\d{4}-\d{2}-\d{2}',
                    r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2},?\s+\d{4}'
                ]
                
                for date_pattern in date_patterns:
                    date_match = re.search(date_pattern, deadline_text, re.IGNORECASE)
                    if date_match:
                        return date_match.group(0)
                
                return deadline_text[:100]  # Return first part if no specific date
        
        return None

    def _extract_keywords_from_text(self, text: str) -> List[str]:
        """Extract relevant keywords from text using NLP"""
        doc = self.nlp(text)
        
        keywords = []
        
        # Extract entities
        for ent in doc.ents:
            if ent.label_ in ['ORG', 'PRODUCT', 'EVENT', 'WORK_OF_ART']:
                keywords.append(ent.text.lower())
        
        # Extract key phrases (noun phrases)
        for chunk in doc.noun_chunks:
            if len(chunk.text.split()) <= 3:  # Limit to 3-word phrases
                keywords.append(chunk.text.lower())
        
        # Match against our keyword categories
        text_lower = text.lower()
        for category, category_keywords in self.keyword_categories.items():
            for keyword in category_keywords:
                if keyword in text_lower:
                    keywords.append(f"{category}:{keyword}")
        
        return list(set(keywords))[:20]  # Limit and deduplicate

    def _classify_opportunity(self, opportunity: Dict) -> Dict:
        """Classify opportunity into categories"""
        text = f"{opportunity.get('title', '')} {opportunity.get('description', '')}"
        text_lower = text.lower()
        
        # Determine primary categories
        categories = []
        category_scores = {}
        
        for category, keywords in self.keyword_categories.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                categories.append(category)
                category_scores[category] = score
        
        # Sort categories by relevance
        categories.sort(key=lambda x: category_scores.get(x, 0), reverse=True)
        
        # Determine funding amount (if mentioned)
        funding_amount = self._extract_funding_amount(text)
        
        # Determine opportunity type
        opp_type = self._determine_opportunity_type(text_lower)
        
        opportunity.update({
            'categories': categories[:5],  # Top 5 categories
            'primary_category': categories[0] if categories else 'general',
            'category_scores': category_scores,
            'estimated_funding': funding_amount,
            'opportunity_type': opp_type,
            'relevance_score': self._calculate_relevance_score(opportunity)
        })
        
        return opportunity

    def _extract_funding_amount(self, text: str) -> Optional[str]:
        """Extract funding amount from text"""
        # Look for monetary amounts
        patterns = [
            r'\$[\d,]+(?:\.\d{2})?',
            r'[\d,]+\s*(?:million|thousand|billion)?\s*(?:dollars|USD|EUR|GBP)',
            r'up to\s*\$[\d,]+',
            r'maximum\s*\$[\d,]+'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return None

    def _determine_opportunity_type(self, text: str) -> str:
        """Determine the type of opportunity"""
        if any(word in text for word in ['grant', 'funding', 'award']):
            return 'grant'
        elif any(word in text for word in ['competition', 'challenge', 'prize']):
            return 'competition'
        elif any(word in text for word in ['conference', 'paper', 'abstract']):
            return 'conference'
        elif any(word in text for word in ['collaboration', 'partnership']):
            return 'collaboration'
        elif any(word in text for word in ['job', 'position', 'hiring']):
            return 'employment'
        else:
            return 'other'

    def _calculate_relevance_score(self, opportunity: Dict) -> float:
        """Calculate relevance score for an opportunity"""
        score = 0.0
        
        # Base score for having key information
        if opportunity.get('title'):
            score += 0.2
        if opportunity.get('description') and len(opportunity['description']) > 100:
            score += 0.2
        if opportunity.get('deadline'):
            score += 0.2
        if opportunity.get('url'):
            score += 0.1
        
        # Category-based scoring
        categories = opportunity.get('categories', [])
        if categories:
            score += 0.2 * min(len(categories), 3)  # More categories = more relevant
        
        # Funding amount bonus
        if opportunity.get('estimated_funding'):
            score += 0.1
        
        return min(score, 1.0)

    def _is_valid_opportunity(self, opportunity: Dict) -> bool:
        """Check if an opportunity is valid and worth storing"""
        # Must have title and description
        if not opportunity.get('title') or not opportunity.get('description'):
            return False
        
        # Title should be reasonable length
        title = opportunity['title']
        if len(title) < 10 or len(title) > 500:
            return False
        
        # Description should be substantial
        description = opportunity['description']
        if len(description) < 50:
            return False
        
        # Should have some relevance
        relevance_score = opportunity.get('relevance_score', 0)
        if relevance_score < 0.3:
            return False
        
        return True

    def match_opportunities_to_profile(self, profile_data: Dict, opportunities: List[Dict], top_n: int = 20) -> List[Dict]:
        """Match opportunities to a user profile/resume"""
        if not opportunities:
            return []
        
        # Create profile text
        profile_text = self._create_profile_text(profile_data)
        
        # Create opportunity texts
        opp_texts = []
        for opp in opportunities:
            opp_text = f"{opp.get('title', '')} {opp.get('description', '')} {' '.join(opp.get('keywords', []))}"
            opp_texts.append(opp_text)
        
        # Calculate similarities using TF-IDF
        all_texts = [profile_text] + opp_texts
        tfidf_matrix = self.vectorizer.fit_transform(all_texts)
        
        # Calculate cosine similarities
        profile_vector = tfidf_matrix[0:1]
        opp_vectors = tfidf_matrix[1:]
        similarities = cosine_similarity(profile_vector, opp_vectors)[0]
        
        # Add similarity scores to opportunities
        scored_opportunities = []
        for i, opp in enumerate(opportunities):
            opp_copy = opp.copy()
            opp_copy['profile_match_score'] = float(similarities[i])
            opp_copy['combined_score'] = (similarities[i] * 0.7) + (opp.get('relevance_score', 0) * 0.3)
            scored_opportunities.append(opp_copy)
        
        # Sort by combined score and return top N
        scored_opportunities.sort(key=lambda x: x['combined_score'], reverse=True)
        return scored_opportunities[:top_n]

    def _create_profile_text(self, profile_data: Dict) -> str:
        """Create a text representation of user profile for matching"""
        profile_parts = []
        
        # Add various profile fields
        fields_to_include = [
            'skills', 'experience', 'education', 'research_interests',
            'expertise', 'background', 'keywords', 'specialization',
            'industry', 'technologies', 'publications'
        ]
        
        for field in fields_to_include:
            if field in profile_data and profile_data[field]:
                if isinstance(profile_data[field], list):
                    profile_parts.extend(profile_data[field])
                else:
                    profile_parts.append(str(profile_data[field]))
        
        return ' '.join(profile_parts)

    def match_proposal_to_opportunities(self, proposal_text: str, opportunities: List[Dict], top_n: int = 10) -> List[Dict]:
        """Match a proposal to relevant opportunities"""
        if not opportunities:
            return []
        
        # Extract key information from proposal
        proposal_keywords = self._extract_keywords_from_text(proposal_text)
        proposal_categories = self._classify_text_categories(proposal_text)
        
        # Score opportunities based on proposal content
        scored_opportunities = []
        for opp in opportunities:
            # Calculate keyword overlap
            opp_keywords = opp.get('keywords', [])
            keyword_overlap = len(set(proposal_keywords) & set(opp_keywords))
            
            # Calculate category overlap
            opp_categories = opp.get('categories', [])
            category_overlap = len(set(proposal_categories) & set(opp_categories))
            
            # Calculate text similarity
            opp_text = f"{opp.get('title', '')} {opp.get('description', '')}"
            all_texts = [proposal_text, opp_text]
            tfidf_matrix = self.vectorizer.fit_transform(all_texts)
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            # Combined score
            match_score = (
                similarity * 0.5 +
                (keyword_overlap / max(len(proposal_keywords), 1)) * 0.3 +
                (category_overlap / max(len(proposal_categories), 1)) * 0.2
            )
            
            opp_copy = opp.copy()
            opp_copy['proposal_match_score'] = float(match_score)
            opp_copy['keyword_overlap'] = keyword_overlap
            opp_copy['category_overlap'] = category_overlap
            scored_opportunities.append(opp_copy)
        
        # Sort by match score
        scored_opportunities.sort(key=lambda x: x['proposal_match_score'], reverse=True)
        return scored_opportunities[:top_n]

    def _classify_text_categories(self, text: str) -> List[str]:
        """Classify text into our predefined categories"""
        text_lower = text.lower()
        categories = []
        
        for category, keywords in self.keyword_categories.items():
            if any(keyword in text_lower for keyword in keywords):
                categories.append(category)
        
        return categories

    def save_opportunities_to_database(self, opportunities: List[Dict]):
        """Save discovered opportunities to database"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        saved_count = 0
        for opp in opportunities:
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO scraped_opportunities 
                    (source_url, title, description, deadline, category, keywords, raw_data, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    opp.get('source_url'),
                    opp.get('title'),
                    opp.get('description'),
                    opp.get('deadline'),
                    opp.get('primary_category'),
                    json.dumps(opp.get('keywords', [])),
                    json.dumps(opp),
                    datetime.now().isoformat()
                ))
                saved_count += 1
            except Exception as e:
                print(f"⚠️ Error saving opportunity: {e}")
        
        conn.commit()
        conn.close()
        print(f"💾 Saved {saved_count} opportunities to database")
        return saved_count


# Testing function
def test_enhanced_discovery():
    """Test the enhanced discovery engine"""
    discoverer = EnhancedOpportunityDiscoverer()
    
    # Test with a limited set first
    print("🧪 Testing enhanced discovery engine...")
    opportunities = discoverer.discover_opportunities(max_per_source=5)
    
    if opportunities:
        print(f"✅ Found {len(opportunities)} opportunities")
        
        # Save to database
        discoverer.save_opportunities_to_database(opportunities)
        
        # Test profile matching
        test_profile = {
            'skills': ['machine learning', 'space technology', 'python', 'data science'],
            'experience': 'AI researcher with focus on space applications',
            'education': 'PhD in Computer Science',
            'research_interests': ['artificial intelligence', 'satellite data processing']
        }
        
        matched_opps = discoverer.match_opportunities_to_profile(test_profile, opportunities, top_n=10)
        print(f"🎯 Top 10 matched opportunities:")
        for i, opp in enumerate(matched_opps[:5], 1):
            print(f"  {i}. {opp['title'][:80]}... (Score: {opp['combined_score']:.3f})")
    
    else:
        print("❌ No opportunities found")


if __name__ == "__main__":
    test_enhanced_discovery()
