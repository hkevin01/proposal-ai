"""
Database setup and models for Proposal AI
"""
import sqlite3
from typing import Optional

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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
    
    def add_organization(self, name: str, industry: Optional[str] = None, 
                        website: Optional[str] = None, contact_info: Optional[str] = None):
        """Add a new organization"""
        conn = get_connection()
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
        conn = get_connection()
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
        conn = get_connection()
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
                               keywords: Optional[str] = None, raw_data: Optional[str] = None):
        """Add scraped opportunity data"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO scraped_opportunities (source_url, title, description, deadline, category, keywords, raw_data) 
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (source_url, title, description, deadline, category, keywords, raw_data)
        )
        opportunity_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return opportunity_id
    
    def get_unprocessed_opportunities(self):
        """Get unprocessed scraped opportunities"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM scraped_opportunities WHERE processed = FALSE")
        opportunities = cursor.fetchall()
        conn.close()
        return opportunities


if __name__ == "__main__":
    setup_database()
