"""
Phase 2: Opportunity Discovery Engine
- Web scraping using Scrapy
- NLP using spaCy (or HuggingFace)
- Database integration
- PyQt GUI for opportunity search
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse

import scrapy

from database import DatabaseManager


class OpportunitySpider(scrapy.Spider):
    """Main spider for discovering proposal opportunities"""
    name = "opportunity_spider"
    
    def __init__(self, *args, **kwargs):
        super(OpportunitySpider, self).__init__(*args, **kwargs)
        self.db_manager = DatabaseManager()
        
        # Define target websites and their patterns
        self.start_urls = [
            'https://www.iafastro.org/',  # IAC
            'https://sbir.nasa.gov/',     # NASA SBIR
            'https://www.esa.int/Applications/Telecommunications_Integrated_Applications',  # ESA
            'https://grants.gov/',        # US Government grants
        ]
        
        # Keywords to identify opportunities
        self.opportunity_keywords = [
            'call for papers', 'call for proposals', 'cfp', 'rfp', 
            'competition', 'grant', 'funding', 'submission', 'deadline',
            'application', 'solicitation', 'innovation', 'research'
        ]
    
    def parse(self, response):
        """Parse main pages and find opportunity links"""
        # Extract all links that might lead to opportunities
        opportunity_links = self._find_opportunity_links(response)
        
        for link in opportunity_links:
            yield response.follow(link, self.parse_opportunity)
        
        # Follow pagination if available
        next_page = response.css('a.next::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)
    
    def parse_opportunity(self, response):
        """Parse individual opportunity pages"""
        # Extract opportunity data
        title = self._extract_title(response)
        description = self._extract_description(response)
        deadline = self._extract_deadline(response)
        requirements = self._extract_requirements(response)
        organization = self._extract_organization(response)
        
        if title:  # Only process if we have a title
            opportunity_data = {
                'source_url': response.url,
                'title': title,
                'description': description,
                'deadline': deadline,
                'requirements': requirements,
                'organization': organization,
                'keywords': ', '.join(self._extract_keywords(response.text)),
                'raw_data': json.dumps({
                    'html_title': response.css('title::text').get(),
                    'meta_description': response.css('meta[name="description"]::attr(content)').get(),
                    'extracted_at': datetime.now().isoformat()
                })
            }
            
            # Save to database
            self.db_manager.add_scraped_opportunity(**opportunity_data)
            
            yield opportunity_data
    
    def _find_opportunity_links(self, response) -> List[str]:
        """Find links that likely lead to opportunities"""
        links = []
        
        # Look for links with opportunity-related text
        for keyword in self.opportunity_keywords:
            # CSS selectors for links containing keywords
            keyword_links = response.css(f'a:contains("{keyword}")::attr(href)').getall()
            links.extend(keyword_links)
            
            # Also check href attributes
            href_links = response.css(f'a[href*="{keyword}"]::attr(href)').getall()
            links.extend(href_links)
        
        # Clean and absolute URLs
        clean_links = []
        for link in links:
            if link:
                absolute_url = urljoin(response.url, link)
                if self._is_valid_opportunity_url(absolute_url):
                    clean_links.append(absolute_url)
        
        return list(set(clean_links))  # Remove duplicates
    
    def _is_valid_opportunity_url(self, url: str) -> bool:
        """Check if URL is likely an opportunity page"""
        parsed = urlparse(url)
        
        # Skip certain file types and external domains
        skip_extensions = ['.pdf', '.doc', '.docx', '.jpg', '.png']
        if any(url.lower().endswith(ext) for ext in skip_extensions):
            return False
        
        # Check if URL contains opportunity-related terms
        url_lower = url.lower()
        return any(keyword in url_lower for keyword in self.opportunity_keywords)
    
    def _extract_title(self, response) -> Optional[str]:
        """Extract opportunity title"""
        # Try multiple selectors
        selectors = [
            'h1::text',
            'h2::text',
            '.title::text',
            '#title::text',
            'title::text'
        ]
        
        for selector in selectors:
            title = response.css(selector).get()
            if title:
                return title.strip()
        
        return None
    
    def _extract_description(self, response) -> Optional[str]:
        """Extract opportunity description"""
        # Try to find description in various places
        description_selectors = [
            '.description *::text',
            '.content *::text',
            '.summary *::text',
            'meta[name="description"]::attr(content)',
            'p::text'
        ]
        
        for selector in description_selectors:
            desc_parts = response.css(selector).getall()
            if desc_parts:
                description = ' '.join(desc_parts).strip()
                if len(description) > 50:  # Ensure substantial content
                    return description[:2000]  # Limit length
        
        return None
    
    def _extract_deadline(self, response) -> Optional[str]:
        """Extract submission deadline"""
        text = response.text.lower()
        
        # Look for deadline patterns
        deadline_patterns = [
            r'deadline[:\s]+([^.]+)',
            r'due[:\s]+([^.]+)',
            r'submit by[:\s]+([^.]+)',
            r'closing date[:\s]+([^.]+)'
        ]
        
        for pattern in deadline_patterns:
            match = re.search(pattern, text)
            if match:
                deadline_text = match.group(1).strip()
                # Try to extract actual date
                date_match = re.search(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}-\d{2}-\d{2}', deadline_text)
                if date_match:
                    return date_match.group(0)
                return deadline_text[:100]  # Return first part if no date found
        
        return None
    
    def _extract_requirements(self, response) -> Optional[str]:
        """Extract submission requirements"""
        # Look for requirements sections
        requirements_selectors = [
            '*:contains("requirements") + *::text',
            '*:contains("eligibility") + *::text',
            '*:contains("criteria") + *::text'
        ]
        
        for selector in requirements_selectors:
            req_parts = response.css(selector).getall()
            if req_parts:
                requirements = ' '.join(req_parts).strip()
                if len(requirements) > 20:
                    return requirements[:1000]  # Limit length
        
        return None
    
    def _extract_organization(self, response) -> Optional[str]:
        """Extract organizing organization"""
        # Try to identify organization from URL or content
        domain = urlparse(response.url).netloc
        
        # Common organization mappings
        org_mappings = {
            'nasa.gov': 'NASA',
            'esa.int': 'European Space Agency',
            'iafastro.org': 'International Astronautical Federation',
            'grants.gov': 'US Government',
            'nsf.gov': 'National Science Foundation'
        }
        
        for domain_part, org_name in org_mappings.items():
            if domain_part in domain:
                return org_name
        
        # Try to extract from page content
        org_selectors = [
            '.organization::text',
            '.sponsor::text',
            '.organizer::text'
        ]
        
        for selector in org_selectors:
            org = response.css(selector).get()
            if org:
                return org.strip()
        
        return domain  # Fallback to domain
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract relevant keywords from text"""
        text_lower = text.lower()
        found_keywords = []
        
        # Extended keyword list for categorization
        all_keywords = [
            'space', 'aerospace', 'satellite', 'rocket', 'mission',
            'research', 'innovation', 'technology', 'engineering',
            'science', 'funding', 'grant', 'competition', 'award',
            'proposal', 'application', 'submission', 'deadline'
        ]
        
        for keyword in all_keywords:
            if keyword in text_lower:
                found_keywords.append(keyword)
        
        return found_keywords


class OpportunityProcessor:
    """Process and analyze scraped opportunities"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
    
    def process_unprocessed_opportunities(self):
        """Process all unprocessed scraped opportunities"""
        opportunities = self.db_manager.get_unprocessed_opportunities()
        
        for opp in opportunities:
            self._process_single_opportunity(opp)
    
    def _process_single_opportunity(self, opportunity):
        """Process a single opportunity and add to events table"""
        # Convert scraped data to event format
        try:
            # Extract organization or create new one
            org_id = self._get_or_create_organization(opportunity[9])  # organization field
            
            # Add to events table
            event_id = self.db_manager.add_event(
                name=opportunity[2],  # title
                organization_id=org_id,
                description=opportunity[3],  # description
                deadline=opportunity[4],  # deadline
                url=opportunity[1],  # source_url
                requirements=opportunity[10] if len(opportunity) > 10 else None
            )
            
            # Mark as processed
            # Update processed flag in scraped_opportunities table
            
            return event_id
            
        except Exception as e:
            print(f"Error processing opportunity {opportunity[0]}: {e}")
            return None
    
    def _get_or_create_organization(self, org_name: str) -> int:
        """Get existing organization or create new one"""
        if not org_name:
            org_name = "Unknown"
        
        # For now, always create new - in real implementation, check for existing
        return self.db_manager.add_organization(
            name=org_name,
            industry="Various"
        )


if __name__ == "__main__":
    # Test the spider
    from scrapy.crawler import CrawlerProcess
    
    process = CrawlerProcess({
        'USER_AGENT': 'Proposal-AI-Bot (+http://www.yourdomain.com)'
    })
    
    process.crawl(OpportunitySpider)
    process.start()
