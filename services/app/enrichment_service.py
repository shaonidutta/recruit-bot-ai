"""
Mid-Level Enrichment Service - Essential company data enrichment
"""

import os
import aiohttp
from typing import Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)
APOLLO_API_KEY = os.getenv("APOLLO_API_KEY")


class EnrichmentService:
    """Mid-level company enrichment with essential data only"""

    def __init__(self):
        self._session: Optional[aiohttp.ClientSession] = None

    async def get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        if not self._session or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={"User-Agent": "AI-Recruitment-Agent/1.0"}
            )
        return self._session

    async def enrich_company(self, company_name: str) -> Optional[Dict[str, Any]]:
        """Basic company enrichment using Apollo.io"""
        if not APOLLO_API_KEY or not company_name:
            return None

        try:
            session = await self.get_session()
            url = "https://api.apollo.io/v1/organizations/search"
            payload = {
                "api_key": APOLLO_API_KEY,
                "q_organization_name": company_name,
                "page": 1,
                "per_page": 1
            }

            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    orgs = data.get("organizations", [])
                    if orgs:
                        org = orgs[0]
                        return {
                            "name": org.get("name", company_name),
                            "domain": org.get("primary_domain"),
                            "website": org.get("website_url"),
                            "industry": org.get("industry"),
                            "size": self._format_company_size(org.get("estimated_num_employees")),
                            "headquarters": f"{org.get('city', '')}, {org.get('state', '')}, {org.get('country', '')}".strip(", ")
                        }
        except Exception as e:
            logger.error(f"Enrichment failed for {company_name}: {e}")

        return None

    def _format_company_size(self, employee_count: Optional[int]) -> Optional[str]:
        """Format company size into readable ranges"""
        if not employee_count:
            return None

        if employee_count < 10:
            return "1-10 employees"
        elif employee_count < 50:
            return "11-50 employees"
        elif employee_count < 200:
            return "51-200 employees"
        elif employee_count < 1000:
            return "201-1000 employees"
        else:
            return "1000+ employees"

    async def cleanup(self):
        """Clean up resources"""
        if self._session:
            await self._session.close()


# Global instance
enrichment_service = EnrichmentService()

async def get_enrichment_service() -> EnrichmentService:
    """Get enrichment service instance"""
    return enrichment_service
