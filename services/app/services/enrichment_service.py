import asyncio
import aiohttp
import logging
from typing import List, Dict, Any, Optional, Tuple
import json
import re
from datetime import datetime
from ..models import JobPosting, CompanyInfo, Contact, EnrichmentResult
from ..common.utils import validate_email, extract_contact_info

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnrichmentService:
    def __init__(self, apollo_api_key: str = None, snov_api_key: str = None):
        self.apollo_api_key = apollo_api_key
        self.snov_api_key = snov_api_key
        self.apollo_base_url = "https://api.apollo.io/v1"
        self.snov_base_url = "https://app.snov.io/api/v1"
        
        # Rate limiting
        self.apollo_rate_limit = 60  # requests per minute
        self.snov_rate_limit = 100   # requests per minute
        
        # Cache for company data
        self.company_cache = {}
        
    async def enrich_job_posting(self, job: JobPosting) -> EnrichmentResult:
        """
        Enrich a job posting with company information and contact details
        """
        try:
            logger.info(f"Enriching job posting: {job.title} at {job.company}")
            
            # Get company information
            company_info = await self.get_company_info(job.company, job.location)
            
            # Find hiring manager contacts
            contacts = await self.find_hiring_contacts(job.company, job.title)
            
            # Extract additional info from job description
            additional_info = self._extract_additional_info(job.description)
            
            return EnrichmentResult(
                job_id=job.id or f"job_{hash(job.title + job.company)}",
                company_info=company_info,
                contacts=contacts,
                enrichment_timestamp=datetime.now(),
                data_sources=["apollo", "snov", "internal_parsing"],
                additional_data=additional_info
            )
            
        except Exception as e:
            logger.error(f"Error enriching job posting: {str(e)}")
            return self._create_fallback_enrichment(job)
    
    async def get_company_info(self, company_name: str, location: str = None) -> CompanyInfo:
        """
        Get comprehensive company information from multiple sources
        """
        try:
            # Check cache first
            cache_key = f"{company_name.lower()}_{location or 'unknown'}"
            if cache_key in self.company_cache:
                logger.info(f"Using cached company info for {company_name}")
                return self.company_cache[cache_key]
            
            # Try Apollo.io first
            apollo_info = await self._get_apollo_company_info(company_name)
            
            # Fallback to Snov.io if Apollo fails
            if not apollo_info:
                apollo_info = await self._get_snov_company_info(company_name)
            
            # Create company info object
            company_info = CompanyInfo(
                name=apollo_info.get('name', company_name),
                domain=apollo_info.get('website_url', ''),
                industry=apollo_info.get('industry', 'Unknown'),
                size=apollo_info.get('employee_count', 'Unknown'),
                location=apollo_info.get('headquarters_address', location or 'Unknown'),
                description=apollo_info.get('short_description', ''),
                founded_year=apollo_info.get('founded_year'),
                linkedin_url=apollo_info.get('linkedin_url', ''),
                technologies=apollo_info.get('technologies', []),
                funding_info=apollo_info.get('funding_info', {})
            )
            
            # Cache the result
            self.company_cache[cache_key] = company_info
            
            return company_info
            
        except Exception as e:
            logger.error(f"Error getting company info for {company_name}: {str(e)}")
            return self._create_fallback_company_info(company_name, location)
    
    async def find_hiring_contacts(self, company_name: str, job_title: str) -> List[Contact]:
        """
        Find potential hiring managers and recruiters for a specific role
        """
        try:
            contacts = []
            
            # Define search criteria based on job title
            search_titles = self._get_relevant_contact_titles(job_title)
            
            # Search Apollo.io for contacts
            apollo_contacts = await self._search_apollo_contacts(company_name, search_titles)
            contacts.extend(apollo_contacts)
            
            # Search Snov.io for additional contacts
            snov_contacts = await self._search_snov_contacts(company_name, search_titles)
            contacts.extend(snov_contacts)
            
            # Remove duplicates and validate emails
            unique_contacts = self._deduplicate_contacts(contacts)
            validated_contacts = await self._validate_contact_emails(unique_contacts)
            
            # Sort by relevance (hiring managers first, then recruiters)
            sorted_contacts = self._sort_contacts_by_relevance(validated_contacts, job_title)
            
            return sorted_contacts[:10]  # Return top 10 contacts
            
        except Exception as e:
            logger.error(f"Error finding hiring contacts for {company_name}: {str(e)}")
            return []
    
    async def _get_apollo_company_info(self, company_name: str) -> Dict[str, Any]:
        """
        Get company information from Apollo.io
        """
        if not self.apollo_api_key:
            logger.warning("Apollo API key not provided")
            return {}
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.apollo_base_url}/organizations/search"
                headers = {
                    "Cache-Control": "no-cache",
                    "Content-Type": "application/json",
                    "X-Api-Key": self.apollo_api_key
                }
                
                payload = {
                    "q_organization_name": company_name,
                    "page": 1,
                    "per_page": 1
                }
                
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        organizations = data.get('organizations', [])
                        if organizations:
                            return organizations[0]
                    else:
                        logger.error(f"Apollo API error: {response.status}")
                        
        except Exception as e:
            logger.error(f"Error calling Apollo API: {str(e)}")
        
        return {}
    
    async def _get_snov_company_info(self, company_name: str) -> Dict[str, Any]:
        """
        Get company information from Snov.io
        """
        if not self.snov_api_key:
            logger.warning("Snov API key not provided")
            return {}
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.snov_base_url}/get-domain-emails-with-info"
                params = {
                    "domain": f"{company_name.lower().replace(' ', '')}.com",
                    "type": "all",
                    "limit": 1
                }
                headers = {
                    "Authorization": f"Bearer {self.snov_api_key}"
                }
                
                async with session.get(url, params=params, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('domain_info', {})
                    else:
                        logger.error(f"Snov API error: {response.status}")
                        
        except Exception as e:
            logger.error(f"Error calling Snov API: {str(e)}")
        
        return {}
    
    async def _search_apollo_contacts(self, company_name: str, search_titles: List[str]) -> List[Contact]:
        """
        Search for contacts using Apollo.io
        """
        if not self.apollo_api_key:
            return []
        
        contacts = []
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.apollo_base_url}/people/search"
                headers = {
                    "Cache-Control": "no-cache",
                    "Content-Type": "application/json",
                    "X-Api-Key": self.apollo_api_key
                }
                
                for title in search_titles:
                    payload = {
                        "q_organization_name": company_name,
                        "person_titles": [title],
                        "page": 1,
                        "per_page": 5
                    }
                    
                    async with session.post(url, headers=headers, json=payload) as response:
                        if response.status == 200:
                            data = await response.json()
                            people = data.get('people', [])
                            
                            for person in people:
                                contact = Contact(
                                    name=f"{person.get('first_name', '')} {person.get('last_name', '')}".strip(),
                                    email=person.get('email', ''),
                                    title=person.get('title', ''),
                                    company=company_name,
                                    linkedin_url=person.get('linkedin_url', ''),
                                    phone=person.get('phone', ''),
                                    source="apollo"
                                )
                                contacts.append(contact)
                        
                        # Rate limiting
                        await asyncio.sleep(1)  # 1 second between requests
                        
        except Exception as e:
            logger.error(f"Error searching Apollo contacts: {str(e)}")
        
        return contacts
    
    async def _search_snov_contacts(self, company_name: str, search_titles: List[str]) -> List[Contact]:
        """
        Search for contacts using Snov.io
        """
        if not self.snov_api_key:
            return []
        
        contacts = []
        
        try:
            # First, get the company domain
            domain = f"{company_name.lower().replace(' ', '')}.com"
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.snov_base_url}/get-domain-emails-with-info"
                params = {
                    "domain": domain,
                    "type": "all",
                    "limit": 20
                }
                headers = {
                    "Authorization": f"Bearer {self.snov_api_key}"
                }
                
                async with session.get(url, params=params, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        emails = data.get('emails', [])
                        
                        for email_data in emails:
                            # Filter by relevant titles
                            person_title = email_data.get('position', '').lower()
                            if any(title.lower() in person_title for title in search_titles):
                                contact = Contact(
                                    name=f"{email_data.get('firstName', '')} {email_data.get('lastName', '')}".strip(),
                                    email=email_data.get('email', ''),
                                    title=email_data.get('position', ''),
                                    company=company_name,
                                    linkedin_url=email_data.get('socialLinks', {}).get('linkedin', ''),
                                    source="snov"
                                )
                                contacts.append(contact)
                        
        except Exception as e:
            logger.error(f"Error searching Snov contacts: {str(e)}")
        
        return contacts
    
    def _get_relevant_contact_titles(self, job_title: str) -> List[str]:
        """
        Get relevant contact titles based on the job title
        """
        job_title_lower = job_title.lower()
        
        # Base titles to always search for
        base_titles = [
            "hiring manager",
            "recruiter",
            "talent acquisition",
            "hr manager",
            "human resources"
        ]
        
        # Add specific titles based on job type
        if any(tech in job_title_lower for tech in ['engineer', 'developer', 'programmer', 'software']):
            base_titles.extend([
                "engineering manager",
                "technical lead",
                "cto",
                "vp engineering",
                "head of engineering"
            ])
        
        if any(role in job_title_lower for role in ['data', 'analyst', 'scientist']):
            base_titles.extend([
                "data manager",
                "analytics manager",
                "head of data",
                "chief data officer"
            ])
        
        if any(role in job_title_lower for role in ['marketing', 'sales']):
            base_titles.extend([
                "marketing manager",
                "sales manager",
                "vp marketing",
                "vp sales"
            ])
        
        if any(role in job_title_lower for role in ['product', 'pm']):
            base_titles.extend([
                "product manager",
                "vp product",
                "head of product"
            ])
        
        return base_titles
    
    def _deduplicate_contacts(self, contacts: List[Contact]) -> List[Contact]:
        """
        Remove duplicate contacts based on email
        """
        seen_emails = set()
        unique_contacts = []
        
        for contact in contacts:
            if contact.email and contact.email not in seen_emails:
                seen_emails.add(contact.email)
                unique_contacts.append(contact)
        
        return unique_contacts
    
    async def _validate_contact_emails(self, contacts: List[Contact]) -> List[Contact]:
        """
        Validate contact email addresses
        """
        validated_contacts = []
        
        for contact in contacts:
            if contact.email and validate_email(contact.email):
                validated_contacts.append(contact)
        
        return validated_contacts
    
    def _sort_contacts_by_relevance(self, contacts: List[Contact], job_title: str) -> List[Contact]:
        """
        Sort contacts by relevance to the job
        """
        def relevance_score(contact: Contact) -> int:
            score = 0
            title_lower = contact.title.lower()
            job_title_lower = job_title.lower()
            
            # Hiring managers get highest priority
            if 'hiring manager' in title_lower:
                score += 100
            
            # Recruiters and talent acquisition
            if any(term in title_lower for term in ['recruiter', 'talent acquisition']):
                score += 90
            
            # Department-specific managers
            if any(tech in job_title_lower for tech in ['engineer', 'developer']) and \
               any(term in title_lower for term in ['engineering', 'technical', 'cto']):
                score += 80
            
            # General HR
            if any(term in title_lower for term in ['hr', 'human resources']):
                score += 70
            
            # VP and C-level
            if any(term in title_lower for term in ['vp', 'vice president', 'ceo', 'cto', 'coo']):
                score += 60
            
            return score
        
        return sorted(contacts, key=relevance_score, reverse=True)
    
    def _extract_additional_info(self, job_description: str) -> Dict[str, Any]:
        """
        Extract additional information from job description
        """
        additional_info = {}
        
        try:
            # Extract contact information from description
            contact_info = extract_contact_info(job_description)
            if contact_info:
                additional_info['contact_info'] = contact_info
            
            # Extract application instructions
            app_instructions = self._extract_application_instructions(job_description)
            if app_instructions:
                additional_info['application_instructions'] = app_instructions
            
            # Extract urgency indicators
            urgency = self._extract_urgency_indicators(job_description)
            if urgency:
                additional_info['urgency_level'] = urgency
            
            # Extract team size information
            team_size = self._extract_team_size(job_description)
            if team_size:
                additional_info['team_size'] = team_size
            
        except Exception as e:
            logger.error(f"Error extracting additional info: {str(e)}")
        
        return additional_info
    
    def _extract_application_instructions(self, description: str) -> str:
        """
        Extract application instructions from job description
        """
        patterns = [
            r'to apply[^.]*[.!]',
            r'application process[^.]*[.!]',
            r'send.*resume[^.]*[.!]',
            r'submit.*application[^.]*[.!]'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, description, re.IGNORECASE)
            if matches:
                return matches[0]
        
        return ''
    
    def _extract_urgency_indicators(self, description: str) -> str:
        """
        Extract urgency level from job description
        """
        urgent_keywords = ['urgent', 'immediate', 'asap', 'quickly', 'fast-track']
        high_keywords = ['soon', 'quickly', 'expedited']
        
        description_lower = description.lower()
        
        if any(keyword in description_lower for keyword in urgent_keywords):
            return 'urgent'
        elif any(keyword in description_lower for keyword in high_keywords):
            return 'high'
        else:
            return 'normal'
    
    def _extract_team_size(self, description: str) -> str:
        """
        Extract team size information from job description
        """
        patterns = [
            r'team of (\d+)',
            r'(\d+)[- ]person team',
            r'(\d+)[- ]member team',
            r'join our (\d+)[- ]person'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, description, re.IGNORECASE)
            if matches:
                return f"{matches[0]} people"
        
        return ''
    
    def _create_fallback_company_info(self, company_name: str, location: str = None) -> CompanyInfo:
        """
        Create fallback company info when enrichment fails
        """
        return CompanyInfo(
            name=company_name,
            domain='',
            industry='Unknown',
            size='Unknown',
            location=location or 'Unknown',
            description='',
            founded_year=None,
            linkedin_url='',
            technologies=[],
            funding_info={}
        )
    
    def _create_fallback_enrichment(self, job: JobPosting) -> EnrichmentResult:
        """
        Create fallback enrichment result when enrichment fails
        """
        return EnrichmentResult(
            job_id=job.id or f"job_{hash(job.title + job.company)}",
            company_info=self._create_fallback_company_info(job.company, job.location),
            contacts=[],
            enrichment_timestamp=datetime.now(),
            data_sources=["fallback"],
            additional_data={}
        )

# Global instance
enrichment_service = EnrichmentService()

def set_api_keys(apollo_key: str = None, snov_key: str = None):
    """
    Set API keys for enrichment services
    """
    global enrichment_service
    if apollo_key:
        enrichment_service.apollo_api_key = apollo_key
    if snov_key:
        enrichment_service.snov_api_key = snov_key

async def enrich_job_with_contacts(job: JobPosting) -> EnrichmentResult:
    """
    Enrich a job posting with company and contact information
    """
    return await enrichment_service.enrich_job_posting(job)

async def get_company_information(company_name: str, location: str = None) -> CompanyInfo:
    """
    Get company information
    """
    return await enrichment_service.get_company_info(company_name, location)

async def find_hiring_managers(company_name: str, job_title: str) -> List[Contact]:
    """
    Find hiring managers for a specific role
    """
    return await enrichment_service.find_hiring_contacts(company_name, job_title)