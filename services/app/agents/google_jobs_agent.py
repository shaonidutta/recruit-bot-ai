import asyncio
import logging
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
import time
from urllib.parse import quote_plus
from ..models import JobPosting, ScrapingResult
from ..common.utils import clean_text, extract_salary_info, parse_experience_level, format_job_data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoogleJobsAgent:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or "your_serpapi_key_here"  # SerpAPI for Google Jobs
        self.base_url = "https://serpapi.com/search.json"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 1.0  # 1 second between requests
        
        # Job type mappings
        self.job_type_mapping = {
            'full_time': 'Full-time',
            'part_time': 'Part-time',
            'contract': 'Contract',
            'temporary': 'Temporary',
            'internship': 'Internship',
            'volunteer': 'Volunteer'
        }
        
    async def scrape_jobs(self, 
                         query: str, 
                         location: str = "",
                         num_results: int = 50,
                         job_type: str = None,
                         date_posted: str = "week",
                         salary_min: int = None,
                         experience_level: str = None) -> ScrapingResult:
        """
        Scrape jobs from Google Jobs using SerpAPI
        """
        try:
            logger.info(f"Starting Google Jobs scraping for query: {query} in {location}")
            
            jobs = []
            start = 0
            max_pages = min(5, (num_results // 10) + 1)  # Google Jobs typically shows 10 results per page
            
            for page in range(max_pages):
                try:
                    # Rate limiting
                    await self._rate_limit()
                    
                    # Build search parameters
                    params = self._build_search_params(
                        query=query,
                        location=location,
                        start=start,
                        job_type=job_type,
                        date_posted=date_posted,
                        salary_min=salary_min,
                        experience_level=experience_level
                    )
                    
                    # Make API request
                    response = self.session.get(self.base_url, params=params)
                    response.raise_for_status()
                    
                    data = response.json()
                    
                    # Extract jobs from response
                    page_jobs = self._extract_jobs_from_response(data)
                    
                    if not page_jobs:
                        logger.info(f"No more jobs found on page {page + 1}")
                        break
                    
                    jobs.extend(page_jobs)
                    logger.info(f"Scraped {len(page_jobs)} jobs from page {page + 1}")
                    
                    # Check if we have enough jobs
                    if len(jobs) >= num_results:
                        jobs = jobs[:num_results]
                        break
                    
                    start += 10
                    
                except Exception as e:
                    logger.error(f"Error scraping page {page + 1}: {str(e)}")
                    continue
            
            # Convert to JobPosting objects
            job_postings = []
            for job_data in jobs:
                try:
                    job_posting = self._convert_to_job_posting(job_data)
                    if job_posting:
                        job_postings.append(job_posting)
                except Exception as e:
                    logger.error(f"Error converting job data: {str(e)}")
                    continue
            
            result = ScrapingResult(
                source="google_jobs",
                query=query,
                location=location,
                total_found=len(job_postings),
                jobs_scraped=len(job_postings),
                jobs=job_postings,
                scraping_time=datetime.now(),
                success=True,
                error_message=None
            )
            
            logger.info(f"Successfully scraped {len(job_postings)} jobs from Google Jobs")
            return result
            
        except Exception as e:
            logger.error(f"Error in Google Jobs scraping: {str(e)}")
            return ScrapingResult(
                source="google_jobs",
                query=query,
                location=location,
                total_found=0,
                jobs_scraped=0,
                jobs=[],
                scraping_time=datetime.now(),
                success=False,
                error_message=str(e)
            )
    
    def _build_search_params(self, 
                           query: str,
                           location: str,
                           start: int = 0,
                           job_type: str = None,
                           date_posted: str = "week",
                           salary_min: int = None,
                           experience_level: str = None) -> Dict[str, Any]:
        """
        Build search parameters for Google Jobs API
        """
        params = {
            'engine': 'google_jobs',
            'q': query,
            'api_key': self.api_key,
            'start': start,
            'num': 10  # Results per page
        }
        
        if location:
            params['location'] = location
        
        if job_type and job_type in self.job_type_mapping:
            params['employment_type'] = job_type
        
        if date_posted:
            # Map date_posted to Google Jobs format
            date_mapping = {
                'today': 'today',
                'week': 'week',
                'month': 'month',
                '3days': '3days'
            }
            if date_posted in date_mapping:
                params['date_posted'] = date_mapping[date_posted]
        
        if salary_min:
            params['salary_min'] = salary_min
        
        return params
    
    def _extract_jobs_from_response(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract job data from Google Jobs API response
        """
        jobs = []
        
        try:
            jobs_results = data.get('jobs_results', [])
            
            for job in jobs_results:
                job_data = {
                    'title': job.get('title', ''),
                    'company': job.get('company_name', ''),
                    'location': job.get('location', ''),
                    'description': job.get('description', ''),
                    'job_id': job.get('job_id', ''),
                    'apply_link': job.get('apply_options', [{}])[0].get('link', '') if job.get('apply_options') else '',
                    'salary': self._extract_salary_from_job(job),
                    'job_type': job.get('detected_extensions', {}).get('schedule_type', ''),
                    'posted_date': job.get('detected_extensions', {}).get('posted_at', ''),
                    'experience_level': self._extract_experience_level(job),
                    'company_logo': job.get('thumbnail', ''),
                    'source': 'Google Jobs'
                }
                
                jobs.append(job_data)
                
        except Exception as e:
            logger.error(f"Error extracting jobs from response: {str(e)}")
        
        return jobs
    
    def _extract_salary_from_job(self, job: Dict[str, Any]) -> Optional[str]:
        """
        Extract salary information from job data
        """
        try:
            # Check detected extensions
            extensions = job.get('detected_extensions', {})
            if 'salary' in extensions:
                return extensions['salary']
            
            # Check description for salary info
            description = job.get('description', '')
            salary_info = extract_salary_info(description)
            if salary_info:
                return f"${salary_info['min']:,} - ${salary_info['max']:,}" if salary_info['max'] else f"${salary_info['min']:,}+"
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting salary: {str(e)}")
            return None
    
    def _extract_experience_level(self, job: Dict[str, Any]) -> Optional[str]:
        """
        Extract experience level from job data
        """
        try:
            # Check detected extensions
            extensions = job.get('detected_extensions', {})
            if 'experience' in extensions:
                return extensions['experience']
            
            # Parse from title and description
            title = job.get('title', '')
            description = job.get('description', '')
            
            return parse_experience_level(f"{title} {description}")
            
        except Exception as e:
            logger.error(f"Error extracting experience level: {str(e)}")
            return None
    
    def _convert_to_job_posting(self, job_data: Dict[str, Any]) -> Optional[JobPosting]:
        """
        Convert scraped job data to JobPosting model
        """
        try:
            # Parse posted date
            posted_date = self._parse_posted_date(job_data.get('posted_date', ''))
            
            # Clean and format data
            title = clean_text(job_data.get('title', ''))
            company = clean_text(job_data.get('company', ''))
            location = clean_text(job_data.get('location', ''))
            description = clean_text(job_data.get('description', ''))
            
            # Create JobPosting
            job_posting = JobPosting(
                job_id=job_data.get('job_id', f"google_{hash(title + company)}"),
                title=title,
                company=company,
                location=location,
                description=description,
                requirements=[],  # Will be parsed later
                salary=job_data.get('salary'),
                job_type=job_data.get('job_type'),
                experience_level=job_data.get('experience_level'),
                posted_date=posted_date,
                apply_url=job_data.get('apply_link', ''),
                source="google_jobs",
                scraped_at=datetime.now()
            )
            
            return job_posting
            
        except Exception as e:
            logger.error(f"Error converting job data to JobPosting: {str(e)}")
            return None
    
    def _parse_posted_date(self, date_str: str) -> Optional[datetime]:
        """
        Parse posted date string to datetime
        """
        try:
            if not date_str:
                return None
            
            # Handle relative dates
            date_str = date_str.lower()
            now = datetime.now()
            
            if 'today' in date_str or 'just posted' in date_str:
                return now
            elif 'yesterday' in date_str:
                return now - timedelta(days=1)
            elif 'day' in date_str:
                # Extract number of days
                import re
                match = re.search(r'(\d+)\s*day', date_str)
                if match:
                    days = int(match.group(1))
                    return now - timedelta(days=days)
            elif 'week' in date_str:
                # Extract number of weeks
                import re
                match = re.search(r'(\d+)\s*week', date_str)
                if match:
                    weeks = int(match.group(1))
                    return now - timedelta(weeks=weeks)
                else:
                    return now - timedelta(weeks=1)
            elif 'month' in date_str:
                # Extract number of months
                import re
                match = re.search(r'(\d+)\s*month', date_str)
                if match:
                    months = int(match.group(1))
                    return now - timedelta(days=months * 30)
                else:
                    return now - timedelta(days=30)
            
            return None
            
        except Exception as e:
            logger.error(f"Error parsing posted date: {str(e)}")
            return None
    
    async def _rate_limit(self):
        """
        Implement rate limiting
        """
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last_request
            await asyncio.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def get_supported_locations(self) -> List[str]:
        """
        Get list of supported locations
        """
        return [
            "United States",
            "New York, NY",
            "San Francisco, CA",
            "Los Angeles, CA",
            "Chicago, IL",
            "Boston, MA",
            "Seattle, WA",
            "Austin, TX",
            "Denver, CO",
            "Atlanta, GA",
            "Remote",
            "Worldwide"
        ]
    
    def get_supported_job_types(self) -> List[str]:
        """
        Get list of supported job types
        """
        return list(self.job_type_mapping.keys())

# Global instance
google_jobs_agent = GoogleJobsAgent()

async def fetch_google_jobs(query: str, 
                          location: str = "",
                          num_results: int = 50,
                          **kwargs) -> ScrapingResult:
    """
    Fetch jobs from Google Jobs
    """
    return await google_jobs_agent.scrape_jobs(
        query=query,
        location=location,
        num_results=num_results,
        **kwargs
    )

def get_google_jobs_locations() -> List[str]:
    """
    Get supported locations for Google Jobs
    """
    return google_jobs_agent.get_supported_locations()

def get_google_jobs_types() -> List[str]:
    """
    Get supported job types for Google Jobs
    """
    return google_jobs_agent.get_supported_job_types()