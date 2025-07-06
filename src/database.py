"""
Database setup and models for Proposal AI
"""
import sqlite3
from datetime import datetime
from typing import Dict, Optional

DATABASE_PATH = "proposal_ai.db"


def setup_database():
    """Create database tables if they don't exist"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Organizations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS organizations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            industry TEXT,
            website TEXT,
            contact_info TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Events table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            organization_id INTEGER,
            event_date TEXT,
            deadline TEXT,
            description TEXT,
            url TEXT,
            requirements TEXT,
            status TEXT DEFAULT 'open',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (organization_id) REFERENCES organizations (id)
        )
    ''')
    
    # Proposals table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS proposals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER,
            user_id INTEGER,
            title TEXT,
            status TEXT DEFAULT 'draft',
            submission_date TEXT,
            document_path TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (event_id) REFERENCES events (id)
        )
    ''')
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE,
            affiliation TEXT,
            preferences TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
     # Scraped data table for raw opportunity data
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scraped_opportunities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_url TEXT,
            title TEXT,
            description TEXT,
            deadline TEXT,
            category TEXT,
            keywords TEXT,
            raw_data TEXT,
            processed BOOLEAN DEFAULT FALSE,
            relevance_score REAL DEFAULT 0.0,
            estimated_funding TEXT,
            opportunity_type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # User profiles table for resume/background data
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            resume_text TEXT,
            skills TEXT,
            experience TEXT,
            education TEXT,
            research_interests TEXT,
            expertise TEXT,
            background TEXT,
            keywords TEXT,
            specialization TEXT,
            industry TEXT,
            technologies TEXT,
            publications TEXT,
            file_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Opportunity matches table for storing user-opportunity matches
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS opportunity_matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            opportunity_id INTEGER,
            profile_match_score REAL,
            relevance_score REAL,
            combined_score REAL,
            match_keywords TEXT,
            match_categories TEXT,
            is_bookmarked BOOLEAN DEFAULT FALSE,
            is_applied BOOLEAN DEFAULT FALSE,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (opportunity_id) REFERENCES scraped_opportunities (id)
        )
    ''')
    
    # Proposal matches table for proposal-opportunity matching
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS proposal_matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            proposal_id INTEGER,
            opportunity_id INTEGER,
            proposal_match_score REAL,
            keyword_overlap INTEGER,
            category_overlap INTEGER,
            text_similarity REAL,
            is_recommended BOOLEAN DEFAULT FALSE,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (proposal_id) REFERENCES proposals (id),
            FOREIGN KEY (opportunity_id) REFERENCES scraped_opportunities (id)
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ Database setup complete!")


def get_connection():
    """Get database connection"""
    return sqlite3.connect(DATABASE_PATH)


class DatabaseManager:
    """Database operations manager"""
    
    def __init__(self):
        self.db_path = DATABASE_PATH
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def add_organization(self, name: str, industry: Optional[str] = None, 
                        website: Optional[str] = None, contact_info: Optional[str] = None):
        """Add a new organization"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO organizations (name, industry, website, contact_info) VALUES (?, ?, ?, ?)",
            (name, industry, website, contact_info)
        )
        org_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return org_id
    
    def add_event(self, name: str, organization_id: Optional[int] = None, event_date: Optional[str] = None, 
                  deadline: Optional[str] = None, description: Optional[str] = None, 
                  url: Optional[str] = None, requirements: Optional[str] = None):
        """Add a new event/opportunity"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO events (name, organization_id, event_date, deadline, description, url, requirements) 
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (name, organization_id, event_date, deadline, description, url, requirements)
        )
        event_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return event_id
    
    def get_events(self, status: Optional[str] = None):
        """Get all events/opportunities"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if status:
            cursor.execute(
                """SELECT e.*, o.name as org_name FROM events e 
                   LEFT JOIN organizations o ON e.organization_id = o.id 
                   WHERE e.status = ?""", (status,)
            )
        else:
            cursor.execute(
                """SELECT e.*, o.name as org_name FROM events e 
                   LEFT JOIN organizations o ON e.organization_id = o.id"""
            )
        
        events = cursor.fetchall()
        conn.close()
        return events
    
    def add_scraped_opportunity(self, source_url: str, title: str, description: Optional[str] = None, 
                               deadline: Optional[str] = None, category: Optional[str] = None, 
                               keywords: Optional[str] = None, raw_data: Optional[str] = None,
                               relevance_score: Optional[float] = None, estimated_funding: Optional[str] = None,
                               opportunity_type: Optional[str] = None):
        """Add scraped opportunity data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO scraped_opportunities 
               (source_url, title, description, deadline, category, keywords, raw_data, 
                relevance_score, estimated_funding, opportunity_type) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (source_url, title, description, deadline, category, keywords, raw_data,
             relevance_score, estimated_funding, opportunity_type)
        )
        opportunity_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return opportunity_id
    
    def get_unprocessed_opportunities(self):
        """Get unprocessed scraped opportunities"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM scraped_opportunities WHERE processed = FALSE")
        opportunities = cursor.fetchall()
        conn.close()
        return opportunities
    
    def add_user_profile(self, user_id: int, resume_text: Optional[str] = None,
                        skills: Optional[str] = None, experience: Optional[str] = None,
                        education: Optional[str] = None, research_interests: Optional[str] = None,
                        expertise: Optional[str] = None, background: Optional[str] = None,
                        keywords: Optional[str] = None, specialization: Optional[str] = None,
                        industry: Optional[str] = None, technologies: Optional[str] = None,
                        publications: Optional[str] = None, file_path: Optional[str] = None):
        """Add or update user profile"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Check if profile exists
        cursor.execute("SELECT id FROM user_profiles WHERE user_id = ?", (user_id,))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing profile
            cursor.execute(
                """UPDATE user_profiles SET 
                   resume_text=?, skills=?, experience=?, education=?, research_interests=?,
                   expertise=?, background=?, keywords=?, specialization=?, industry=?,
                   technologies=?, publications=?, file_path=?, updated_at=CURRENT_TIMESTAMP
                   WHERE user_id=?""",
                (resume_text, skills, experience, education, research_interests,
                 expertise, background, keywords, specialization, industry,
                 technologies, publications, file_path, user_id)
            )
            profile_id = existing[0]
        else:
            # Insert new profile
            cursor.execute(
                """INSERT INTO user_profiles 
                   (user_id, resume_text, skills, experience, education, research_interests,
                    expertise, background, keywords, specialization, industry,
                    technologies, publications, file_path)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (user_id, resume_text, skills, experience, education, research_interests,
                 expertise, background, keywords, specialization, industry,
                 technologies, publications, file_path)
            )
            profile_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        return profile_id
    
    def get_user_profile(self, user_id: int):
        """Get user profile by user ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_profiles WHERE user_id = ?", (user_id,))
        profile = cursor.fetchone()
        conn.close()
        return profile
    
    def add_opportunity_match(self, user_id: int, opportunity_id: int, 
                             profile_match_score: float, relevance_score: float,
                             combined_score: float, match_keywords: Optional[str] = None,
                             match_categories: Optional[str] = None):
        """Add opportunity match for a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO opportunity_matches 
               (user_id, opportunity_id, profile_match_score, relevance_score, 
                combined_score, match_keywords, match_categories)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (user_id, opportunity_id, profile_match_score, relevance_score,
             combined_score, match_keywords, match_categories)
        )
        match_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return match_id
    
    def get_user_opportunity_matches(self, user_id: int, top_n: int = 20):
        """Get top opportunity matches for a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT om.*, so.title, so.description, so.deadline, so.source_url 
               FROM opportunity_matches om
               JOIN scraped_opportunities so ON om.opportunity_id = so.id
               WHERE om.user_id = ?
               ORDER BY om.combined_score DESC
               LIMIT ?""",
            (user_id, top_n)
        )
        matches = cursor.fetchall()
        conn.close()
        return matches
    
    def save_opportunity(self, opportunity: Dict):
        """Save an opportunity to the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Check if opportunity already exists (by title and source)
            cursor.execute(
                "SELECT id FROM scraped_opportunities WHERE title = ? AND source_url = ?",
                (opportunity.get('title', ''), opportunity.get('url', ''))
            )
            existing = cursor.fetchone()
            
            if existing:
                # Update existing opportunity
                cursor.execute(
                    """UPDATE scraped_opportunities SET 
                       description = ?, deadline = ?, category = ?, 
                       estimated_funding = ?, relevance_score = ?, 
                       opportunity_type = ?
                       WHERE id = ?""",
                    (opportunity.get('description', ''),
                     opportunity.get('deadline', ''),
                     opportunity.get('category', ''),
                     opportunity.get('funding_amount', ''),
                     opportunity.get('ai_relevance_score', 0.0),
                     opportunity.get('source', ''),
                     existing[0])
                )
                opportunity_id = existing[0]
            else:
                # Insert new opportunity
                cursor.execute(
                    """INSERT INTO scraped_opportunities 
                       (source_url, title, description, deadline, category, 
                        estimated_funding, relevance_score, opportunity_type) 
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (opportunity.get('url', ''),
                     opportunity.get('title', ''),
                     opportunity.get('description', ''),
                     opportunity.get('deadline', ''),
                     opportunity.get('category', ''),
                     opportunity.get('funding_amount', ''),
                     opportunity.get('ai_relevance_score', 0.0),
                     opportunity.get('source', ''))
                )
                opportunity_id = cursor.lastrowid
            
            conn.commit()
            return opportunity_id
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def get_opportunities(self, limit: int = 100):
        """Get all discovered opportunities"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT id, title, description, deadline, category, 
                      estimated_funding, opportunity_type, relevance_score, 
                      source_url, created_at 
               FROM scraped_opportunities 
               ORDER BY created_at DESC 
               LIMIT ?""", 
            (limit,)
        )
        opportunities = cursor.fetchall()
        conn.close()
        return opportunities


if __name__ == "__main__":
    setup_database()
