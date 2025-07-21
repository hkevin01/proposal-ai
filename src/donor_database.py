#!/usr/bin/env python3
"""
Donor and Foundation Database Management System
Manages information about potential donors, foundations, and funding orgs
"""

import json
import logging
import re
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import requests
from bs4 import BeautifulSoup

from .config import DONORS_DATABASE_PATH

@dataclass
class Donor:
    """Represents a donor or foundation"""
    id: Optional[int] = None
    name: str = ""
    type: str = ""  # individual, foundation, corporation, government
    region: str = ""
    country: str = ""
    focus_areas: List[str] = None
    website: str = ""
    contact_email: str = ""
    contact_phone: str = ""
    description: str = ""
    giving_amount: str = ""  # estimated annual giving
    application_process: str = ""
    deadlines: str = ""
    requirements: str = ""
    success_stories: str = ""
    last_updated: str = ""
    
    def __post_init__(self):
        if self.focus_areas is None:
            self.focus_areas = []
        if not self.last_updated:
            self.last_updated = datetime.now().isoformat()

class DonorDatabase:
    """Manages donor and foundation information"""
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or DONORS_DATABASE_PATH
        self.logger = logging.getLogger(__name__)
        self.init_database()
        self.populate_initial_donors()

    def init_database(self):
        """Initialize the donor database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS donors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    type TEXT,
                    region TEXT,
                    country TEXT,
                    focus_areas TEXT,
                    website TEXT,
                    contact_email TEXT,
                    contact_phone TEXT,
                    description TEXT,
                    giving_amount TEXT,
                    application_process TEXT,
                    deadlines TEXT,
                    requirements TEXT,
                    success_stories TEXT,
                    last_updated TEXT
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS donor_matches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    donor_id INTEGER,
                    opportunity_id INTEGER,
                    match_score REAL,
                    match_reasons TEXT,
                    created_at TEXT,
                    FOREIGN KEY (donor_id) REFERENCES donors (id)
                )
            ''')
            conn.commit()
            conn.close()
            self.logger.info("Donor database initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing donor database: {e}")

    def add_donor(self, donor: Donor) -> int:
        """Add a new donor to the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            focus_areas_json = json.dumps(donor.focus_areas)
            cursor.execute('''
                INSERT OR REPLACE INTO donors
                (name, type, region, country, focus_areas, website,
                 contact_email, contact_phone, description, giving_amount,
                 application_process, deadlines, requirements,
                 success_stories, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                donor.name, donor.type, donor.region, donor.country,
                focus_areas_json, donor.website, donor.contact_email,
                donor.contact_phone, donor.description, donor.giving_amount,
                donor.application_process, donor.deadlines, donor.requirements,
                donor.success_stories, donor.last_updated
            ))
            donor_id = cursor.lastrowid
            conn.commit()
            conn.close()
            self.logger.info(f"Added donor: {donor.name}")
            return donor_id
        except Exception as e:
            self.logger.error(f"Error adding donor {donor.name}: {e}")
            return -1

    def get_donors(self, limit: int = 100) -> List[Donor]:
        """Get all donors from the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM donors LIMIT ?', (limit,))
            rows = cursor.fetchall()
            conn.close()
            donors = []
            for row in rows:
                donor = Donor(
                    id=row[0], name=row[1], type=row[2], region=row[3],
                    country=row[4], focus_areas=json.loads(row[5] or '[]'),
                    website=row[6], contact_email=row[7], contact_phone=row[8],
                    description=row[9], giving_amount=row[10],
                    application_process=row[11], deadlines=row[12],
                    requirements=row[13], success_stories=row[14],
                    last_updated=row[15]
                )
                donors.append(donor)
            return donors
        except Exception as e:
            self.logger.error(f"Error getting donors: {e}")
            return []

    def search_donors(self, query: str, focus_area: str = None,
                      region: str = None, donor_type: str = None
                      ) -> List[Donor]:
        """Search donors by various criteria"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            where_clauses = []
            params = []
            if query:
                where_clauses.append('''
                    (name LIKE ? OR description LIKE ? OR focus_areas LIKE ?)
                ''')
                query_param = f'%{query}%'
                params.extend([query_param, query_param, query_param])
            if focus_area:
                where_clauses.append('focus_areas LIKE ?')
                params.append(f'%{focus_area}%')
            if region:
                where_clauses.append('region LIKE ?')
                params.append(f'%{region}%')
            if donor_type:
                where_clauses.append('type = ?')
                params.append(donor_type)
            where_clause = (' AND '.join(where_clauses)
                            if where_clauses else '1=1')
            cursor.execute(f'''
                SELECT * FROM donors WHERE {where_clause}
                ORDER BY name
            ''', params)
            rows = cursor.fetchall()
            conn.close()
            donors = []
            for row in rows:
                donor = Donor(
                    id=row[0], name=row[1], type=row[2], region=row[3],
                    country=row[4], focus_areas=json.loads(row[5] or '[]'),
                    website=row[6], contact_email=row[7], contact_phone=row[8],
                    description=row[9], giving_amount=row[10],
                    application_process=row[11], deadlines=row[12],
                    requirements=row[13], success_stories=row[14],
                    last_updated=row[15]
                )
                donors.append(donor)
            return donors
        except Exception as e:
            self.logger.error(f"Error searching donors: {e}")
            return []

    def find_matching_donors(self, opportunity_keywords: List[str],
                             opportunity_type: str = None
                             ) -> List[Tuple[Donor, float]]:
        """Find donors that match an opportunity"""
        try:
            all_donors = self.get_donors()
            matches = []
            for donor in all_donors:
                score = self._calculate_match_score(
                    donor, opportunity_keywords, opportunity_type)
                if score > 0.3:  # Minimum threshold
                    matches.append((donor, score))
            # Sort by match score descending
            matches.sort(key=lambda x: x[1], reverse=True)
            return matches[:10]  # Return top 10 matches
        except Exception as e:
            self.logger.error(f"Error finding matching donors: {e}")
            return []

    def _calculate_match_score(self, donor: Donor, keywords: List[str],
                               opportunity_type: Optional[str] = None
                               ) -> float:
        """Calculate how well a donor matches an opportunity"""
        score = 0.0
        # Check focus areas
        donor_text = ' '.join(donor.focus_areas).lower()
        donor_text += f" {donor.description.lower()}"
        keyword_matches = 0
        for keyword in keywords:
            if keyword.lower() in donor_text:
                keyword_matches += 1
        if keywords:
            score += (keyword_matches / len(keywords)) * 0.6
        # Type-specific matching
        if opportunity_type:
            type_keywords = {
                'research': ['research', 'science', 'education', 'innovation'],
                'space': ['space', 'aerospace', 'technology', 'exploration'],
                'education': ['education', 'learning', 'students', 'schools'],
                'health': ['health', 'medical', 'healthcare', 'medicine'],
                'environment': ['environment', 'climate', 'sustainability',
                                'conservation']
            }
            if opportunity_type.lower() in type_keywords:
                type_words = type_keywords[opportunity_type.lower()]
                for word in type_words:
                    if word in donor_text:
                        score += 0.1
        return min(score, 1.0)  # Cap at 1.0

    def save_donor_match(self, donor_id: int, opportunity_id: int,
                         score: float, reasons: str):
        """Save a donor-opportunity match"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO donor_matches
                (donor_id, opportunity_id, match_score, match_reasons,
                 created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (donor_id, opportunity_id, score, reasons,
                  datetime.now().isoformat()))
            conn.commit()
            conn.close()
            self.logger.info(f"Saved donor match: {donor_id} -> {opportunity_id}")
        except Exception as e:
            self.logger.error(f"Error saving donor match: {e}")

    def get_donor_matches(self, opportunity_id: int) -> List[Dict]:
        """Get all donor matches for an opportunity"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT d.*, dm.match_score, dm.match_reasons 
                FROM donors d
                JOIN donor_matches dm ON d.id = dm.donor_id
                WHERE dm.opportunity_id = ?
                ORDER BY dm.match_score DESC
            ''', (opportunity_id,))
            rows = cursor.fetchall()
            conn.close()
            matches = []
            for row in rows:
                match = {
                    'donor': Donor(
                        id=row[0], name=row[1], type=row[2], region=row[3],
                        country=row[4], focus_areas=json.loads(row[5] or '[]'),
                        website=row[6], contact_email=row[7], contact_phone=row[8],
                        description=row[9], giving_amount=row[10],
                        application_process=row[11], deadlines=row[12],
                        requirements=row[13], success_stories=row[14],
                        last_updated=row[15]
                    ),
                    'score': row[16],
                    'reasons': row[17]
                }
                matches.append(match)
            return matches
        except Exception as e:
            self.logger.error(f"Error getting donor matches: {e}")
            return []

    def update_donor_website_info(self, donor_id: int) -> bool:
        """Update donor information by scraping their website"""
        try:
            donor = self.get_donor_by_id(donor_id)
            if not donor or not donor.website:
                return False
            # Simple web scraping to get additional info
            response = requests.get(donor.website, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            # Extract meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc and not donor.description:
                donor.description = meta_desc.get('content', '')[:1000]
            # Look for contact information
            if not donor.contact_email:
                email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                emails = re.findall(email_pattern, response.text)
                if emails:
                    donor.contact_email = emails[0]
            # Update the donor
            self.add_donor(donor)
            return True
        except Exception as e:
            self.logger.error(f"Error updating donor website info: {e}")
            return False

    def get_donor_by_id(self, donor_id: int) -> Optional[Donor]:
        """Get a specific donor by ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM donors WHERE id = ?', (donor_id,))
            row = cursor.fetchone()
            conn.close()
            if row:
                return Donor(
                    id=row[0], name=row[1], type=row[2], region=row[3],
                    country=row[4], focus_areas=json.loads(row[5] or '[]'),
                    website=row[6], contact_email=row[7], contact_phone=row[8],
                    description=row[9], giving_amount=row[10],
                    application_process=row[11], deadlines=row[12],
                    requirements=row[13], success_stories=row[14],
                    last_updated=row[15]
                )
            return None
        except Exception as e:
            self.logger.error(f"Error getting donor by ID: {e}")
            return None

    def populate_initial_donors(self):
        """Populate database with initial donor data from donors.md"""
        try:
            # Check if we already have donors
            existing_donors = self.get_donors(limit=1)
            if existing_donors:
                return  # Already populated
            # Define initial donors based on donors.md
            initial_donors = [
                Donor(
                    name="MacKenzie Scott",
                    type="individual",
                    region="North America",
                    country="USA",
                    focus_areas=["inequality reduction", "education", "community development"],
                    description="Known for low-profile and highly impactful giving, donated over $14 billion to nonprofits and underserved communities",
                    giving_amount="$14+ billion",
                    website="https://mackenzie-scott.medium.com/"
                ),
                Donor(
                    name="Warren Buffett",
                    type="individual", 
                    region="North America",
                    country="USA",
                    focus_areas=["charity", "education", "healthcare"],
                    description="Pledged to donate over 99% of wealth through the Giving Pledge",
                    giving_amount="$50+ billion pledged",
                    website="https://www.berkshirehathaway.com/"
                ),
                Donor(
                    name="The Giving Pledge",
                    type="foundation",
                    region="Global",
                    country="USA",
                    focus_areas=["philanthropy", "social impact", "global development"],
                    description="Network of billionaires pledging to donate most of their wealth",
                    website="https://givingpledge.org/"
                ),
                Donor(
                    name="Tata Trusts",
                    type="foundation",
                    region="Asia",
                    country="India",
                    focus_areas=["healthcare", "education", "rural development"],
                    description="One of India's largest philanthropic organizations",
                    giving_amount="Billions annually",
                    website="https://www.tatatrusts.org/"
                ),
                Donor(
                    name="Patagonia Foundation",
                    type="corporation",
                    region="North America", 
                    country="USA",
                    focus_areas=["environmental conservation", "climate change", "land protection"],
                    description="All profits dedicated to fighting climate change and protecting undeveloped land",
                    website="https://www.patagonia.com/ownership/"
                ),
                Donor(
                    name="Bill & Melinda Gates Foundation",
                    type="foundation",
                    region="Global",
                    country="USA",
                    focus_areas=["global health", "education", "poverty alleviation"],
                    description="One of the world's largest private foundations",
                    giving_amount="$50+ billion",
                    website="https://www.gatesfoundation.org/"
                ),
                Donor(
                    name="Chan Zuckerberg Initiative",
                    type="foundation",
                    region="North America",
                    country="USA", 
                    focus_areas=["science", "education", "justice & opportunity"],
                    description="Focuses on advancing human potential and promoting equality",
                    giving_amount="$45 billion pledged",
                    website="https://chanzuckerberg.com/"
                ),
                Donor(
                    name="Open Society Foundations",
                    type="foundation",
                    region="Global",
                    country="USA",
                    focus_areas=["human rights", "democracy", "justice"],
                    description="Works to build vibrant and tolerant societies",
                    giving_amount="$18+ billion",
                    website="https://www.opensocietyfoundations.org/"
                ),
                Donor(
                    name="Ford Foundation",
                    type="foundation",
                    region="Global",
                    country="USA",
                    focus_areas=["inequality", "democracy", "education"],
                    description="Fights inequality and strengthens democratic values",
                    giving_amount="$600+ million annually",
                    website="https://www.fordfoundation.org/"
                ),
                Donor(
                    name="Rockefeller Foundation",
                    type="foundation",
                    region="Global",
                    country="USA",
                    focus_areas=["resilience", "equity", "innovation"],
                    description="Works to promote the well-being of humanity",
                    giving_amount="$200+ million annually",
                    website="https://www.rockefellerfoundation.org/"
                )
            ]
            for donor in initial_donors:
                self.add_donor(donor)
            self.logger.info(f"Populated database with {len(initial_donors)} initial donors")
        except Exception as e:
            self.logger.error(f"Error populating initial donors: {e}")

def main():
    """Test the donor database functionality"""
    logging.basicConfig(level=logging.INFO)
    # Initialize database
    db = DonorDatabase()
    # Search for donors
    education_donors = db.search_donors("education")
    print(f"Found {len(education_donors)} education-focused donors")
    # Find matching donors for a space opportunity
    space_keywords = ["space", "aerospace", "satellite", "exploration"]
    matches = db.find_matching_donors(space_keywords, "space")
    print(f"\nTop donor matches for space opportunity:")
    for donor, score in matches[:5]:
        print(f"- {donor.name}: {score:.2f}")

if __name__ == "__main__":
    main()