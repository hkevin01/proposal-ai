# Funding & Partnership Marketplace Stub
class FundingMarketplace:
    def __init__(self):
        self.opportunities = []
        self.partners = []

    def list_opportunities(self):
        """Return available funding opportunities."""
        # Example: Load from a static list or database
        if not self.opportunities:
            self.opportunities = [
                {"name": "IAC Space Competition", "deadline": "2025-09-01"},
                {"name": "NASA SBIR", "deadline": "2025-08-15"}
            ]
        return self.opportunities

    def add_opportunity(self, opportunity):
        self.opportunities.append(opportunity)
        return True

    def list_partners(self):
        """Return available partners."""
        if not self.partners:
            self.partners = [
                {"name": "SpaceX", "type": "Industry"},
                {"name": "ESA", "type": "Agency"}
            ]
        return self.partners

    def add_partner(self, partner):
        self.partners.append(partner)
        return True
