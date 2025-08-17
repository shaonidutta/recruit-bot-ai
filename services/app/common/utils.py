# services/app/common/utils.py

import re
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

def clean_text(text: str) -> str:
    """
    Clean and normalize text data
    """
    if not text:
        return ""
    
    # Remove extra whitespace and newlines
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s.,!?()-]', '', text)
    
    return text

def extract_salary_info(description: str) -> Optional[Dict[str, Any]]:
    """
    Extract salary information from job description
    """
    if not description:
        return None
    
    # Common salary patterns
    patterns = [
        r'\$([\d,]+)\s*-\s*\$([\d,]+)\s*(?:per\s+year|annually|/year)?',
        r'\$([\d,]+)\s*(?:per\s+year|annually|/year)',
        r'([\d,]+)\s*-\s*([\d,]+)\s*(?:USD|dollars)',
        r'salary.*?\$([\d,]+)',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, description, re.IGNORECASE)
        if matches:
            match = matches[0]
            if isinstance(match, tuple) and len(match) == 2:
                try:
                    min_salary = int(match[0].replace(',', ''))
                    max_salary = int(match[1].replace(',', ''))
                    return {
                        'min': min_salary,
                        'max': max_salary,
                        'currency': 'USD',
                        'period': 'yearly'
                    }
                except ValueError:
                    continue
            elif isinstance(match, str):
                try:
                    salary = int(match.replace(',', ''))
                    return {
                        'min': salary,
                        'max': salary,
                        'currency': 'USD',
                        'period': 'yearly'
                    }
                except ValueError:
                    continue
    
    return None

def parse_experience_level(description: str) -> Optional[str]:
    """
    Extract experience level from job description
    """
    if not description:
        return None
    
    description_lower = description.lower()
    
    # Experience level patterns
    if any(term in description_lower for term in ['entry level', 'junior', '0-2 years', 'new grad']):
        return 'entry'
    elif any(term in description_lower for term in ['mid level', 'intermediate', '3-5 years', '2-5 years']):
        return 'mid'
    elif any(term in description_lower for term in ['senior', 'lead', '5+ years', '7+ years', 'expert']):
        return 'senior'
    elif any(term in description_lower for term in ['principal', 'staff', 'architect', '10+ years']):
        return 'principal'
    
    # Extract years of experience
    year_patterns = [
        r'(\d+)\+?\s*years?\s*(?:of\s+)?experience',
        r'(\d+)\s*-\s*(\d+)\s*years?\s*(?:of\s+)?experience'
    ]
    
    for pattern in year_patterns:
        matches = re.findall(pattern, description_lower)
        if matches:
            match = matches[0]
            if isinstance(match, tuple):
                try:
                    years = int(match[1])  # Take the higher number
                except (ValueError, IndexError):
                    try:
                        years = int(match[0])
                    except (ValueError, IndexError):
                        continue
            else:
                try:
                    years = int(match)
                except ValueError:
                    continue
            
            if years <= 2:
                return 'entry'
            elif years <= 5:
                return 'mid'
            elif years <= 8:
                return 'senior'
            else:
                return 'principal'
    
    return None

def extract_skills_from_text(text: str, skill_database: List[str] = None) -> List[str]:
    """
    Extract technical skills from text using a predefined skill database
    """
    if not text:
        return []
    
    if skill_database is None:
        skill_database = [
            # Programming Languages
            'python', 'javascript', 'java', 'c++', 'c#', 'go', 'rust', 'php', 'ruby', 'swift',
            'kotlin', 'typescript', 'scala', 'r', 'matlab', 'perl', 'shell', 'bash',
            
            # Web Technologies
            'react', 'angular', 'vue.js', 'node.js', 'express', 'django', 'flask', 'spring',
            'html', 'css', 'sass', 'less', 'bootstrap', 'tailwind', 'jquery',
            
            # Databases
            'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'cassandra',
            'oracle', 'sqlite', 'dynamodb', 'neo4j',
            
            # Cloud & DevOps
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'gitlab', 'github',
            'terraform', 'ansible', 'chef', 'puppet', 'vagrant',
            
            # Data & AI
            'machine learning', 'deep learning', 'ai', 'data science', 'pandas', 'numpy',
            'scikit-learn', 'tensorflow', 'pytorch', 'keras', 'spark', 'hadoop',
            
            # Methodologies
            'agile', 'scrum', 'kanban', 'devops', 'ci/cd', 'tdd', 'bdd',
            
            # Tools
            'git', 'jira', 'confluence', 'slack', 'teams', 'figma', 'sketch'
        ]
    
    text_lower = text.lower()
    found_skills = []
    
    for skill in skill_database:
        if skill.lower() in text_lower:
            found_skills.append(skill)
    
    return list(set(found_skills))  # Remove duplicates

def calculate_text_similarity(text1: str, text2: str) -> float:
    """
    Calculate similarity between two texts using simple word overlap
    """
    if not text1 or not text2:
        return 0.0
    
    # Simple word-based similarity
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    if not union:
        return 0.0
    
    return len(intersection) / len(union)

def normalize_location(location: str) -> str:
    """
    Normalize location strings for better matching
    """
    if not location:
        return ""
    
    # Remove common suffixes and normalize
    location = location.strip()
    location = re.sub(r',\s*United States$', '', location, flags=re.IGNORECASE)
    location = re.sub(r',\s*USA$', '', location, flags=re.IGNORECASE)
    location = re.sub(r',\s*US$', '', location, flags=re.IGNORECASE)
    
    # Handle remote work indicators
    if any(term in location.lower() for term in ['remote', 'anywhere', 'work from home']):
        return 'Remote'
    
    return location.title()

def extract_company_size(description: str) -> Optional[str]:
    """
    Extract company size information from job description
    """
    if not description:
        return None
    
    description_lower = description.lower()
    
    size_patterns = {
        'startup': ['startup', 'early stage', 'seed stage'],
        'small': ['small company', '1-50 employees', '10-50 employees'],
        'medium': ['medium company', '50-200 employees', '100-500 employees'],
        'large': ['large company', '500+ employees', '1000+ employees', 'enterprise'],
        'fortune': ['fortune 500', 'fortune 1000', 'multinational']
    }
    
    for size, patterns in size_patterns.items():
        if any(pattern in description_lower for pattern in patterns):
            return size
    
    return None

def format_job_data_for_api(job_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format job data for API responses
    """
    formatted = {
        'id': job_data.get('id'),
        'title': job_data.get('title', ''),
        'company': job_data.get('company', ''),
        'location': normalize_location(job_data.get('location', '')),
        'description': job_data.get('description', ''),
        'skills': job_data.get('skills_required', []),
        'experience_level': job_data.get('experience_level'),
        'salary_range': job_data.get('salary_range'),
        'remote_option': job_data.get('remote_option', False),
        'posted_date': job_data.get('posted_date'),
        'source': job_data.get('source', ''),
        'url': job_data.get('url', '')
    }
    
    return {k: v for k, v in formatted.items() if v is not None}

def validate_email(email: str) -> bool:
    """
    Basic email validation
    """
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def extract_contact_info(text: str) -> Dict[str, Any]:
    """
    Extract contact information from text
    """
    contact_info = {
        'emails': [],
        'phones': [],
        'linkedin_urls': []
    }
    
    # Email pattern
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    contact_info['emails'] = [email for email in emails if validate_email(email)]
    
    # Phone pattern (US format)
    phone_pattern = r'\b(?:\+?1[-.]?)?\(?([0-9]{3})\)?[-.]?([0-9]{3})[-.]?([0-9]{4})\b'
    phones = re.findall(phone_pattern, text)
    contact_info['phones'] = [f"({match[0]}) {match[1]}-{match[2]}" for match in phones]
    
    # LinkedIn URL pattern
    linkedin_pattern = r'https?://(?:www\.)?linkedin\.com/in/[\w-]+/?'
    linkedin_urls = re.findall(linkedin_pattern, text)
    contact_info['linkedin_urls'] = linkedin_urls
    
    return contact_info
