"""
Real-time Opportunity Monitoring System
Tracks new opportunities and sends alerts based on user preferences
"""

import json
import logging
import sqlite3
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set

import schedule

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OpportunityMonitor:
    """Real-time monitoring system for new opportunities"""
    
    def __init__(self, db_path: str = "opportunities.db"):
        self.db_path = db_path
        self.monitoring_active = False
        self.known_opportunities: Set[str] = set()
        self.alert_callbacks = []
        
        # Load existing opportunities to avoid duplicates
        self._load_existing_opportunities()
        
    def _load_existing_opportunities(self):
        """Load existing opportunity IDs to avoid duplicate alerts"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT id FROM opportunities")
            self.known_opportunities = {row[0] for row in cursor.fetchall()}
            
            conn.close()
            logger.info(f"Loaded {len(self.known_opportunities)} existing opportunities")
            
        except Exception as e:
            logger.warning(f"Could not load existing opportunities: {e}")
            self.known_opportunities = set()
    
    def add_alert_callback(self, callback):
        """Add a callback function to be called when new opportunities are found"""
        self.alert_callbacks.append(callback)
    
    def check_for_new_opportunities(self):
        """Check all sources for new opportunities"""
        logger.info("Checking for new opportunities...")
        
        try:
            # Import here to avoid circular imports
            from api_integrations import APIIntegrationManager
            from enhanced_discovery_engine import EnhancedOpportunityDiscoverer
            
            discoverer = EnhancedOpportunityDiscoverer()
            api_manager = APIIntegrationManager()
            
            new_opportunities = []
            
            # Check API sources
            try:
                grants_gov_opps = api_manager.search_grants_gov(['AI', 'space', 'research'])
                for opp in grants_gov_opps:
                    if opp['id'] not in self.known_opportunities:
                        new_opportunities.append(opp)
                        self.known_opportunities.add(opp['id'])
            except Exception as e:
                logger.warning(f"Grants.gov check failed: {e}")
            
            try:
                nasa_opps = api_manager.search_nasa_nspires(['technology', 'innovation'])
                for opp in nasa_opps:
                    if opp['id'] not in self.known_opportunities:
                        new_opportunities.append(opp)
                        self.known_opportunities.add(opp['id'])
            except Exception as e:
                logger.warning(f"NASA check failed: {e}")
            
            # Save new opportunities to database
            if new_opportunities:
                self._save_new_opportunities(new_opportunities)
                self._send_alerts(new_opportunities)
                logger.info(f"Found {len(new_opportunities)} new opportunities")
            else:
                logger.info("No new opportunities found")
                
        except Exception as e:
            logger.error(f"Error checking for opportunities: {e}")
    
    def _save_new_opportunities(self, opportunities: List[Dict]):
        """Save new opportunities to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS opportunities (
                    id TEXT PRIMARY KEY,
                    title TEXT,
                    description TEXT,
                    organization TEXT,
                    deadline TEXT,
                    funding_amount TEXT,
                    url TEXT,
                    source TEXT,
                    category TEXT,
                    keywords TEXT,
                    discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            for opp in opportunities:
                cursor.execute("""
                    INSERT OR REPLACE INTO opportunities 
                    (id, title, description, organization, deadline, funding_amount, 
                     url, source, category, keywords)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    opp.get('id', ''),
                    opp.get('title', ''),
                    opp.get('description', ''),
                    opp.get('organization', ''),
                    opp.get('deadline', ''),
                    opp.get('funding_amount', ''),
                    opp.get('url', ''),
                    opp.get('source', ''),
                    opp.get('category', ''),
                    ','.join(opp.get('keywords', []))
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error saving opportunities: {e}")
    
    def _send_alerts(self, opportunities: List[Dict]):
        """Send alerts for new opportunities"""
        for callback in self.alert_callbacks:
            try:
                callback(opportunities)
            except Exception as e:
                logger.error(f"Alert callback failed: {e}")
    
    def start_monitoring(self, check_interval_minutes: int = 60):
        """Start the monitoring system"""
        if self.monitoring_active:
            logger.warning("Monitoring is already active")
            return
        
        self.monitoring_active = True
        logger.info(f"Starting monitoring with {check_interval_minutes} minute intervals")
        
        # Schedule periodic checks
        schedule.every(check_interval_minutes).minutes.do(self.check_for_new_opportunities)
        
        # Run initial check
        self.check_for_new_opportunities()
        
        # Start scheduler in background thread
        def run_scheduler():
            while self.monitoring_active:
                schedule.run_pending()
                time.sleep(60)  # Check every minute for scheduled tasks
        
        self.monitor_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.monitor_thread.start()
        
        logger.info("Monitoring system started successfully")
    
    def stop_monitoring(self):
        """Stop the monitoring system"""
        self.monitoring_active = False
        schedule.clear()
        logger.info("Monitoring system stopped")
    
    def get_recent_opportunities(self, days: int = 7) -> List[Dict]:
        """Get opportunities discovered in the last N days"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
            cursor.execute("""
                SELECT * FROM opportunities 
                WHERE discovered_at > ? 
                ORDER BY discovered_at DESC
            """, (cutoff_date.isoformat(),))
            
            columns = [desc[0] for desc in cursor.description]
            opportunities = []
            
            for row in cursor.fetchall():
                opp = dict(zip(columns, row))
                opp['keywords'] = opp['keywords'].split(',') if opp['keywords'] else []
                opportunities.append(opp)
            
            conn.close()
            return opportunities
            
        except Exception as e:
            logger.error(f"Error retrieving recent opportunities: {e}")
            return []
    
    def check_deadline_alerts(self, days_ahead: int = 7) -> List[Dict]:
        """Check for opportunities with approaching deadlines"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM opportunities WHERE deadline != ''")
            
            approaching_deadlines = []
            
            for row in cursor.fetchall():
                # Simple deadline parsing (can be enhanced)
                deadline_str = row[4]  # deadline column
                
                # Look for date patterns and alert if within range
                # This is a simplified version - real implementation would parse dates properly
                if any(word in deadline_str.lower() for word in ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']):
                    opportunity = {
                        'id': row[0],
                        'title': row[1],
                        'deadline': deadline_str,
                        'organization': row[3],
                        'url': row[6]
                    }
                    approaching_deadlines.append(opportunity)
            
            conn.close()
            return approaching_deadlines
            
        except Exception as e:
            logger.error(f"Error checking deadlines: {e}")
            return []


class AlertManager:
    """Manages different types of alerts and notifications"""
    
    def __init__(self):
        self.alert_preferences = {
            'new_opportunities': True,
            'deadline_warnings': True,
            'keyword_matches': True,
            'email_alerts': False,  # Would need email configuration
            'desktop_notifications': True
        }
        
        # Keywords to watch for
        self.watch_keywords = [
            'artificial intelligence', 'AI', 'machine learning',
            'space technology', 'aerospace', 'satellite',
            'research', 'innovation', 'SBIR', 'STTR'
        ]
    
    def new_opportunity_alert(self, opportunities: List[Dict]):
        """Handle alerts for new opportunities"""
        if not self.alert_preferences['new_opportunities']:
            return
        
        print("\n🚨 NEW OPPORTUNITIES ALERT! 🚨")
        print("=" * 50)
        
        for opp in opportunities:
            print(f"📋 {opp.get('title', 'Unknown Title')}")
            print(f"🏢 {opp.get('organization', 'Unknown Org')}")
            print(f"💰 {opp.get('funding_amount', 'Amount TBD')}")
            print(f"⏰ Deadline: {opp.get('deadline', 'See announcement')}")
            print(f"🔗 {opp.get('url', 'No URL')}")
            print("-" * 30)
        
        print(f"Total new opportunities: {len(opportunities)}")
        print("=" * 50)
    
    def deadline_warning_alert(self, opportunities: List[Dict]):
        """Handle alerts for approaching deadlines"""
        if not self.alert_preferences['deadline_warnings']:
            return
        
        if opportunities:
            print("\n⚠️ DEADLINE WARNING! ⚠️")
            print("=" * 40)
            
            for opp in opportunities:
                print(f"📋 {opp.get('title', 'Unknown Title')}")
                print(f"⏰ Deadline: {opp.get('deadline', 'TBD')}")
                print(f"🏢 {opp.get('organization', 'Unknown')}")
                print("-" * 20)
    
    def keyword_match_alert(self, opportunities: List[Dict]):
        """Handle alerts for keyword matches"""
        if not self.alert_preferences['keyword_matches']:
            return
        
        matched_opportunities = []
        
        for opp in opportunities:
            title_desc = f"{opp.get('title', '')} {opp.get('description', '')}".lower()
            
            matched_keywords = [kw for kw in self.watch_keywords if kw.lower() in title_desc]
            
            if matched_keywords:
                opp['matched_keywords'] = matched_keywords
                matched_opportunities.append(opp)
        
        if matched_opportunities:
            print("\n🎯 KEYWORD MATCH ALERT! 🎯")
            print("=" * 40)
            
            for opp in matched_opportunities:
                print(f"📋 {opp.get('title', 'Unknown Title')}")
                print(f"🎯 Keywords: {', '.join(opp['matched_keywords'])}")
                print(f"🏢 {opp.get('organization', 'Unknown')}")
                print("-" * 20)


def create_sample_monitoring_config():
    """Create a sample monitoring configuration"""
    config = {
        'monitoring': {
            'enabled': True,
            'check_interval_minutes': 60,
            'sources': [
                {'name': 'grants_gov', 'enabled': True, 'keywords': ['AI', 'space', 'research']},
                {'name': 'nasa_nspires', 'enabled': True, 'keywords': ['technology', 'innovation']},
                {'name': 'nsf_funding', 'enabled': True, 'keywords': ['science', 'research']},
                {'name': 'esa_opportunities', 'enabled': False, 'keywords': ['space', 'satellite']}
            ]
        },
        'alerts': {
            'new_opportunities': True,
            'deadline_warnings': {'enabled': True, 'days_ahead': 7},
            'keyword_matches': {
                'enabled': True,
                'keywords': [
                    'artificial intelligence', 'machine learning', 'AI',
                    'space technology', 'aerospace', 'satellite',
                    'research', 'innovation', 'SBIR', 'STTR'
                ]
            }
        },
        'notifications': {
            'email': {'enabled': False, 'address': 'user@example.com'},
            'desktop': {'enabled': True},
            'dashboard': {'enabled': True}
        }
    }
    
    with open('monitoring_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    return config


if __name__ == "__main__":
    # Demo the monitoring system
    print("🔍 Proposal AI - Monitoring System Demo")
    print("=" * 50)
    
    # Create configuration
    config = create_sample_monitoring_config()
    print("✅ Monitoring configuration created")
    
    # Initialize monitoring system
    monitor = OpportunityMonitor()
    alert_manager = AlertManager()
    
    # Add alert callback
    monitor.add_alert_callback(alert_manager.new_opportunity_alert)
    
    # Run a single check
    print("🔄 Running opportunity check...")
    monitor.check_for_new_opportunities()
    
    # Check for recent opportunities
    recent = monitor.get_recent_opportunities(days=30)
    print(f"📊 Found {len(recent)} opportunities in the last 30 days")
    
    # Check deadline alerts
    deadline_alerts = monitor.check_deadline_alerts(days=14)
    if deadline_alerts:
        alert_manager.deadline_warning_alert(deadline_alerts)
    
    print("\n✅ Monitoring system demo completed!")
    print("💡 To start continuous monitoring, call monitor.start_monitoring()")
