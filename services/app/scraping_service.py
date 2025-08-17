# services/app/scraping_service.py

import asyncio
from typing import List, Dict
from playwright.async_api import async_playwright, Browser, Page
from tenacity import retry, stop_after_attempt, wait_exponential
from app.common.utils import get_json
import os
import httpx
import feedparser
import requests

from serpapi import GoogleSearch
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

SERPAPI_KEY = os.getenv("SERPAPI_KEY")
SCRAPINGANT_API_KEY = os.getenv("SCRAPINGANT_API_KEY")
if not SERPAPI_KEY:
    raise ValueError("❌ SERPAPI_KEY is not set. Please add it to your .env file.")



# ---------- Helpers ----------
async def init_browser():
    """Initialize a Playwright browser with stealth options."""
    p = await async_playwright().start()
    browser = await p.chromium.launch(
        headless=False,
        args=[
            "--no-sandbox",
            "--disable-blink-features=AutomationControlled",
            "--disable-web-security",
            "--disable-features=VizDisplayCompositor",
        ],
    )
    context = await browser.new_context(
        viewport={"width": 1920, "height": 1080},
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
    )
    # Anti-detection patch
    await context.add_init_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )
    return p, browser, context


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, max=10))
async def safe_goto(page: Page, url: str):
    """Goto with retries."""
    await page.goto(url, wait_until="domcontentloaded", timeout=25000)
    await page.wait_for_timeout(3000)


def normalize_result(
    title: str,
    url: str,
    source: str,
    company: str | None = None,
    location: str | None = None,
    description: str | None = None,
) -> Dict:
    """Ensure consistent schema across scrapers."""
    return {
        "title": title.strip(),
        "company": company or "Unknown",
        "location": location or "Unknown",
        "url": url,
        "raw_description": description or "N/A",
        "source": source,
    }


# ---------- LinkedIn ----------
async def scrape_linkedin_jobs(job_title: str) -> List[Dict]:
    print(f"Scraping LinkedIn for: {job_title}")
    results: List[Dict] = []

    p, browser, context = await init_browser()
    page = await context.new_page()

    try:
        search_url = f"https://www.google.com/search?q=site%3Alinkedin.com%2Fjobs%2Fview+%22{job_title}%22"
        await safe_goto(page, search_url)

        job_links = await page.query_selector_all('a[href*="linkedin.com/jobs/view"]')

        for link in job_links[:5]:
            href = await link.get_attribute("href")
            title = await link.inner_text() if href else None
            if href and title:
                results.append(
                    normalize_result(
                        title=title,
                        url=href,
                        source="LinkedIn",
                        description="LinkedIn job description would be scraped from job page.",
                    )
                )
    except Exception as e:
        print(f"[LinkedIn] Error: {e}")
    finally:
        await browser.close()
        await p.stop()

    return results

# ---------- Indeed ----------
# async def scrape_indeed_jobs(job_title: str) -> List[Dict]:
#     print(f"Fetching Indeed RSS for: {job_title}")
#     q = job_title.replace(" ", "+")
#     domains = [
#         "indeed.com",
#         "in.indeed.com",
#         "ca.indeed.com",
#         "uk.indeed.com",
#     ]
#     headers = {
#         "User-Agent": (
#             "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
#             "AppleWebKit/537.36 (KHTML, like Gecko) "
#             "Chrome/120.0.0.0 Safari/537.36"
#         )
#     }

#     results = []
#     for domain in domains:
#         url = f"https://{domain}/rss?q={q}"
#         try:
#             r = httpx.get(url, headers=headers, timeout=15, follow_redirects=True)
#             print("rrrr", r)
#             if r.status_code != 200:
#                 continue


#             feed = feedparser.parse(r.text)
#             if not feed.entries:
#                 print(f"[Indeed] No entries from {url}")
#                 continue

#             for entry in feed.entries[:5]:
#                 results.append({
#                     "title": entry.title,
#                     "url": entry.link,
#                     "company": entry.get("author", "Unknown"),
#                     "raw_description": entry.get("summary", ""),
#                     "location": "Unknown",
#                     "source": f"Indeed-RSS-{domain}"
#                 })

#             if results:
#                 break  # stop once we find results from one domain
#         except Exception as e:
#             print(f"[Indeed RSS] Error from {url}: {e}")

#     print(f"[Indeed] Returning {len(results)} jobs")
#     return results

# async def scrape_indeed_jobs(job_title: str) -> List[Dict]:
#     """
#     Fetch Indeed jobs using SerpAPI (Google Jobs Engine).
#     """
#     print(f"Fetching Indeed jobs for: {job_title}")

#     params = {
#         "engine": "google_jobs",
#         "q": job_title,
#         "hl": "en",
#         "api_key": SERPAPI_KEY,
#     }

#     search = GoogleSearch(params)
#     results = search.get_dict()
#     jobs_data = results.get("jobs_results", [])
#     jobs = []

#     for job in jobs_data:
#         if "indeed" in str(job.get("via", "")).lower():
#             jobs.append({
#                 "title": job.get("title"),
#                 "company": job.get("company_name"),
#                 "location": job.get("location"),
#                 "description": job.get("description"),
#                 "via": job.get("via"),
#             })

#     print(f"✅ Found {len(jobs)} Indeed jobs.")
#     return jobs

# async def scrape_indeed_jobs(job_title: str) -> List[Dict]:
#     """
#     Scrape jobs directly from Indeed search results.
#     """
#     print(f"Scraping Indeed for: {job_title}")
#     results = []

#     async with async_playwright() as p:
#         browser = await p.chromium.launch(
#             headless=True,
#             args=[
#                 "--no-sandbox",
#                 "--disable-blink-features=AutomationControlled",
#                 "--disable-dev-shm-usage",
#             ]
#         )
#         context = await browser.new_context(
#             viewport={"width": 1280, "height": 800},
#             user_agent=(
#                 "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
#                 "AppleWebKit/537.36 (KHTML, like Gecko) "
#                 "Chrome/120.0.0.0 Safari/537.36"
#             ),
#         )

#         # Hide webdriver
#         await context.add_init_script(
#             "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
#         )

#         page = await context.new_page()
#         search_url = f"https://www.indeed.com/jobs?q={job_title.replace(' ', '+')}"
#         await page.goto(search_url, wait_until="domcontentloaded", timeout=30000)

#         # Wait for job cards
#         await page.wait_for_selector("div.job_seen_beacon", timeout=10000)

#         job_cards = await page.query_selector_all("div.job_seen_beacon")
#         print(f"Found {len(job_cards)} job cards.")

#         for card in job_cards[:10]:  # limit to 10 for demo
#             try:
#                 title_el = await card.query_selector("h2.jobTitle span")
#                 company_el = await card.query_selector("span.companyName")
#                 location_el = await card.query_selector("div.companyLocation")
#                 snippet_el = await card.query_selector("div.job-snippet")

#                 job = {
#                     "title": await title_el.inner_text() if title_el else "N/A",
#                     "company": await company_el.inner_text() if company_el else "N/A",
#                     "location": await location_el.inner_text() if location_el else "N/A",
#                     "description": await snippet_el.inner_text() if snippet_el else "N/A",
#                 }
#                 results.append(job)

#             except Exception as e:
#                 print(f"Error parsing job card: {e}")

#         await browser.close()

#     print(f"✅ Scraped {len(results)} jobs from Indeed.")
#     return results

SCRAPINGANT_URL = "https://api.scrapingant.com/v2/general"

def scrape_indeed_jobs(job_title: str) -> List[Dict]:
    """
    Scrape Indeed jobs using ScrapingAnt API (handles JS + bot detection).
    """
    query = job_title.replace(" ", "+")
    search_url = f"https://www.indeed.com/jobs?q={query}"

    print(f"Scraping Indeed via ScrapingAnt: {search_url}")

    params = {
        "url": search_url,
        "x-api-key": SCRAPINGANT_API_KEY,
        "browser": "true",   # run in real browser mode
    }

    response = requests.get(SCRAPINGANT_URL, params=params, timeout=30)

    if response.status_code != 200:
        print(f"❌ ScrapingAnt error: {response.status_code} {response.text}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    jobs = []
    job_cards = soup.select("div.job_seen_beacon")

    print(f"Found {len(job_cards)} job cards")

    for card in job_cards[:10]:  # limit to 10
        try:
            title = card.select_one("h2.jobTitle span")
            company = card.select_one("span.companyName")
            location = card.select_one("div.companyLocation")
            snippet = card.select_one("div.job-snippet")

            jobs.append({
                "title": title.get_text(strip=True) if title else "N/A",
                "company": company.get_text(strip=True) if company else "N/A",
                "location": location.get_text(strip=True) if location else "N/A",
                "description": snippet.get_text(strip=True) if snippet else "N/A",
            })
        except Exception as e:
            print(f"⚠️ Error parsing card: {e}")

    return jobs


# ---------- Glassdoor ----------
async def scrape_glassdoor_jobs(job_title: str) -> List[Dict]:
    print(f"Scraping Glassdoor for: {job_title}")
    results: List[Dict] = []

    p, browser, context = await init_browser()
    page = await context.new_page()

    try:
        search_url = f"https://www.glassdoor.com/Job/jobs.htm?sc.keyword={job_title.replace(' ', '%20')}"
        await safe_goto(page, search_url)

        selectors = [".react-job-listing", '[data-test="job-link"]', ".JobCard"]
        job_cards = []
        for sel in selectors:
            job_cards = await page.query_selector_all(sel)
            if job_cards:
                break

        for card in job_cards[:5]:
            try:
                title_el = await card.query_selector("[data-test='job-title']")
                company_el = await card.query_selector("[data-test='employer-name']")
                loc_el = await card.query_selector("[data-test='job-location']")

                title = await title_el.inner_text() if title_el else None
                company = await company_el.inner_text() if company_el else None
                loc = await loc_el.inner_text() if loc_el else None

                if title:
                    results.append(
                        normalize_result(
                            title=title,
                            url="https://www.glassdoor.com",
                            source="Glassdoor",
                            company=company,
                            location=loc,
                        )
                    )
            except Exception as e:
                print(f"[Glassdoor] Card error: {e}")
    except Exception as e:
        print(f"[Glassdoor] Error: {e}")
    finally:
        await browser.close()
        await p.stop()

    return results

async def fetch_jobs_google(job_title: str):
    params = {
        "engine": "google_jobs",
        "q": job_title,
        "api_key": os.getenv("SERPAPI_KEY")
    }
    data = await get_json("https://serpapi.com/search", params=params)
    jobs = []
    for j in data.get("jobs_results", []):
        jobs.append({
            "title": j.get("title"),
            "company": j.get("company_name"),
            "location": j.get("location"),
            "url": j.get("link"),
            "raw_description": j.get("description"),
            "source": "GoogleJobs"
        })
    return jobs

async def scrape_indeed_with_playwright(job_title: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, args=[
            "--disable-blink-features=AutomationControlled",
            "--disable-web-security",
            "--disable-features=site-per-process",
        ])
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/120.0.0.0 Safari/537.36"
        )

        # Hide webdriver flag
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        """)

        page = await context.new_page()
        await page.goto(f"https://www.indeed.com/jobs?q={job_title}&l=", timeout=30000)

        # wait for job cards
        await page.wait_for_selector("div.job_seen_beacon", timeout=10000)
        jobs = await page.query_selector_all("div.job_seen_beacon")

        results = []
        for job in jobs[:5]:
            title = await job.inner_text()
            results.append(title)

        await browser.close()
        return results