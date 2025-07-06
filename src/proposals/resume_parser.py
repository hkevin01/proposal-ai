"""
Resume/Profile Parser and Manager for Proposal AI
- Parse resumes from various formats (PDF, Word, text)
- Extract key skills, experience, education
- Store and manage user profiles
- Match profiles to opportunities
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import PyPDF2
import spacy
from docx import Document

from ..core.database import DatabaseManager


class ResumeParser:
    """Parse and extract information from resumes"""
    
    def __init__(self):
        self.nlp = spacy.load('en_core_web_sm')
        self.db_manager = DatabaseManager()
        
        # Common section headers in resumes
        self.section_patterns = {
            'education': [
                r'education', r'academic background', r'academic qualifications',
                r'degrees', r'university', r'college', r'school'
            ],
            'experience': [
                r'experience', r'work experience', r'employment', r'career',
                r'professional experience', r'work history', r'positions'
            ],
            'skills': [
                r'skills', r'technical skills', r'core competencies',
                r'expertise', r'technologies', r'programming languages'
            ],
            'research': [
                r'research', r'research experience', r'research interests',
                r'publications', r'papers', r'projects'
            ],
            'publications': [
                r'publications', r'papers', r'articles', r'journals',
                r'conferences', r'proceedings'
            ]
        }
        
        # Technology and skill keywords
        self.tech_keywords = {
            'programming': [
                'python', 'java', 'c++', 'javascript', 'matlab', 'r',
                'sql', 'html', 'css', 'php', 'ruby', 'go', 'rust', 'scala'
            ],
            'ai_ml': [
                'machine learning', 'artificial intelligence', 'deep learning',
                'neural networks', 'tensorflow', 'pytorch', 'scikit-learn',
                'computer vision', 'nlp', 'natural language processing'
            ],
            'data_science': [
                'data science', 'data analysis', 'statistics', 'big data',
                'pandas', 'numpy', 'matplotlib', 'data visualization'
            ],
            'space_tech': [
                'satellite', 'spacecraft', 'orbital mechanics', 'mission planning',
                'space systems', 'aerospace', 'rocket', 'propulsion'
            ],
            'engineering': [
                'mechanical engineering', 'electrical engineering', 
                'software engineering', 'systems engineering', 'design'
            ],
            'tools': [
                'git', 'docker', 'kubernetes', 'aws', 'azure', 'linux',
                'windows', 'macos', 'autocad', 'solidworks'
            ]
        }
        
        # Education level keywords
        self.education_levels = [
            'phd', 'ph.d', 'doctorate', 'doctoral',
            'masters', 'master', 'ms', 'm.s', 'msc', 'm.sc',
            'bachelors', 'bachelor', 'bs', 'b.s', 'ba', 'b.a',
            'associate', 'diploma', 'certificate'
        ]

    def parse_resume_file(self, file_path: str) -> Dict:
        """Parse resume from file (PDF, Word, or text)"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Resume file not found: {file_path}")
        
        # Extract text based on file type
        if file_path.suffix.lower() == '.pdf':
            text = self._extract_pdf_text(file_path)
        elif file_path.suffix.lower() in ['.docx', '.doc']:
            text = self._extract_word_text(file_path)
        elif file_path.suffix.lower() == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
        
        # Parse the extracted text
        return self.parse_resume_text(text, str(file_path))

    def _extract_pdf_text(self, file_path: Path) -> str:
        """Extract text from PDF file"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\\n"
        except Exception as e:
            raise ValueError(f"Error reading PDF: {e}")
        return text

    def _extract_word_text(self, file_path: Path) -> str:
        """Extract text from Word document"""
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\\n"
            return text
        except Exception as e:
            raise ValueError(f"Error reading Word document: {e}")

    def parse_resume_text(self, text: str, file_path: Optional[str] = None) -> Dict:
        """Parse resume text and extract structured information"""
        # Clean the text
        text = self._clean_text(text)
        
        # Extract sections
        sections = self._extract_sections(text)
        
        # Extract specific information
        profile_data = {
            'resume_text': text,
            'file_path': file_path,
            'skills': self._extract_skills(text, sections),
            'experience': self._extract_experience(text, sections),
            'education': self._extract_education(text, sections),
            'research_interests': self._extract_research_interests(text, sections),
            'publications': self._extract_publications(text, sections),
            'technologies': self._extract_technologies(text),
            'expertise': self._extract_expertise(text),
            'keywords': self._extract_keywords(text),
            'contact_info': self._extract_contact_info(text),
            'specialization': self._determine_specialization(text),
            'industry': self._determine_industry(text)
        }
        
        return profile_data

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\\s+', ' ', text)
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\\w\\s\\.,;:()-]', '', text)
        return text.strip()

    def _extract_sections(self, text: str) -> Dict[str, str]:
        """Extract different sections from resume text"""
        sections = {}
        text_lower = text.lower()
        
        for section_name, patterns in self.section_patterns.items():
            section_text = ""
            
            for pattern in patterns:
                # Find section start
                match = re.search(rf'\\b{pattern}\\b', text_lower)
                if match:
                    start_pos = match.start()
                    
                    # Find section end (next section or end of document)
                    end_pos = len(text)
                    for next_pattern in [p for sublist in self.section_patterns.values() 
                                       for p in sublist if p != pattern]:
                        next_match = re.search(rf'\\b{next_pattern}\\b', 
                                             text_lower[start_pos + 50:])
                        if next_match:
                            potential_end = start_pos + 50 + next_match.start()
                            if potential_end < end_pos:
                                end_pos = potential_end
                    
                    section_text = text[start_pos:end_pos]
                    break
            
            if section_text:
                sections[section_name] = section_text
        
        return sections

    def _extract_skills(self, text: str, sections: Dict[str, str]) -> str:
        """Extract skills from resume"""
        skills = set()
        
        # Look in skills section first
        skills_text = sections.get('skills', '')
        if skills_text:
            skills.update(self._find_skill_keywords(skills_text))
        
        # Also look in full text
        skills.update(self._find_skill_keywords(text))
        
        return ', '.join(sorted(skills))

    def _find_skill_keywords(self, text: str) -> List[str]:
        """Find skill keywords in text"""
        text_lower = text.lower()
        found_skills = []
        
        for category, keywords in self.tech_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    found_skills.append(keyword)
        
        return found_skills

    def _extract_experience(self, text: str, sections: Dict[str, str]) -> str:
        """Extract work experience"""
        exp_section = sections.get('experience', '')
        if exp_section:
            # Clean up and return first 1000 chars
            return exp_section[:1000].strip()
        
        # Fallback: look for experience indicators
        experience_indicators = [
            r'worked at', r'employed by', r'position', r'role',
            r'\\d+ years? of experience', r'\\d+-\\d+ years?'
        ]
        
        for indicator in experience_indicators:
            matches = re.findall(rf'.{{0,100}}{indicator}.{{0,100}}', 
                               text, re.IGNORECASE)
            if matches:
                return ' '.join(matches[:3])
        
        return ""

    def _extract_education(self, text: str, sections: Dict[str, str]) -> str:
        """Extract education information"""
        edu_section = sections.get('education', '')
        if edu_section:
            return edu_section[:1000].strip()
        
        # Look for education keywords
        education_found = []
        text_lower = text.lower()
        
        for level in self.education_levels:
            if level in text_lower:
                # Find context around education level
                pattern = rf'.{{0,50}}\\b{level}\\b.{{0,100}}'
                matches = re.findall(pattern, text, re.IGNORECASE)
                education_found.extend(matches)
        
        return ' '.join(education_found[:3]) if education_found else ""

    def _extract_research_interests(self, text: str, sections: Dict[str, str]) -> str:
        """Extract research interests"""
        research_section = sections.get('research', '')
        if research_section:
            return research_section[:1000].strip()
        
        # Look for research keywords
        research_patterns = [
            r'research interests?[:\\s]+([^.]+)',
            r'research focus[:\\s]+([^.]+)',
            r'research areas?[:\\s]+([^.]+)'
        ]
        
        for pattern in research_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)[:500]
        
        return ""

    def _extract_publications(self, text: str, sections: Dict[str, str]) -> str:
        """Extract publications"""
        pub_section = sections.get('publications', '')
        if pub_section:
            return pub_section[:1000].strip()
        
        # Look for publication patterns
        pub_patterns = [
            r'"[^"]+",?\\s*\\d{4}',  # "Title", Year
            r'[A-Z][^.]+\\.\\s*\\d{4}',  # Title. Year
        ]
        
        publications = []
        for pattern in pub_patterns:
            matches = re.findall(pattern, text)
            publications.extend(matches[:5])
        
        return ' | '.join(publications) if publications else ""

    def _extract_technologies(self, text: str) -> str:
        """Extract technology mentions"""
        technologies = set()
        text_lower = text.lower()
        
        for tech_list in self.tech_keywords.values():
            for tech in tech_list:
                if tech in text_lower:
                    technologies.add(tech)
        
        return ', '.join(sorted(technologies))

    def _extract_expertise(self, text: str) -> str:
        """Extract areas of expertise"""
        # Use NLP to find key noun phrases that might indicate expertise
        doc = self.nlp(text)
        
        expertise_phrases = []
        for chunk in doc.noun_chunks:
            chunk_text = chunk.text.lower()
            # Filter for relevant expertise phrases
            if (len(chunk_text.split()) <= 4 and 
                any(word in chunk_text for word in 
                   ['engineering', 'science', 'technology', 'development',
                    'analysis', 'research', 'design', 'management'])):
                expertise_phrases.append(chunk.text)
        
        return ', '.join(expertise_phrases[:10])

    def _extract_keywords(self, text: str) -> str:
        """Extract important keywords using NLP"""
        doc = self.nlp(text)
        
        keywords = set()
        
        # Extract named entities
        for ent in doc.ents:
            if ent.label_ in ['ORG', 'PRODUCT', 'WORK_OF_ART', 'EVENT']:
                keywords.add(ent.text.lower())
        
        # Extract key terms from noun phrases
        for chunk in doc.noun_chunks:
            if len(chunk.text.split()) <= 3:
                keywords.add(chunk.text.lower())
        
        return ', '.join(list(keywords)[:20])

    def _extract_contact_info(self, text: str) -> str:
        """Extract contact information"""
        contact_info = {}
        
        # Email pattern
        email_pattern = r'\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b'
        emails = re.findall(email_pattern, text)
        if emails:
            contact_info['email'] = emails[0]
        
        # Phone pattern
        phone_pattern = r'\\b(?:\\+?1[-\\s]?)?\\(?\\d{3}\\)?[-\\s]?\\d{3}[-\\s]?\\d{4}\\b'
        phones = re.findall(phone_pattern, text)
        if phones:
            contact_info['phone'] = phones[0]
        
        return json.dumps(contact_info) if contact_info else ""

    def _determine_specialization(self, text: str) -> str:
        """Determine primary specialization"""
        text_lower = text.lower()
        
        specializations = {
            'ai_ml': ['machine learning', 'artificial intelligence', 'data science'],
            'space_technology': ['space', 'satellite', 'aerospace', 'orbital'],
            'software_engineering': ['software', 'programming', 'development'],
            'research': ['research', 'phd', 'publications', 'academic'],
            'engineering': ['engineering', 'technical', 'systems'],
            'management': ['management', 'project', 'team', 'leadership']
        }
        
        scores = {}
        for spec, keywords in specializations.items():
            scores[spec] = sum(1 for keyword in keywords if keyword in text_lower)
        
        if scores:
            return max(scores, key=scores.get)
        return "general"

    def _determine_industry(self, text: str) -> str:
        """Determine primary industry"""
        text_lower = text.lower()
        
        industries = {
            'aerospace': ['aerospace', 'space', 'satellite', 'rocket', 'nasa', 'esa'],
            'technology': ['software', 'tech', 'computer', 'programming'],
            'academia': ['university', 'research', 'academic', 'professor'],
            'defense': ['defense', 'military', 'security', 'government'],
            'healthcare': ['medical', 'healthcare', 'biotech', 'pharmaceutical'],
            'finance': ['finance', 'banking', 'investment', 'financial']
        }
        
        scores = {}
        for industry, keywords in industries.items():
            scores[industry] = sum(1 for keyword in keywords if keyword in text_lower)
        
        if scores:
            return max(scores, key=scores.get)
        return "other"

    def save_profile_to_database(self, user_id: int, profile_data: Dict) -> int:
        """Save parsed profile to database"""
        return self.db_manager.add_user_profile(
            user_id=user_id,
            resume_text=profile_data.get('resume_text'),
            skills=profile_data.get('skills'),
            experience=profile_data.get('experience'),
            education=profile_data.get('education'),
            research_interests=profile_data.get('research_interests'),
            expertise=profile_data.get('expertise'),
            background=profile_data.get('contact_info'),
            keywords=profile_data.get('keywords'),
            specialization=profile_data.get('specialization'),
            industry=profile_data.get('industry'),
            technologies=profile_data.get('technologies'),
            publications=profile_data.get('publications'),
            file_path=profile_data.get('file_path')
        )


class ProfileManager:
    """Manage user profiles and resume data"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.parser = ResumeParser()
        
    def create_profile_folder(self, user_id: int) -> str:
        """Create a folder for storing user profile documents"""
        profile_folder = Path(f"profiles/user_{user_id}")
        profile_folder.mkdir(parents=True, exist_ok=True)
        return str(profile_folder)
    
    def upload_resume(self, user_id: int, file_path: str) -> Dict:
        """Upload and parse a resume file"""
        # Create profile folder
        profile_folder = self.create_profile_folder(user_id)
        
        # Copy file to profile folder
        source_path = Path(file_path)
        destination_path = Path(profile_folder) / source_path.name
        
        import shutil
        shutil.copy2(source_path, destination_path)
        
        # Parse the resume
        profile_data = self.parser.parse_resume_file(str(destination_path))
        
        # Save to database
        profile_id = self.parser.save_profile_to_database(user_id, profile_data)
        
        return {
            'profile_id': profile_id,
            'file_path': str(destination_path),
            'profile_data': profile_data
        }
    
    def get_profile(self, user_id: int) -> Optional[Dict]:
        """Get user profile from database"""
        profile_row = self.db_manager.get_user_profile(user_id)
        if not profile_row:
            return None
        
        # Convert database row to dictionary
        column_names = [
            'id', 'user_id', 'resume_text', 'skills', 'experience',
            'education', 'research_interests', 'expertise', 'background',
            'keywords', 'specialization', 'industry', 'technologies',
            'publications', 'file_path', 'created_at', 'updated_at'
        ]
        
        return dict(zip(column_names, profile_row))
    
    def update_profile_text(self, user_id: int, resume_text: str) -> int:
        """Update profile with manually entered text"""
        profile_data = self.parser.parse_resume_text(resume_text)
        return self.parser.save_profile_to_database(user_id, profile_data)


# Testing function
def test_resume_parser():
    """Test the resume parser"""
    parser = ResumeParser()
    
    # Test with sample text
    sample_resume = """
    John Doe
    john.doe@email.com
    (555) 123-4567
    
    EDUCATION
    PhD in Computer Science, MIT, 2020
    MS in Aerospace Engineering, Stanford, 2017
    
    EXPERIENCE
    Senior AI Researcher at SpaceX (2020-present)
    - Developed machine learning algorithms for satellite data processing
    - Led team of 5 engineers on autonomous navigation systems
    
    Research Scientist at NASA JPL (2017-2020)
    - Worked on Mars rover mission planning using Python and MATLAB
    - Published 12 papers on space robotics
    
    SKILLS
    Programming: Python, C++, MATLAB, JavaScript
    AI/ML: TensorFlow, PyTorch, scikit-learn, computer vision
    Space Technology: Orbital mechanics, mission planning, satellite systems
    
    RESEARCH INTERESTS
    Autonomous space systems, machine learning for space applications,
    robotic exploration, satellite data analysis
    
    PUBLICATIONS
    "Autonomous Navigation for Mars Rovers", Journal of Space Robotics, 2021
    "Machine Learning in Satellite Data Processing", IEEE Aerospace, 2020
    """
    
    profile_data = parser.parse_resume_text(sample_resume)
    
    print("📋 Parsed Resume Profile:")
    for key, value in profile_data.items():
        if value:
            print(f"  {key}: {value[:100]}{'...' if len(str(value)) > 100 else ''}")


if __name__ == "__main__":
    test_resume_parser()
