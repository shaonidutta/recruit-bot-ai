import re
import spacy
import nltk
from typing import List, Dict, Any, Optional
from textblob import TextBlob
from datetime import datetime
import logging
from ..models import JobPosting, ParsedJobData
from ..common.utils import clean_text, extract_skills_from_text, parse_experience_level, extract_salary_info

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JobParsingService:
    def __init__(self):
        self.nlp = None
        self._load_nlp_model()
        self._download_nltk_data()
        
        # Common job-related keywords and patterns
        self.requirement_keywords = [
            'required', 'must have', 'essential', 'mandatory', 'necessary',
            'minimum', 'preferred', 'desired', 'ideal', 'looking for',
            'experience with', 'knowledge of', 'proficient in', 'skilled in',
            'familiar with', 'background in', 'expertise in'
        ]
        
        self.responsibility_keywords = [
            'responsible for', 'duties include', 'will be responsible',
            'key responsibilities', 'main duties', 'primary responsibilities',
            'job duties', 'role involves', 'you will', 'responsibilities include'
        ]
        
        self.benefit_keywords = [
            'benefits', 'perks', 'compensation', 'package includes',
            'we offer', 'benefits include', 'competitive salary',
            'health insurance', 'dental', 'vision', '401k', 'pto',
            'paid time off', 'vacation', 'flexible', 'remote work'
        ]
        
        self.education_patterns = [
            r"bachelor[''']?s?\s+degree",
            r"master[''']?s?\s+degree",
            r"phd|doctorate",
            r"associate[''']?s?\s+degree",
            r"high school|hs diploma",
            r"certification",
            r"\b(?:bs|ba|ms|ma|mba)\b"
        ]
        
    def _load_nlp_model(self):
        """Load spaCy NLP model"""
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("spaCy model 'en_core_web_sm' not found. Some NLP features will be limited.")
            self.nlp = None
            
    def _download_nltk_data(self):
        """Download required NLTK data"""
        try:
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('averaged_perceptron_tagger', quiet=True)
        except Exception as e:
            logger.warning(f"Could not download NLTK data: {str(e)}")
    
    def parse_job_description(self, job_posting: JobPosting) -> ParsedJobData:
        """
        Parse a job description and extract structured data
        """
        try:
            description = job_posting.description
            
            # Extract different sections
            requirements = self._extract_requirements(description)
            responsibilities = self._extract_responsibilities(description)
            benefits = self._extract_benefits(description)
            education_requirements = self._extract_education_requirements(description)
            
            # Extract technical skills
            technical_skills = extract_skills_from_text(description)
            
            # Extract soft skills
            soft_skills = self._extract_soft_skills(description)
            
            # Parse experience level
            experience_level = parse_experience_level(description)
            
            # Extract salary information
            salary_info = extract_salary_info(description)
            
            # Determine job type
            job_type = self._determine_job_type(description)
            
            # Extract company size indicators
            company_size = self._extract_company_size(description)
            
            # Analyze job urgency
            urgency_level = self._analyze_urgency(description)
            
            # Extract location details
            location_details = self._parse_location_details(job_posting.location)
            
            # Sentiment analysis
            sentiment = self._analyze_sentiment(description)
            
            return ParsedJobData(
                job_id=getattr(job_posting, 'id', None),
                title=job_posting.title,
                company=job_posting.company,
                location=job_posting.location,
                requirements=requirements,
                responsibilities=responsibilities,
                benefits=benefits,
                education_requirements=education_requirements,
                technical_skills=technical_skills,
                soft_skills=soft_skills,
                experience_level=experience_level,
                salary_info=salary_info,
                job_type=job_type,
                company_size=company_size,
                urgency_level=urgency_level,
                location_details=location_details,
                sentiment_score=sentiment,
                parsed_at=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error parsing job description: {str(e)}")
            return self._create_fallback_parsed_data(job_posting)
    
    def _extract_requirements(self, description: str) -> List[str]:
        """
        Extract job requirements from description
        """
        requirements = []
        
        # Split description into sentences
        sentences = self._split_into_sentences(description)
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            
            # Check if sentence contains requirement keywords
            if any(keyword in sentence_lower for keyword in self.requirement_keywords):
                # Clean and add requirement
                req = clean_text(sentence)
                if len(req) > 20 and len(req) < 200:  # Filter reasonable length
                    requirements.append(req)
        
        # Extract bullet points that look like requirements
        bullet_requirements = self._extract_bullet_points(description, 'requirements')
        requirements.extend(bullet_requirements)
        
        return requirements[:10]  # Limit to top 10
    
    def _extract_responsibilities(self, description: str) -> List[str]:
        """
        Extract job responsibilities from description
        """
        responsibilities = []
        
        sentences = self._split_into_sentences(description)
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            
            # Check if sentence contains responsibility keywords
            if any(keyword in sentence_lower for keyword in self.responsibility_keywords):
                resp = clean_text(sentence)
                if len(resp) > 20 and len(resp) < 200:
                    responsibilities.append(resp)
        
        # Extract bullet points that look like responsibilities
        bullet_responsibilities = self._extract_bullet_points(description, 'responsibilities')
        responsibilities.extend(bullet_responsibilities)
        
        return responsibilities[:10]  # Limit to top 10
    
    def _extract_benefits(self, description: str) -> List[str]:
        """
        Extract benefits and perks from description
        """
        benefits = []
        
        sentences = self._split_into_sentences(description)
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            
            # Check if sentence contains benefit keywords
            if any(keyword in sentence_lower for keyword in self.benefit_keywords):
                benefit = clean_text(sentence)
                if len(benefit) > 15 and len(benefit) < 150:
                    benefits.append(benefit)
        
        # Extract specific benefit patterns
        benefit_patterns = [
            r'health insurance',
            r'dental (?:insurance|coverage)',
            r'vision (?:insurance|coverage)',
            r'401\(k\)|401k',
            r'pto|paid time off',
            r'flexible (?:hours|schedule|work)',
            r'remote work',
            r'work from home',
            r'competitive salary',
            r'stock options',
            r'equity',
            r'bonus',
            r'vacation days?'
        ]
        
        for pattern in benefit_patterns:
            matches = re.findall(pattern, description, re.IGNORECASE)
            for match in matches:
                if match not in [b.lower() for b in benefits]:
                    benefits.append(match.title())
        
        return benefits[:8]  # Limit to top 8
    
    def _extract_education_requirements(self, description: str) -> List[str]:
        """
        Extract education requirements
        """
        education_reqs = []
        
        for pattern in self.education_patterns:
            matches = re.findall(pattern, description, re.IGNORECASE)
            for match in matches:
                edu_req = clean_text(match)
                if edu_req and edu_req not in education_reqs:
                    education_reqs.append(edu_req.title())
        
        return education_reqs
    
    def _extract_soft_skills(self, description: str) -> List[str]:
        """
        Extract soft skills from job description
        """
        soft_skills_keywords = [
            'communication', 'leadership', 'teamwork', 'problem solving',
            'analytical', 'creative', 'detail oriented', 'organized',
            'time management', 'multitasking', 'adaptable', 'flexible',
            'collaborative', 'interpersonal', 'presentation', 'writing',
            'critical thinking', 'decision making', 'project management',
            'customer service', 'negotiation', 'mentoring', 'coaching'
        ]
        
        soft_skills = []
        description_lower = description.lower()
        
        for skill in soft_skills_keywords:
            if skill in description_lower:
                soft_skills.append(skill.title())
        
        return soft_skills
    
    def _determine_job_type(self, description: str) -> str:
        """
        Determine job type (full-time, part-time, contract, etc.)
        """
        description_lower = description.lower()
        
        if any(term in description_lower for term in ['full-time', 'full time', 'permanent']):
            return 'Full-time'
        elif any(term in description_lower for term in ['part-time', 'part time']):
            return 'Part-time'
        elif any(term in description_lower for term in ['contract', 'contractor', 'freelance']):
            return 'Contract'
        elif any(term in description_lower for term in ['intern', 'internship']):
            return 'Internship'
        elif any(term in description_lower for term in ['temporary', 'temp']):
            return 'Temporary'
        else:
            return 'Full-time'  # Default assumption
    
    def _extract_company_size(self, description: str) -> Optional[str]:
        """
        Extract company size indicators
        """
        description_lower = description.lower()
        
        if any(term in description_lower for term in ['startup', 'start-up', 'early stage']):
            return 'Startup'
        elif any(term in description_lower for term in ['fortune 500', 'large corporation', 'enterprise']):
            return 'Large'
        elif any(term in description_lower for term in ['small business', 'small company']):
            return 'Small'
        elif any(term in description_lower for term in ['mid-size', 'medium size', 'growing company']):
            return 'Medium'
        
        return None
    
    def _analyze_urgency(self, description: str) -> str:
        """
        Analyze job posting urgency
        """
        description_lower = description.lower()
        
        urgent_keywords = ['urgent', 'immediate', 'asap', 'right away', 'start immediately']
        high_keywords = ['soon', 'quickly', 'fast-paced', 'rapid growth']
        
        if any(keyword in description_lower for keyword in urgent_keywords):
            return 'Urgent'
        elif any(keyword in description_lower for keyword in high_keywords):
            return 'High'
        else:
            return 'Normal'
    
    def _parse_location_details(self, location: str) -> Dict[str, Any]:
        """
        Parse location details
        """
        if not location:
            return {}
        
        location_lower = location.lower()
        
        return {
            'original': location,
            'is_remote': any(term in location_lower for term in ['remote', 'anywhere', 'work from home']),
            'is_hybrid': 'hybrid' in location_lower,
            'is_onsite': not any(term in location_lower for term in ['remote', 'hybrid'])
        }
    
    def _analyze_sentiment(self, description: str) -> float:
        """
        Analyze sentiment of job description
        """
        try:
            blob = TextBlob(description)
            return blob.sentiment.polarity  # Returns value between -1 and 1
        except Exception:
            return 0.0
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences
        """
        if self.nlp:
            doc = self.nlp(text)
            return [sent.text.strip() for sent in doc.sents]
        else:
            # Fallback to simple splitting
            sentences = re.split(r'[.!?]+', text)
            return [s.strip() for s in sentences if s.strip()]
    
    def _extract_bullet_points(self, text: str, context: str) -> List[str]:
        """
        Extract bullet points from text based on context
        """
        bullet_patterns = [
            r'[•·*-]\s*([^\n]+)',
            r'\d+\.\s*([^\n]+)'
        ]
        
        bullets = []
        for pattern in bullet_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                bullet = clean_text(match)
                if len(bullet) > 15 and len(bullet) < 200:
                    # Filter based on context
                    if context == 'requirements' and any(keyword in bullet.lower() for keyword in self.requirement_keywords[:5]):
                        bullets.append(bullet)
                    elif context == 'responsibilities' and any(keyword in bullet.lower() for keyword in ['will', 'responsible', 'manage', 'develop', 'work']):
                        bullets.append(bullet)
        
        return bullets
    
    def _create_fallback_parsed_data(self, job_posting: JobPosting) -> ParsedJobData:
        """
        Create fallback parsed data when parsing fails
        """
        return ParsedJobData(
            job_id=getattr(job_posting, 'id', None),
            title=job_posting.title,
            company=job_posting.company,
            location=job_posting.location,
            requirements=job_posting.requirements if hasattr(job_posting, 'requirements') else [],
            responsibilities=[],
            benefits=[],
            education_requirements=[],
            technical_skills=job_posting.skills_required if hasattr(job_posting, 'skills_required') else [],
            soft_skills=[],
            experience_level=job_posting.experience_level if hasattr(job_posting, 'experience_level') else 'Not specified',
            salary_info=job_posting.salary_range if hasattr(job_posting, 'salary_range') else 'Not specified',
            job_type='Full-time',
            company_size=None,
            urgency_level='Normal',
            location_details={'original': job_posting.location},
            sentiment_score=0.0,
            parsed_at=datetime.now()
        )

# Global instance
job_parser = JobParsingService()

def parse_job_posting(job_posting: JobPosting) -> ParsedJobData:
    """
    Parse a job posting and return structured data
    """
    return job_parser.parse_job_description(job_posting)

def batch_parse_jobs(job_postings: List[JobPosting]) -> List[ParsedJobData]:
    """
    Parse multiple job postings
    """
    parsed_jobs = []
    for job in job_postings:
        try:
            parsed_job = parse_job_posting(job)
            parsed_jobs.append(parsed_job)
        except Exception as e:
            logger.error(f"Error parsing job {job.title}: {str(e)}")
    
    return parsed_jobs