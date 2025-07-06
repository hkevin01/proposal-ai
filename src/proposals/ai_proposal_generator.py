"""
AI-Powered Proposal Generation Module
Using OpenAI GPT and other LLMs to generate proposal drafts
"""
import json
import os
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Tuple

try:
    import openai
except ImportError:
    openai = None

try:
    from transformers import AutoModel, AutoTokenizer, pipeline
except ImportError:
    pipeline = None


@dataclass
class ProposalTemplate:
    """Template structure for proposals"""
    id: str
    name: str
    category: str
    sections: List[str]
    requirements: List[str]
    word_limit: Optional[int] = None
    format_guidelines: Optional[str] = None


@dataclass
class ProposalContext:
    """Context information for proposal generation"""
    opportunity_title: str
    organization: str
    deadline: str
    requirements: str
    description: str
    keywords: List[str]
    user_background: Optional[str] = None
    previous_proposals: Optional[List[str]] = None


class AIProposalGenerator:
    """AI-powered proposal generation engine"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.openai_client = None
        self.local_model = None
        self.templates = self._load_proposal_templates()
        
        # Initialize OpenAI if API key is provided
        if api_key or os.getenv('OPENAI_API_KEY'):
            if openai:
                openai.api_key = api_key or os.getenv('OPENAI_API_KEY')
                self.openai_client = openai
        
        # Initialize local model as fallback
        if pipeline:
            try:
                self.local_model = pipeline(
                    "text-generation", 
                    model="microsoft/DialoGPT-medium",
                    device=-1  # CPU
                )
            except Exception as e:
                print(f"Warning: Could not load local model: {e}")
    
    def _load_proposal_templates(self) -> Dict[str, ProposalTemplate]:
        """Load predefined proposal templates"""
        templates = {
            "research_proposal": ProposalTemplate(
                id="research_proposal",
                name="Research Proposal",
                category="Academic/Research",
                sections=[
                    "Executive Summary",
                    "Problem Statement", 
                    "Literature Review",
                    "Methodology",
                    "Expected Outcomes",
                    "Timeline",
                    "Budget",
                    "Team Qualifications",
                    "References"
                ],
                requirements=[
                    "Clear research objectives",
                    "Novel contribution to field",
                    "Feasible methodology",
                    "Realistic timeline and budget"
                ],
                word_limit=5000
            ),
            "business_proposal": ProposalTemplate(
                id="business_proposal", 
                name="Business/Commercial Proposal",
                category="Business",
                sections=[
                    "Executive Summary",
                    "Company Overview",
                    "Market Analysis",
                    "Solution Description",
                    "Implementation Plan",
                    "Financial Projections",
                    "Risk Assessment",
                    "Team & Qualifications",
                    "Conclusion"
                ],
                requirements=[
                    "Market viability",
                    "Competitive advantage",
                    "Revenue model",
                    "Implementation feasibility"
                ],
                word_limit=3000
            ),
            "grant_application": ProposalTemplate(
                id="grant_application",
                name="Grant Application",
                category="Funding",
                sections=[
                    "Project Summary",
                    "Statement of Need",
                    "Project Description",
                    "Goals and Objectives",
                    "Methodology",
                    "Evaluation Plan",
                    "Budget Narrative",
                    "Organizational Capacity",
                    "Sustainability Plan"
                ],
                requirements=[
                    "Alignment with funder priorities",
                    "Clear measurable outcomes",
                    "Cost-effectiveness",
                    "Community impact"
                ],
                word_limit=4000
            ),
            "conference_abstract": ProposalTemplate(
                id="conference_abstract",
                name="Conference Abstract/Paper",
                category="Academic",
                sections=[
                    "Title",
                    "Abstract",
                    "Introduction",
                    "Methodology/Approach",
                    "Results/Expected Results",
                    "Discussion",
                    "Conclusions",
                    "Keywords"
                ],
                requirements=[
                    "Original research/work",
                    "Conference theme alignment",
                    "Clear contribution",
                    "Peer-review quality"
                ],
                word_limit=1500
            )
        }
        return templates
    
    def suggest_template(self, context: ProposalContext) -> ProposalTemplate:
        """Suggest the best template based on opportunity context"""
        opportunity_lower = context.opportunity_title.lower()
        requirements_lower = context.requirements.lower()
        
        # Keywords for template matching
        template_keywords = {
            "research_proposal": ["research", "study", "investigation", "analysis", "science"],
            "business_proposal": ["business", "commercial", "startup", "innovation", "product"],
            "grant_application": ["grant", "funding", "support", "award", "foundation"],
            "conference_abstract": ["conference", "congress", "symposium", "paper", "abstract", "presentation"]
        }
        
        scores = {}
        for template_id, keywords in template_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in opportunity_lower:
                    score += 2
                if keyword in requirements_lower:
                    score += 1
            scores[template_id] = score
        
        # Return template with highest score
        best_template_id = max(scores, key=scores.get)
        return self.templates[best_template_id]
    
    def generate_proposal_outline(self, context: ProposalContext, 
                                template: Optional[ProposalTemplate] = None) -> Dict[str, str]:
        """Generate a proposal outline based on context and template"""
        if not template:
            template = self.suggest_template(context)
        
        outline = {}
        
        for section in template.sections:
            # Generate section content using AI
            section_content = self._generate_section_content(section, context, template)
            outline[section] = section_content
        
        return outline
    
    def _generate_section_content(self, section: str, context: ProposalContext, 
                                template: ProposalTemplate) -> str:
        """Generate content for a specific section"""
        
        # Create context-specific prompts for each section
        prompts = {
            "Executive Summary": f"""Write an executive summary for a {template.category.lower()} proposal titled "{context.opportunity_title}" 
                for {context.organization}. The proposal should address: {context.description[:200]}...""",
            
            "Problem Statement": f"""Define the problem or need that this proposal addresses for the opportunity: {context.opportunity_title}. 
                Consider the organization's focus: {context.organization} and requirements: {context.requirements[:300]}...""",
            
            "Solution Description": f"""Describe an innovative solution for {context.opportunity_title}. 
                The solution should align with {context.organization}'s goals and address: {context.description[:300]}...""",
            
            "Methodology": f"""Outline a detailed methodology for executing the proposed work for {context.opportunity_title}. 
                Consider the requirements: {context.requirements[:200]}... and ensure feasibility.""",
            
            "Timeline": f"""Create a realistic timeline for completing the work proposed for {context.opportunity_title}. 
                The deadline is {context.deadline}. Break down the work into phases.""",
            
            "Budget": f"""Provide a budget outline for the proposed work on {context.opportunity_title}. 
                Consider typical costs for {template.category.lower()} projects.""",
            
            "Team Qualifications": f"""Describe the team qualifications needed for {context.opportunity_title}. 
                {context.user_background or 'Highlight relevant expertise and experience.'}""",
            
            "Expected Outcomes": f"""Describe the expected outcomes and impact of the proposed work for {context.opportunity_title}. 
                Consider {context.organization}'s objectives."""
        }
        
        # Get prompt for this section or create a generic one
        prompt = prompts.get(section, f"""Write content for the "{section}" section of a proposal for {context.opportunity_title}. 
            Consider the context: {context.description[:200]}... and requirements: {context.requirements[:200]}...""")
        
        # Generate content using available AI model
        if self.openai_client:
            return self._generate_with_openai(prompt)
        elif self.local_model:
            return self._generate_with_local_model(prompt)
        else:
            return self._generate_placeholder_content(section, context)
    
    def _generate_with_openai(self, prompt: str) -> str:
        """Generate content using OpenAI GPT"""
        try:
            response = self.openai_client.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert proposal writer helping create compelling, professional proposals."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"OpenAI generation error: {e}")
            return f"[AI Generation Error: {e}]\n\nPlease provide content for this section manually."
    
    def _generate_with_local_model(self, prompt: str) -> str:
        """Generate content using local model"""
        try:
            result = self.local_model(prompt, max_length=200, num_return_sequences=1)
            return result[0]['generated_text'][len(prompt):].strip()
        except Exception as e:
            print(f"Local model generation error: {e}")
            return f"[Local AI Generation Error: {e}]\n\nPlease provide content for this section manually."
    
    def _generate_placeholder_content(self, section: str, context: ProposalContext) -> str:
        """Generate placeholder content when AI is not available"""
        placeholders = {
            "Executive Summary": f"""[Executive Summary for {context.opportunity_title}]

Please provide a compelling 2-3 paragraph summary that:
- Clearly states the proposal's main objective
- Highlights key benefits to {context.organization}
- Summarizes the approach and expected outcomes
- Demonstrates alignment with opportunity requirements""",

            "Problem Statement": f"""[Problem Statement]

Please describe:
- The specific problem or opportunity being addressed
- Why this problem is important to {context.organization}
- Current gaps or limitations in existing solutions
- The urgency or timeliness of addressing this issue""",

            "Solution Description": f"""[Solution Description]

Please outline:
- Your proposed solution approach
- Key features and innovations
- How it addresses the identified problem
- Unique advantages over alternative approaches""",

            "Methodology": f"""[Methodology]

Please detail:
- Step-by-step approach to executing the work
- Tools, techniques, and methods to be used
- Quality assurance and validation procedures
- Risk mitigation strategies""",

            "Timeline": f"""[Timeline - Deadline: {context.deadline}]

Please provide:
- Major project milestones and deliverables
- Realistic timeframes for each phase
- Dependencies and critical path items
- Buffer time for unexpected delays""",

            "Budget": f"""[Budget]

Please include:
- Personnel costs and time allocation
- Equipment and materials needed
- Travel and other direct costs
- Indirect costs and overhead
- Total project cost breakdown""",

            "Team Qualifications": f"""[Team Qualifications]

Please highlight:
- Key team members and their roles
- Relevant education and experience
- Previous similar projects or achievements
- Organizational capabilities and resources"""
        }
        
        return placeholders.get(section, f"""[{section}]

Please provide content for the {section} section that addresses the requirements for {context.opportunity_title}.

Consider:
- Opportunity requirements: {context.requirements[:200]}...
- Organization focus: {context.organization}
- Deadline: {context.deadline}""")
    
    def improve_content(self, content: str, section: str, context: ProposalContext) -> str:
        """Improve existing content using AI"""
        if not content.strip():
            return content
        
        improvement_prompt = f"""Improve the following {section} content for a proposal to {context.organization}:

Original content:
{content}

Please enhance it by:
- Making it more compelling and professional
- Ensuring alignment with opportunity requirements
- Improving clarity and flow
- Adding specific details where appropriate

Improved content:"""
        
        if self.openai_client:
            return self._generate_with_openai(improvement_prompt)
        elif self.local_model:
            return self._generate_with_local_model(improvement_prompt)
        else:
            return content  # Return original if no AI available
    
    def generate_full_proposal(self, context: ProposalContext, 
                             template: Optional[ProposalTemplate] = None) -> Dict[str, any]:
        """Generate a complete proposal document"""
        if not template:
            template = self.suggest_template(context)
        
        outline = self.generate_proposal_outline(context, template)
        
        # Calculate word count
        total_words = sum(len(content.split()) for content in outline.values())
        
        proposal = {
            "title": context.opportunity_title,
            "organization": context.organization,
            "template_used": template.name,
            "generated_at": datetime.now().isoformat(),
            "sections": outline,
            "word_count": total_words,
            "word_limit": template.word_limit,
            "requirements_met": self._check_requirements(outline, template),
            "suggestions": self._generate_improvement_suggestions(outline, context, template)
        }
        
        return proposal
    
    def _check_requirements(self, outline: Dict[str, str], template: ProposalTemplate) -> List[str]:
        """Check which template requirements are met"""
        met_requirements = []
        content_text = " ".join(outline.values()).lower()
        
        requirement_keywords = {
            "clear research objectives": ["objective", "goal", "aim", "purpose"],
            "market viability": ["market", "demand", "customer", "viable"],
            "alignment with funder priorities": ["align", "priority", "mission", "focus"],
            "original research/work": ["original", "novel", "new", "innovative"],
            "feasible methodology": ["method", "approach", "feasible", "realistic"],
            "cost-effectiveness": ["cost", "budget", "efficient", "value"]
        }
        
        for requirement in template.requirements:
            req_lower = requirement.lower()
            keywords = requirement_keywords.get(req_lower, [req_lower])
            
            if any(keyword in content_text for keyword in keywords):
                met_requirements.append(requirement)
        
        return met_requirements
    
    def _generate_improvement_suggestions(self, outline: Dict[str, str], 
                                        context: ProposalContext, 
                                        template: ProposalTemplate) -> List[str]:
        """Generate suggestions for improving the proposal"""
        suggestions = []
        
        # Check word count
        total_words = sum(len(content.split()) for content in outline.values())
        if template.word_limit and total_words > template.word_limit:
            suggestions.append(f"Reduce content by {total_words - template.word_limit} words to meet limit")
        elif template.word_limit and total_words < template.word_limit * 0.8:
            suggestions.append("Consider expanding content to better utilize word limit")
        
        # Check for missing key elements
        content_text = " ".join(outline.values()).lower()
        
        if "budget" not in content_text and "cost" not in content_text:
            suggestions.append("Consider adding budget or cost information")
        
        if "timeline" not in content_text and "schedule" not in content_text:
            suggestions.append("Include timeline or schedule details")
        
        if context.organization.lower() not in content_text:
            suggestions.append(f"Mention {context.organization} more prominently")
        
        # Check for context keywords
        missing_keywords = []
        for keyword in context.keywords[:3]:  # Check top 3 keywords
            if keyword.lower() not in content_text:
                missing_keywords.append(keyword)
        
        if missing_keywords:
            suggestions.append(f"Consider incorporating keywords: {', '.join(missing_keywords)}")
        
        return suggestions


class ProposalManager:
    """Manager for proposal creation, editing, and storage"""
    
    def __init__(self, db_manager, ai_generator: Optional[AIProposalGenerator] = None):
        self.db_manager = db_manager
        self.ai_generator = ai_generator or AIProposalGenerator()
    
    def create_new_proposal(self, event_id: int, user_id: int, 
                          user_background: Optional[str] = None) -> Dict[str, any]:
        """Create a new proposal for an event"""
        # Get event details from database
        events = self.db_manager.get_events()
        event = next((e for e in events if e[0] == event_id), None)
        
        if not event:
            raise ValueError(f"Event {event_id} not found")
        
        # Create context from event data
        context = ProposalContext(
            opportunity_title=event[1],  # name
            organization=event[10] if len(event) > 10 else "Unknown",  # org_name
            deadline=event[4] or "Not specified",  # deadline
            requirements=event[7] or "No specific requirements listed",  # requirements
            description=event[5] or "No description available",  # description
            keywords=event[6].split(", ") if event[6] else [],  # keywords from URL or other field
            user_background=user_background
        )
        
        # Generate proposal
        proposal = self.ai_generator.generate_full_proposal(context)
        
        # Save to database
        proposal_id = self.save_proposal_to_db(proposal, event_id, user_id)
        proposal["id"] = proposal_id
        
        return proposal
    
    def save_proposal_to_db(self, proposal: Dict[str, any], event_id: int, user_id: int) -> int:
        """Save proposal to database"""
        # Convert proposal to JSON for storage
        proposal_data = {
            "sections": proposal["sections"],
            "template_used": proposal["template_used"],
            "word_count": proposal["word_count"],
            "requirements_met": proposal["requirements_met"],
            "suggestions": proposal["suggestions"]
        }
        
        # Note: This would need to be implemented in the DatabaseManager
        # For now, return a mock ID
        return 1
    
    def get_proposal_templates(self) -> List[ProposalTemplate]:
        """Get all available proposal templates"""
        return list(self.ai_generator.templates.values())


if __name__ == "__main__":
    # Test the AI proposal generator
    generator = AIProposalGenerator()
    
    # Test context
    context = ProposalContext(
        opportunity_title="NASA Small Business Innovation Research 2025",
        organization="NASA",
        deadline="2025-08-01",
        requirements="Small business, innovative technology, space applications",
        description="NASA SBIR funding for innovative space technologies",
        keywords=["space", "innovation", "technology", "NASA"]
    )
    
    # Generate proposal
    proposal = generator.generate_full_proposal(context)
    
    print("Generated Proposal:")
    print(f"Title: {proposal['title']}")
    print(f"Template: {proposal['template_used']}")
    print(f"Word Count: {proposal['word_count']}")
    print("\nSections:")
    for section, content in proposal['sections'].items():
        print(f"\n{section}:")
        print(content[:200] + "..." if len(content) > 200 else content)
