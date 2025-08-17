import asyncio
import re
from datetime import datetime
from typing import List, Dict, Any
from playwright.async_api import async_playwright, Page
import logging
from ..models import JobPosting, ScrapingResult
from ..common.utils import clean_text, extract_salary_info, parse_experience_level

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LinkedInJobsAgent:
    def __init__(self):
        self.base_url = "https://www.linkedin.com/jobs/search"
        self.max_jobs = 50
        
    async def scrape_jobs(self, query: str, location: str = "", max_pages: int = 3) -> ScrapingResult:
        """
        Scrape LinkedIn jobs using Playwright with stealth techniques
        """
        start_time = datetime.now()
        jobs_data = []
        errors = []
        
        try:
            async with async_playwright() as p:
                # Launch browser with stealth settings
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage'
                    ]
                )
                
                context = await browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    viewport={'width': 1920, 'height': 1080}
                )
                
                page = await context.new_page()
                
                # Add stealth scripts
                await page.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined,
                    });
                """)
                
                for page_num in range(max_pages):
                    try:
                        # Build search URL
                        search_url = self._build_search_url(query, location, page_num * 25)
                        logger.info(f"Scraping LinkedIn page {page_num + 1}: {search_url}")
                        
                        await page.goto(search_url, wait_until='networkidle')
                        await asyncio.sleep(2)  # Wait for dynamic content
                        
                        # Extract job listings
                        page_jobs = await self._extract_jobs_from_page(page)
                        jobs_data.extend(page_jobs)
                        
                        # Random delay between pages
                        await asyncio.sleep(3)
                        
                    except Exception as e:
                        error_msg = f"Error scraping page {page_num + 1}: {str(e)}"
                        logger.error(error_msg)
                        errors.append(error_msg)
                        
                await browser.close()
                
        except Exception as e:
            error_msg = f"Browser setup error: {str(e)}"
            logger.error(error_msg)
            errors.append(error_msg)
            
        scraping_time = (datetime.now() - start_time).total_seconds()
        
        return ScrapingResult(
            source="linkedin",
            jobs_found=len(jobs_data),
            jobs_data=jobs_data,
            errors=errors,
            scraping_time=scraping_time
        )
    
    def _build_search_url(self, query: str, location: str, start: int = 0) -> str:
        """
        Build LinkedIn jobs search URL
        """
        params = {
            'keywords': query,
            'location': location,
            'start': start,
            'f_TPR': 'r86400',  # Last 24 hours
            'f_JT': 'F',  # Full-time
        }
        
        param_string = '&'.join([f"{k}={v}" for k, v in params.items() if v])
        return f"{self.base_url}?{param_string}"
    
    async def _extract_jobs_from_page(self, page: Page) -> List[JobPosting]:
        """
        Extract job data from LinkedIn search results page
        """
        jobs = []
        
        try:
            # Wait for job cards to load
            await page.wait_for_selector('.job-search-card', timeout=10000)
            
            # Get all job cards
            job_cards = await page.query_selector_all('.job-search-card')
            
            for card in job_cards[:self.max_jobs]:
                try:
                    job_data = await self._extract_job_data(card, page)
                    if job_data:
                        jobs.append(job_data)
                except Exception as e:
                    logger.error(f"Error extracting job data: {str(e)}")
                    
        except Exception as e:
            logger.error(f"Error finding job cards: {str(e)}")
            
        return jobs
    
    async def _extract_job_data(self, card, page: Page) -> JobPosting:
        """
        Extract individual job data from job card
        """
        try:
            # Extract basic info
            title_elem = await card.query_selector('.base-search-card__title')
            title = await title_elem.inner_text() if title_elem else "Unknown Title"
            
            company_elem = await card.query_selector('.base-search-card__subtitle')
            company = await company_elem.inner_text() if company_elem else "Unknown Company"
            
            location_elem = await card.query_selector('.job-search-card__location')
            location = await location_elem.inner_text() if location_elem else "Unknown Location"
            
            # Get job URL
            link_elem = await card.query_selector('a[data-control-name="job_search_job_result_click"]')
            job_url = await link_elem.get_attribute('href') if link_elem else ""
            
            # Extract additional details by clicking on the job
            description = ""
            requirements = []
            skills_required = []
            
            if job_url:
                try:
                    # Click on job to get details
                    await link_elem.click()
                    await asyncio.sleep(1)
                    
                    # Extract job description
                    desc_elem = await page.query_selector('.show-more-less-html__markup')
                    if desc_elem:
                        description = await desc_elem.inner_text()
                        requirements, skills_required = self._parse_job_description(description)
                        
                except Exception as e:
                    logger.error(f"Error extracting job details: {str(e)}")
            
            # Clean and process data
            title = clean_text(title)
            company = clean_text(company)
            location = clean_text(location)
            description = clean_text(description)
            
            # Extract salary and experience info
            salary_range = extract_salary_info(description)
            experience_level = parse_experience_level(description)
            
            return JobPosting(
                title=title,
                company=company,
                location=location,
                description=description,
                requirements=requirements,
                skills_required=skills_required,
                experience_level=experience_level,
                salary_range=salary_range,
                remote_option='remote' in description.lower() or 'work from home' in description.lower(),
                posted_date=datetime.now(),
                source="linkedin",
                url=job_url,
                status="active"
            )
            
        except Exception as e:
            logger.error(f"Error extracting job data: {str(e)}")
            return None
    
    def _parse_job_description(self, description: str) -> tuple:
        """
        Parse job description to extract requirements and skills
        """
        requirements = []
        skills = []
        
        # Common requirement patterns
        req_patterns = [
            r'(?:require[sd]?|must have|need|essential).*?(?:\n|\.|;)',
            r'(?:qualifications?).*?(?:\n|\.|;)',
            r'(?:experience with|knowledge of).*?(?:\n|\.|;)'
        ]
        
        for pattern in req_patterns:
            matches = re.findall(pattern, description, re.IGNORECASE | re.DOTALL)
            requirements.extend([clean_text(match) for match in matches])
        
        # Common technical skills
        tech_skills = [
            'python', 'javascript', 'java', 'react', 'node.js', 'sql', 'aws', 'docker',
            'kubernetes', 'git', 'agile', 'scrum', 'machine learning', 'ai', 'data science'
        ]
        
        description_lower = description.lower()
        for skill in tech_skills:
            if skill in description_lower:
                skills.append(skill)
        
        return requirements[:5], skills  # Limit to top 5

# Global instance
linkedin_agent = LinkedInJobsAgent()

async def fetch_linkedin_jobs(query: str, location: str = "") -> Dict[str, Any]:
    """
    Main function to fetch LinkedIn jobs
    """
    try:
        result = await linkedin_agent.scrape_jobs(query, location)
        return {
            "agent": "linkedin",
            "status": "success",
            "jobs_found": result.jobs_found,
            "jobs": [job.dict() for job in result.jobs_data],
            "errors": result.errors,
            "scraping_time": result.scraping_time
        }
    except Exception as e:
        logger.error(f"LinkedIn scraping failed: {str(e)}")
        return {
            "agent": "linkedin",
            "status": "error",
            "error": str(e),
            "jobs": []
        }
