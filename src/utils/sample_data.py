"""
Sample data for testing Proposal AI
"""
from ..core.database import DatabaseManager


def create_sample_data():
    """Create sample organizations and opportunities for testing"""
    db = DatabaseManager()
    
    print("Creating sample data...")
    
    # Create sample organizations
    nasa_id = db.add_organization(
        name="NASA",
        industry="Space & Aerospace",
        website="https://nasa.gov",
        contact_info="contact@nasa.gov"
    )
    
    esa_id = db.add_organization(
        name="European Space Agency",
        industry="Space & Aerospace", 
        website="https://esa.int",
        contact_info="contact@esa.int"
    )
    
    iac_id = db.add_organization(
        name="International Astronautical Federation",
        industry="Space & Aerospace",
        website="https://iafastro.org",
        contact_info="admin@iafastro.org"
    )
    
    # Create sample events/opportunities
    db.add_event(
        name="NASA Small Business Innovation Research (SBIR) 2025",
        organization_id=nasa_id,
        event_date="2025-09-15",
        deadline="2025-08-01",
        description="NASA SBIR provides funding opportunities for small businesses to engage in research and development that has the potential for commercialization.",
        url="https://sbir.nasa.gov/",
        requirements="Must be a US small business, innovative technology focus"
    )
    
    db.add_event(
        name="International Astronautical Congress 2025 - Call for Papers",
        organization_id=iac_id,
        event_date="2025-10-14",
        deadline="2025-06-30",
        description="The International Astronautical Congress is the world's premier space event, bringing together all space actors to exchange information and ideas.",
        url="https://iafastro.org/events/iac/",
        requirements="Original research, peer review process"
    )
    
    db.add_event(
        name="ESA Business Applications Call for Proposals",
        organization_id=esa_id,
        event_date="2025-12-01",
        deadline="2025-09-15",
        description="ESA seeks innovative business applications utilizing space technologies and data.",
        url="https://business.esa.int/",
        requirements="European entities, commercial viability demonstration"
    )
    
    db.add_event(
        name="NASA Technology Transfer Opportunities",
        organization_id=nasa_id,
        deadline="2025-12-31",
        description="Ongoing opportunities to license NASA technologies for commercial applications.",
        url="https://technology.nasa.gov/",
        requirements="Technology licensing agreement"
    )
    
    print("✅ Sample data created successfully!")


if __name__ == "__main__":
    create_sample_data()
