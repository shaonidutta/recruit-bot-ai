# services/app/models.py

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class JobStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    FILLED = "filled"
    PENDING = "pending"

class MatchScore(BaseModel):
    overall_score: float = Field(..., ge=0, le=100, description="Overall match percentage")
    skills_match: float = Field(..., ge=0, le=100)
    experience_match: float = Field(..., ge=0, le=100)
    location_match: float = Field(..., ge=0, le=100)
    salary_match: float = Field(..., ge=0, le=100)
    culture_match: float = Field(..., ge=0, le=100)
    confidence: float = Field(..., ge=0, le=1, description="Confidence in the match")

class JobPosting(BaseModel):
    id: Optional[str] = None
    title: str
    company: str
    location: str
    description: str
    requirements: List[str] = []
    skills_required: List[str] = []
    experience_level: Optional[str] = None
    salary_range: Optional[Dict[str, Any]] = None
    job_type: Optional[str] = None  # full-time, part-time, contract
    remote_option: bool = False
    posted_date: Optional[datetime] = None
    source: str  # linkedin, indeed, glassdoor, etc.
    url: str
    status: JobStatus = JobStatus.ACTIVE
    
    # Enriched data
    company_size: Optional[str] = None
    company_industry: Optional[str] = None
    company_funding: Optional[str] = None
    hiring_urgency: Optional[str] = None
    tech_stack: List[str] = []
    
class Candidate(BaseModel):
    id: Optional[str] = None
    name: str
    email: str
    phone: Optional[str] = None
    location: str
    skills: List[str] = []
    experience_years: int
    current_role: Optional[str] = None
    preferred_roles: List[str] = []
    salary_expectation: Optional[Dict[str, Any]] = None
    remote_preference: bool = False
    availability: Optional[str] = None
    linkedin_url: Optional[str] = None
    resume_url: Optional[str] = None
    
class Contact(BaseModel):
    name: str
    email: str
    title: str
    company: str
    linkedin_url: Optional[str] = None
    phone: Optional[str] = None
    verified: bool = False
    confidence_score: float = Field(..., ge=0, le=1)
    
class CompanyInfo(BaseModel):
    name: str
    domain: Optional[str] = None
    size: Optional[str] = None
    industry: Optional[str] = None
    funding_stage: Optional[str] = None
    total_funding: Optional[str] = None
    tech_stack: List[str] = []
    culture_keywords: List[str] = []
    hiring_contacts: List[Contact] = []
    recent_news: List[str] = []
    
class JobMatch(BaseModel):
    job: JobPosting
    candidate: Candidate
    match_score: MatchScore
    reasons: List[str] = []
    red_flags: List[str] = []
    created_at: datetime = Field(default_factory=datetime.now)
    
class OutreachTemplate(BaseModel):
    id: Optional[str] = None
    name: str
    subject_template: str
    body_template: str
    channel: str  # email, linkedin
    template_type: str  # initial, follow_up_1, follow_up_2
    variables: List[str] = []  # placeholders like {candidate_name}, {company_name}
    
class OutreachCampaign(BaseModel):
    id: Optional[str] = None
    name: str
    job_match: JobMatch
    templates: List[OutreachTemplate]
    status: str = "pending"  # pending, active, paused, completed
    sent_count: int = 0
    response_count: int = 0
    created_at: datetime = Field(default_factory=datetime.now)
    
class ScrapingResult(BaseModel):
    source: str
    jobs_found: int
    jobs_data: List[JobPosting]
    errors: List[str] = []
    scraping_time: float
    timestamp: datetime = Field(default_factory=datetime.now)
    
class ParsedJobData(BaseModel):
    title: str
    company: str
    location: str
    skills_extracted: List[str]
    requirements_extracted: List[str]
    experience_level: Optional[str]
    salary_info: Optional[Dict[str, Any]]
    job_type: Optional[str]
    remote_option: bool
    confidence_score: float = Field(..., ge=0, le=1)
    
class ParsedJobData(BaseModel):
    job_id: Optional[str] = None
    title: str
    company: str
    location: str
    requirements: List[str] = []
    responsibilities: List[str] = []
    benefits: List[str] = []
    education_requirements: List[str] = []
    technical_skills: List[str] = []
    soft_skills: List[str] = []
    experience_level: str = "Not specified"
    salary_info: str = "Not specified"
    job_type: str = "Full-time"
    company_size: Optional[str] = None
    urgency_level: str = "Normal"
    location_details: Dict[str, Any] = {}
    sentiment_score: float = 0.0
    parsed_at: datetime = Field(default_factory=datetime.now)
    
class EnrichmentResult(BaseModel):
    job_id: str
    company_info: Optional[CompanyInfo]
    contacts_found: List[Contact]
    enrichment_score: float = Field(..., ge=0, le=1)
    errors: List[str] = []
    timestamp: datetime = Field(default_factory=datetime.now)