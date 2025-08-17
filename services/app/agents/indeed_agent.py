import asyncio
import re
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
from playwright.async_api import async_playwright, Page
import logging
from urllib.parse import urlencode, quote_plus
from ..models import JobPosting, ScrapingResult
from ..common.utils import clean_text, extract_salary_info, parse_experience_level, extract_skills_from_text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IndeedJobsAgent:
    def __init__(self):
        self.base_url = "https://www.indeed.com/jobs"
        self.max_jobs = 50
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        ]
        
    async def scrape_jobs(self, query: str, location: str = "", max_pages: int = 3) -> ScrapingResult:
        """
        Scrape Indeed jobs using Playwright with anti-detection measures
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
                        '--disable-dev-shm-usage',
                        '--disable-gpu',
                        '--no-first-run',
                        '--disable-extensions'
                    ]
                )
                
                context = await browser.new_context(
                    user_agent=self.user_agents[0],
                    viewport={'width': 1366, 'height': 768},
                    locale='en-US'
                )
                
                page = await context.new_page()
                
                # Add stealth scripts
                await page.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined,
                    });
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5],
                    });
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['en-US', 'en'],
                    });
                """)
                
                for page_num in range(max_pages):
                    try:
                        # Build search URL
                        search_url = self._build_search_url(query, location, page_num * 10)
                        logger.info(f"Scraping Indeed page {page_num + 1}: {search_url}")
                        
                        # Navigate with random delay
                        await asyncio.sleep(2 + page_num * 0.5)
                        await page.goto(search_url, wait_until='domcontentloaded', timeout=30000)
                        
                        # Wait for content to load
                        await page.wait_for_timeout(3000)
                        
                        # Handle potential popups
                        await self._handle_popups(page)
                        
                        # Extract job listings
                        page_jobs = await self._extract_jobs_from_page(page)
                        jobs_data.extend(page_jobs)
                        
                        logger.info(f"Extracted {len(page_jobs)} jobs from page {page_num + 1}")
                        
                        # Random delay between pages
                        await asyncio.sleep(3 + page_num * 0.5)
                        
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
            source="indeed",
            jobs_found=len(jobs_data),
            jobs_data=jobs_data,
            errors=errors,
            scraping_time=scraping_time
        )
    
    def _build_search_url(self, query: str, location: str, start: int = 0) -> str:
        """
        Build Indeed jobs search URL
        """
        params = {
            'q': query,
            'l': location,
            'start': start,
            'sort': 'date',  # Sort by date
            'fromage': '1',  # Last 1 day
            'filter': '0'    # No duplicates
        }
        
        # Remove empty parameters
        params = {k: v for k, v in params.items() if v != ''}
        
        return f"{self.base_url}?{urlencode(params)}"
    
    async def _handle_popups(self, page: Page):
        """
        Handle Indeed popups and overlays
        """
        try:
            # Close cookie banner
            cookie_button = await page.query_selector('#onetrust-accept-btn-handler')
            if cookie_button:
                await cookie_button.click()
                await asyncio.sleep(1)
            
            # Close location popup
            location_popup = await page.query_selector('[data-testid="close-button"]')
            if location_popup:
                await location_popup.click()
                await asyncio.sleep(1)
                
            # Close any modal dialogs
            modal_close = await page.query_selector('.icl-Modal-close')
            if modal_close:
                await modal_close.click()
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.debug(f"Error handling popups: {str(e)}")
    
    async def _extract_jobs_from_page(self, page: Page) -> List[JobPosting]:
        """
        Extract job data from Indeed search results page
        """
        jobs = []
        
        try:
            # Wait for job cards to load
            await page.wait_for_selector('[data-testid="job-title"]', timeout=10000)
            
            # Get all job cards - Indeed uses different selectors
            job_selectors = [
                '.job_seen_beacon',
                '.slider_container .slider_item',
                '[data-jk]'
            ]
            
            job_cards = []
            for selector in job_selectors:
                cards = await page.query_selector_all(selector)
                if cards:
                    job_cards = cards
                    break
            
            logger.info(f"Found {len(job_cards)} job cards")
            
            for i, card in enumerate(job_cards[:self.max_jobs]):
                try:
                    job_data = await self._extract_job_data(card, page, i)
                    if job_data:
                        jobs.append(job_data)
                except Exception as e:
                    logger.error(f"Error extracting job {i}: {str(e)}")
                    
        except Exception as e:
            logger.error(f"Error finding job cards: {str(e)}")
            
        return jobs
    
    async def _extract_job_data(self, card, page: Page, index: int) -> JobPosting:
        """
        Extract individual job data from job card
        """
        try:
            # Extract basic info with multiple selector strategies
            title = await self._extract_text_with_fallback(card, [
                '[data-testid="job-title"] a span',
                '.jobTitle a span',
                'h2 a span',
                '.jobTitle'
            ])
            
            company = await self._extract_text_with_fallback(card, [
                '[data-testid="company-name"]',
                '.companyName',
                'span.companyName a',
                'span.companyName'
            ])
            
            location = await self._extract_text_with_fallback(card, [
                '[data-testid="job-location"]',
                '.companyLocation',
                'div[data-testid="job-location"]'
            ])
            
            # Get job URL
            job_url = ""
            link_elem = await card.query_selector('[data-testid="job-title"] a, .jobTitle a')
            if link_elem:
                href = await link_elem.get_attribute('href')
                if href:
                    job_url = f"https://www.indeed.com{href}" if href.startswith('/') else href
            
            # Extract salary if visible
            salary_text = await self._extract_text_with_fallback(card, [
                '.salary-snippet',
                '.salaryText',
                '[data-testid="job-salary"]'
            ])
            
            # Extract job snippet/description
            description = await self._extract_text_with_fallback(card, [
                '.job-snippet',
                '.summary',
                '[data-testid="job-snippet"]'
            ])
            
            # Try to get more detailed description by clicking on the job
            detailed_description = description
            if job_url:
                try:
                    # Click on job title to get more details
                    await link_elem.click()
                    await asyncio.sleep(1)
                    
                    # Look for detailed job description
                    detail_elem = await page.query_selector('.jobsearch-jobDescriptionText, #jobDescriptionText')
                    if detail_elem:
                        detailed_description = await detail_elem.inner_text()
                        
                except Exception as e:
                    logger.debug(f"Could not get detailed description: {str(e)}")
            
            # Clean and process data
            title = clean_text(title) if title else "Unknown Title"
            company = clean_text(company) if company else "Unknown Company"
            location = clean_text(location) if location else "Unknown Location"
            description = clean_text(detailed_description) if detailed_description else ""
            
            # Extract additional information
            salary_range = extract_salary_info(salary_text + " " + description)
            experience_level = parse_experience_level(description)
            skills_required = extract_skills_from_text(description)
            
            # Parse requirements from description
            requirements = self._extract_requirements(description)
            
            # Determine if remote
            remote_option = any(term in description.lower() for term in [
                'remote', 'work from home', 'telecommute', 'work remotely'
            ])
            
            return JobPosting(
                title=title,
                company=company,
                location=location,
                description=description,
                requirements=requirements,
                skills_required=skills_required,
                experience_level=experience_level,
                salary_range=salary_range,
                remote_option=remote_option,
                posted_date=datetime.now(),
                source="indeed",
                url=job_url,
                status="active"
            )
            
        except Exception as e:
            logger.error(f"Error extracting job data: {str(e)}")
            return None
    
    async def _extract_text_with_fallback(self, element, selectors: List[str]) -> str:
        """
        Try multiple selectors to extract text
        """
        for selector in selectors:
            try:
                elem = await element.query_selector(selector)
                if elem:
                    text = await elem.inner_text()
                    if text and text.strip():
                        return text.strip()
            except Exception:
                continue
        return ""
    
    def _extract_requirements(self, description: str) -> List[str]:
        """
        Extract job requirements from description
        """
        if not description:
            return []
        
        requirements = []
        
        # Common requirement patterns
        patterns = [
            r'(?:requirements?|qualifications?):\s*([^\n]+)',
            r'(?:must have|required):\s*([^\n]+)',
            r'(?:experience with|knowledge of)\s+([^\n\.]+)',
            r'(?:proficient in|skilled in)\s+([^\n\.]+)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, description, re.IGNORECASE)
            for match in matches:
                req = clean_text(match)
                if req and len(req) > 10:  # Filter out very short matches
                    requirements.append(req)
        
        # Look for bullet points
        bullet_patterns = [
            r'[•·*-]\s*([^\n]+)',
            r'\d+\.\s*([^\n]+)'
        ]
        
        for pattern in bullet_patterns:
            matches = re.findall(pattern, description)
            for match in matches:
                req = clean_text(match)
                if req and len(req) > 15 and any(keyword in req.lower() for keyword in [
                    'experience', 'skill', 'knowledge', 'ability', 'proficient', 'familiar'
                ]):
                    requirements.append(req)
        
        return requirements[:5]  # Limit to top 5 requirements

# Global instance
indeed_agent = IndeedJobsAgent()

async def fetch_indeed_jobs(query: str, location: str = "") -> Dict[str, Any]:
    """
    Main function to fetch Indeed jobs
    """
    try:
        result = await indeed_agent.scrape_jobs(query, location)
        return {
            "agent": "indeed",
            "status": "success",
            "jobs_found": result.jobs_found,
            "jobs": [job.dict() for job in result.jobs_data],
            "errors": result.errors,
            "scraping_time": result.scraping_time
        }
    except Exception as e:
        logger.error(f"Indeed scraping failed: {str(e)}")
        return {
            "agent": "indeed",
            "status": "error",
            "error": str(e),
            "jobs": []
        }
