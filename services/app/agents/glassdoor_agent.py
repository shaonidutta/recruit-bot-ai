import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
import time
import re
from playwright.async_api import async_playwright, Browser, Page
from ..models import JobPosting, ScrapingResult
from ..common.utils import clean_text, extract_salary_info, parse_experience_level, format_job_data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GlassdoorAgent:
    def __init__(self):
        self.base_url = "https://www.glassdoor.com"
        self.browser = None
        self.page = None
        
        # Stealth settings
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        ]
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 2.0  # 2 seconds between requests
        
        # Selectors
        self.selectors = {
            'job_cards': '[data-test="job-search-job-card"], .JobCard',
            'job_title': '[data-test="job-title"], .jobTitle a, .job-title',
            'company_name': '[data-test="employer-name"], .employerName, .company-name',
            'location': '[data-test="job-location"], .location, .job-location',
            'salary': '[data-test="detailSalary"], .salary, .job-salary',
            'job_description': '[data-test="jobDescriptionContent"], .jobDescriptionContent, .job-description',
            'apply_button': '[data-test="apply-button"], .apply-button, .applyButton',
            'next_page': '[data-test="pagination-next"], .next, .pagination-next',
            'job_type': '.job-type, .employment-type',
            'posted_date': '.posted-date, .job-age, [data-test="job-age"]'
        }
    
    async def scrape_jobs(self, 
                         query: str, 
                         location: str = "",
                         num_results: int = 50,
                         job_type: str = None,
                         salary_min: int = None,
                         experience_level: str = None) -> ScrapingResult:
        """
        Scrape jobs from Glassdoor
        """
        try:
            logger.info(f"Starting Glassdoor scraping for query: {query} in {location}")
            
            # Initialize browser
            await self._init_browser()
            
            jobs = []
            page_num = 1
            max_pages = min(10, (num_results // 10) + 1)  # Glassdoor shows ~10-30 jobs per page
            
            # Build search URL
            search_url = self._build_search_url(query, location, job_type, salary_min)
            
            for page in range(max_pages):
                try:
                    # Rate limiting
                    await self._rate_limit()
                    
                    # Navigate to search page
                    if page == 0:
                        await self.page.goto(search_url, wait_until='networkidle')
                    else:
                        # Click next page
                        next_button = await self.page.query_selector(self.selectors['next_page'])
                        if next_button:
                            await next_button.click()
                            await self.page.wait_for_load_state('networkidle')
                        else:
                            logger.info(f"No next page button found on page {page + 1}")
                            break
                    
                    # Handle potential popups/modals
                    await self._handle_popups()
                    
                    # Extract jobs from current page
                    page_jobs = await self._extract_jobs_from_page()
                    
                    if not page_jobs:
                        logger.info(f"No jobs found on page {page + 1}")
                        break
                    
                    jobs.extend(page_jobs)
                    logger.info(f"Scraped {len(page_jobs)} jobs from page {page + 1}")
                    
                    # Check if we have enough jobs
                    if len(jobs) >= num_results:
                        jobs = jobs[:num_results]
                        break
                    
                    page_num += 1
                    
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
                source="glassdoor",
                query=query,
                location=location,
                total_found=len(job_postings),
                jobs_scraped=len(job_postings),
                jobs=job_postings,
                scraping_time=datetime.now(),
                success=True,
                error_message=None
            )
            
            logger.info(f"Successfully scraped {len(job_postings)} jobs from Glassdoor")
            return result
            
        except Exception as e:
            logger.error(f"Error in Glassdoor scraping: {str(e)}")
            return ScrapingResult(
                source="glassdoor",
                query=query,
                location=location,
                total_found=0,
                jobs_scraped=0,
                jobs=[],
                scraping_time=datetime.now(),
                success=False,
                error_message=str(e)
            )
        finally:
            await self._cleanup()
    
    async def _init_browser(self):
        """
        Initialize Playwright browser with stealth settings
        """
        try:
            playwright = await async_playwright().start()
            
            # Launch browser with stealth settings
            self.browser = await playwright.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                    '--disable-gpu',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor'
                ]
            )
            
            # Create new page
            self.page = await self.browser.new_page()
            
            # Set user agent
            import random
            user_agent = random.choice(self.user_agents)
            await self.page.set_user_agent(user_agent)
            
            # Set viewport
            await self.page.set_viewport_size({"width": 1366, "height": 768})
            
            # Add stealth scripts
            await self.page.add_init_script("""
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
            
        except Exception as e:
            logger.error(f"Error initializing browser: {str(e)}")
            raise
    
    def _build_search_url(self, 
                         query: str, 
                         location: str = "",
                         job_type: str = None,
                         salary_min: int = None) -> str:
        """
        Build Glassdoor search URL
        """
        from urllib.parse import quote_plus
        
        base_url = f"{self.base_url}/Job/jobs.htm"
        params = []
        
        if query:
            params.append(f"sc.keyword={quote_plus(query)}")
        
        if location:
            params.append(f"locT=C&locId=1147401&locKeyword={quote_plus(location)}")
        
        if job_type:
            # Map job types to Glassdoor format
            type_mapping = {
                'full_time': 'fulltime',
                'part_time': 'parttime',
                'contract': 'contract',
                'internship': 'internship'
            }
            if job_type in type_mapping:
                params.append(f"jobType={type_mapping[job_type]}")
        
        if salary_min:
            params.append(f"minSalary={salary_min}")
        
        # Add default parameters
        params.extend([
            "suggestCount=0",
            "suggestChosen=false",
            "clickSource=searchBtn",
            "typedKeyword=",
            "sc.occupationParam="
        ])
        
        url = f"{base_url}?{'&'.join(params)}"
        logger.info(f"Built Glassdoor search URL: {url}")
        return url
    
    async def _handle_popups(self):
        """
        Handle Glassdoor popups and modals
        """
        try:
            # Wait a bit for popups to appear
            await asyncio.sleep(1)
            
            # Common popup selectors
            popup_selectors = [
                '[data-test="modal-close"]',
                '.modal-close',
                '.close-button',
                '[aria-label="Close"]',
                '.CloseButton',
                '#HardsellOverlay .SVGInline'
            ]
            
            for selector in popup_selectors:
                try:
                    popup = await self.page.query_selector(selector)
                    if popup:
                        await popup.click()
                        await asyncio.sleep(0.5)
                        logger.info(f"Closed popup with selector: {selector}")
                        break
                except:
                    continue
            
            # Handle sign-up prompts
            signup_selectors = [
                '[data-test="sign-up-later"]',
                '.sign-up-later',
                'text="Continue without signing up"',
                'text="Maybe Later"'
            ]
            
            for selector in signup_selectors:
                try:
                    button = await self.page.query_selector(selector)
                    if button:
                        await button.click()
                        await asyncio.sleep(0.5)
                        logger.info(f"Clicked sign-up later with selector: {selector}")
                        break
                except:
                    continue
                    
        except Exception as e:
            logger.error(f"Error handling popups: {str(e)}")
    
    async def _extract_jobs_from_page(self) -> List[Dict[str, Any]]:
        """
        Extract job data from current page
        """
        jobs = []
        
        try:
            # Wait for job cards to load
            await self.page.wait_for_selector(self.selectors['job_cards'], timeout=10000)
            
            # Get all job cards
            job_cards = await self.page.query_selector_all(self.selectors['job_cards'])
            
            for i, card in enumerate(job_cards):
                try:
                    job_data = await self._extract_job_from_card(card)
                    if job_data:
                        jobs.append(job_data)
                except Exception as e:
                    logger.error(f"Error extracting job {i}: {str(e)}")
                    continue
            
        except Exception as e:
            logger.error(f"Error extracting jobs from page: {str(e)}")
        
        return jobs
    
    async def _extract_job_from_card(self, card) -> Optional[Dict[str, Any]]:
        """
        Extract job data from a single job card
        """
        try:
            job_data = {}
            
            # Extract title
            title_element = await card.query_selector(self.selectors['job_title'])
            if title_element:
                job_data['title'] = await title_element.inner_text()
                # Get job URL
                href = await title_element.get_attribute('href')
                if href:
                    job_data['job_url'] = f"{self.base_url}{href}" if href.startswith('/') else href
            
            # Extract company
            company_element = await card.query_selector(self.selectors['company_name'])
            if company_element:
                job_data['company'] = await company_element.inner_text()
            
            # Extract location
            location_element = await card.query_selector(self.selectors['location'])
            if location_element:
                job_data['location'] = await location_element.inner_text()
            
            # Extract salary
            salary_element = await card.query_selector(self.selectors['salary'])
            if salary_element:
                job_data['salary'] = await salary_element.inner_text()
            
            # Extract job type
            job_type_element = await card.query_selector(self.selectors['job_type'])
            if job_type_element:
                job_data['job_type'] = await job_type_element.inner_text()
            
            # Extract posted date
            posted_element = await card.query_selector(self.selectors['posted_date'])
            if posted_element:
                job_data['posted_date'] = await posted_element.inner_text()
            
            # Get job description (requires clicking on the job)
            if 'job_url' in job_data:
                try:
                    # Open job in new tab to get description
                    new_page = await self.browser.new_page()
                    await new_page.goto(job_data['job_url'], wait_until='networkidle')
                    
                    # Handle popups on job page
                    await self._handle_popups_on_page(new_page)
                    
                    # Extract description
                    desc_element = await new_page.query_selector(self.selectors['job_description'])
                    if desc_element:
                        job_data['description'] = await desc_element.inner_text()
                    
                    await new_page.close()
                    
                except Exception as e:
                    logger.error(f"Error getting job description: {str(e)}")
                    job_data['description'] = "Description not available"
            
            # Set source
            job_data['source'] = 'Glassdoor'
            
            return job_data if job_data.get('title') and job_data.get('company') else None
            
        except Exception as e:
            logger.error(f"Error extracting job from card: {str(e)}")
            return None
    
    async def _handle_popups_on_page(self, page):
        """
        Handle popups on job detail page
        """
        try:
            await asyncio.sleep(1)
            
            popup_selectors = [
                '[data-test="modal-close"]',
                '.modal-close',
                '.close-button',
                '[aria-label="Close"]'
            ]
            
            for selector in popup_selectors:
                try:
                    popup = await page.query_selector(selector)
                    if popup:
                        await popup.click()
                        await asyncio.sleep(0.5)
                        break
                except:
                    continue
                    
        except Exception as e:
            logger.error(f"Error handling popups on job page: {str(e)}")
    
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
            
            # Parse salary
            salary = self._parse_salary(job_data.get('salary', ''))
            
            # Parse experience level
            experience_level = parse_experience_level(f"{title} {description}")
            
            # Create JobPosting
            job_posting = JobPosting(
                job_id=job_data.get('job_id', f"glassdoor_{hash(title + company)}"),
                title=title,
                company=company,
                location=location,
                description=description,
                requirements=[],  # Will be parsed later
                salary=salary,
                job_type=job_data.get('job_type'),
                experience_level=experience_level,
                posted_date=posted_date,
                apply_url=job_data.get('job_url', ''),
                source="glassdoor",
                scraped_at=datetime.now()
            )
            
            return job_posting
            
        except Exception as e:
            logger.error(f"Error converting job data to JobPosting: {str(e)}")
            return None
    
    def _parse_salary(self, salary_str: str) -> Optional[str]:
        """
        Parse salary string
        """
        try:
            if not salary_str:
                return None
            
            # Clean salary string
            salary_str = clean_text(salary_str)
            
            # Extract salary using utility function
            salary_info = extract_salary_info(salary_str)
            if salary_info:
                if salary_info['max']:
                    return f"${salary_info['min']:,} - ${salary_info['max']:,}"
                else:
                    return f"${salary_info['min']:,}+"
            
            return salary_str if salary_str else None
            
        except Exception as e:
            logger.error(f"Error parsing salary: {str(e)}")
            return None
    
    def _parse_posted_date(self, date_str: str) -> Optional[datetime]:
        """
        Parse posted date string to datetime
        """
        try:
            if not date_str:
                return None
            
            date_str = date_str.lower().strip()
            now = datetime.now()
            
            if 'today' in date_str or 'just posted' in date_str:
                return now
            elif 'yesterday' in date_str:
                return now - timedelta(days=1)
            elif 'day' in date_str:
                # Extract number of days
                match = re.search(r'(\d+)\s*day', date_str)
                if match:
                    days = int(match.group(1))
                    return now - timedelta(days=days)
            elif 'week' in date_str:
                # Extract number of weeks
                match = re.search(r'(\d+)\s*week', date_str)
                if match:
                    weeks = int(match.group(1))
                    return now - timedelta(weeks=weeks)
                else:
                    return now - timedelta(weeks=1)
            elif 'month' in date_str:
                # Extract number of months
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
    
    async def _cleanup(self):
        """
        Clean up browser resources
        """
        try:
            if self.page:
                await self.page.close()
            if self.browser:
                await self.browser.close()
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")

# Global instance
glassdoor_agent = GlassdoorAgent()

async def fetch_glassdoor_jobs(query: str, 
                             location: str = "",
                             num_results: int = 50,
                             **kwargs) -> ScrapingResult:
    """
    Fetch jobs from Glassdoor
    """
    return await glassdoor_agent.scrape_jobs(
        query=query,
        location=location,
        num_results=num_results,
        **kwargs
    )