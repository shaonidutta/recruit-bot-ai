"""
Enrichment Service
Handles company and contact enrichment using Apollo.io API with proper data storage
Uses separate companies and contacts collections for better data management
"""
import logging
import aiohttp
import os
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
from dotenv import load_dotenv

from .company_service import company_service
from .contact_service import contact_service
from ..models.company import CompanyCreate, CompanyResponse
from ..models.contact import ContactCreate, ContactResponse

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)
APOLLO_API_KEY = os.getenv("APOLLO_API_KEY")


class EnrichmentService:
    """Enrichment service with companies and contacts collections"""
    
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
    
    async def close_session(self):
        """Close HTTP session"""
        if self._session and not self._session.closed:
            await self._session.close()
    
    # Company Enrichment Methods
    
    async def _apollo_company_search(self, company_name: str) -> Optional[Dict[str, Any]]:
        """Search for company using Apollo.io API"""
        if not APOLLO_API_KEY or not company_name:
            logger.warning(f"⚠️ Missing Apollo API key or company name")
            return None

        try:
            session = await self.get_session()
            url = "https://api.apollo.io/v1/organizations/search"
            headers = {
                "X-Api-Key": APOLLO_API_KEY,
                "Content-Type": "application/json",
                "Cache-Control": "no-cache"
            }
            payload = {
                "q_organization_name": company_name,
                "page": 1,
                "per_page": 1
            }

            logger.info(f"🔍 Searching Apollo for company: {company_name}")
            logger.debug(f"🔧 Using API key: {APOLLO_API_KEY[:10]}...")

            async with session.post(url, json=payload, headers=headers) as response:
                response_text = await response.text()
                logger.debug(f"🔧 Apollo response status: {response.status}")
                logger.debug(f"🔧 Apollo response: {response_text[:200]}...")

                if response.status == 200:
                    data = await response.json()
                    orgs = data.get("organizations", [])

                    if orgs:
                        org = orgs[0]
                        logger.info(f"✅ Found company in Apollo: {org.get('name', company_name)}")

                        # Create description from available data since Apollo free plan doesn't provide descriptions
                        description = self._create_company_description(org)

                        return {
                            "name": org.get("name", company_name),
                            "domain": org.get("primary_domain"),
                            "website": org.get("website_url"),
                            "industry": org.get("industry"),
                            "size": self._format_company_size(org.get("estimated_num_employees")),
                            "headquarters": f"{org.get('city', '')}, {org.get('state', '')}, {org.get('country', '')}".strip(", "),
                            "description": description,
                            "apollo_id": str(org.get("id"))
                        }
                    else:
                        logger.warning(f"⚠️ No company found in Apollo for: {company_name}")
                elif response.status == 401:
                    logger.error(f"❌ Apollo API authentication failed - check API key")
                elif response.status == 422:
                    logger.error(f"❌ Apollo API insufficient credits: {response_text}")
                else:
                    logger.error(f"❌ Apollo API error {response.status}: {response_text}")

        except Exception as e:
            logger.error(f"❌ Apollo company search failed for {company_name}: {e}")

        return None

    def _create_company_description(self, org: Dict[str, Any]) -> Optional[str]:
        """Create a company description from available Apollo data"""
        try:
            description_parts = []

            # Add industry information
            industry = org.get("industry")
            if industry:
                description_parts.append(f"A company in the {industry} industry")

            # Add employee count
            employees = org.get("estimated_num_employees")
            if employees:
                size_desc = self._format_company_size(employees)
                if size_desc:
                    description_parts.append(f"with {size_desc.lower()}")

            # Add location
            city = org.get("city")
            state = org.get("state")
            country = org.get("country")
            if city and country:
                location = f"{city}, {state}, {country}" if state else f"{city}, {country}"
                description_parts.append(f"based in {location}")

            # Add founded year
            founded = org.get("founded_year")
            if founded:
                description_parts.append(f"founded in {founded}")

            # Add revenue if available
            revenue = org.get("organization_revenue_printed")
            if revenue:
                description_parts.append(f"with ${revenue} in revenue")

            # Add key business areas from keywords (limit to top 5)
            keywords = org.get("keywords", [])
            if keywords and len(keywords) > 0:
                # Filter out generic terms and take top business-relevant keywords
                business_keywords = [kw for kw in keywords[:10] if len(kw) > 3 and
                                   not any(generic in kw.lower() for generic in ['b2b', 'b2c', 'e-commerce', 'services', 'solutions'])]
                if business_keywords:
                    top_keywords = business_keywords[:5]
                    description_parts.append(f"specializing in {', '.join(top_keywords)}")

            if description_parts:
                description = ". ".join(description_parts) + "."
                # Capitalize first letter
                return description[0].upper() + description[1:] if description else None

            return None

        except Exception as e:
            logger.warning(f"Failed to create company description: {e}")
            return None

    async def _apollo_people_search(self, company_id: str, company_domain: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search for people at a company using Apollo.io API"""
        if not APOLLO_API_KEY:
            logger.warning(f"⚠️ Missing Apollo API key for people search")
            return []

        try:
            session = await self.get_session()
            url = "https://api.apollo.io/v1/people/search"
            headers = {
                "X-Api-Key": APOLLO_API_KEY,
                "Content-Type": "application/json",
                "Cache-Control": "no-cache"
            }

            # Build search payload
            payload = {
                "page": 1,
                "per_page": 5,  # Reduced to avoid rate limits
                "organization_ids": [company_id] if company_id else None,
                "person_titles": ["recruiter", "hr", "talent", "hiring", "people", "ceo", "founder"]
            }

            # Add domain filter if available
            if company_domain:
                payload["email_domain"] = company_domain

            logger.info(f"🔍 Searching Apollo for contacts at company: {company_id}")
            logger.debug(f"🔧 People search payload: {payload}")

            async with session.post(url, json=payload, headers=headers) as response:
                response_text = await response.text()
                logger.debug(f"🔧 People API response status: {response.status}")

                if response.status == 200:
                    data = await response.json()
                    people = data.get("people", [])

                    contacts = []
                    for person in people:
                        contact_data = {
                            "name": f"{person.get('first_name', '')} {person.get('last_name', '')}".strip(),
                            "email": person.get("email"),
                            "title": person.get("title"),
                            "phone": person.get("phone"),
                            "linkedin_url": person.get("linkedin_url"),
                            "department": person.get("department"),
                            "seniority": person.get("seniority"),
                            "apollo_id": str(person.get("id"))
                        }

                        # Only add if we have essential data
                        if contact_data["name"] and contact_data["email"]:
                            contacts.append(contact_data)

                    logger.info(f"✅ Found {len(contacts)} contacts in Apollo")
                    return contacts
                elif response.status == 401:
                    logger.error(f"❌ Apollo People API authentication failed")
                elif response.status == 422:
                    logger.error(f"❌ Apollo People API insufficient credits: {response_text}")
                else:
                    logger.error(f"❌ Apollo people API error {response.status}: {response_text}")

        except Exception as e:
            logger.error(f"❌ Apollo people search failed: {e}")

        return []
    
    def _format_company_size(self, employee_count: Optional[int]) -> str:
        """Format employee count into size ranges"""
        if not employee_count:
            return "Unknown"
        
        if employee_count < 10:
            return "1-10 employees"
        elif employee_count < 50:
            return "11-50 employees"
        elif employee_count < 200:
            return "51-200 employees"
        elif employee_count < 1000:
            return "201-1000 employees"
        elif employee_count < 5000:
            return "1001-5000 employees"
        else:
            return "5000+ employees"
    
    # Main Enrichment Methods
    
    async def enrich_company_and_contacts(self, company_name: str) -> Dict[str, Any]:
        """
        Main enrichment method: enriches company and finds contacts
        Returns: {company_id: str, contacts_count: int, enrichment_source: str}
        """
        try:
            logger.info(f" Starting enrichment for: {company_name}")
            
            # Step 1: Enrich company data
            company_result = await self._enrich_company(company_name)
            
            if not company_result["success"]:
                logger.warning(f"⚠️ Company enrichment failed for: {company_name}")
                return {
                    "company_id": None,
                    "contacts_count": 0,
                    "enrichment_source": "failed",
                    "error": company_result.get("error")
                }
            
            company_id = company_result["company_id"]
            company_data = company_result["company_data"]
            
            # Step 2: Skip contact enrichment for now (requires paid Apollo plan)
            contacts_count = 0
            logger.info(f"⚠️ Skipping contact enrichment for {company_name} (requires paid Apollo plan)")
            
            logger.info(f"✅ Enrichment complete: {company_name} (Company ID: {company_id}, Contacts: {contacts_count})")
            
            return {
                "company_id": company_id,
                "contacts_count": contacts_count,
                "enrichment_source": company_data.enrichment_source,
                "company_data": {
                    "name": company_data.name,
                    "domain": company_data.domain,
                    "industry": company_data.industry
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Enrichment failed for {company_name}: {e}")
            return {
                "company_id": None,
                "contacts_count": 0,
                "enrichment_source": "error",
                "error": str(e)
            }
    
    async def _enrich_company(self, company_name: str) -> Dict[str, Any]:
        """Enrich and store company data using Apollo API only"""
        try:
            # Try Apollo enrichment
            apollo_data = await self._apollo_company_search(company_name)

            if apollo_data:
                # Create company with Apollo data
                company_create = CompanyCreate(
                    name=apollo_data["name"],
                    domain=apollo_data["domain"],
                    website=apollo_data["website"],
                    industry=apollo_data["industry"],
                    size=apollo_data["size"],
                    headquarters=apollo_data["headquarters"],
                    description=apollo_data["description"],
                    apollo_id=apollo_data["apollo_id"],
                    enrichment_source="apollo"
                )

                # Find or create company (handles deduplication)
                company = await company_service.find_or_create_company(company_create)

                return {
                    "success": True,
                    "company_id": company.id,
                    "company_data": company
                }
            else:
                # No Apollo data found - use fallback enrichment
                logger.warning(f"⚠️ No Apollo data found for {company_name}")
                logger.info(f"🔄 Using fallback enrichment for: {company_name}")

                # Generate fallback company data
                fallback_data = self._generate_fallback_company_data(company_name)

                company_create = CompanyCreate(
                    name=fallback_data["name"],
                    domain=fallback_data["domain"],
                    website=fallback_data["website"],
                    industry=fallback_data["industry"],
                    size=fallback_data["size"],
                    headquarters=fallback_data["headquarters"],
                    description=fallback_data["description"],
                    apollo_id=None,
                    enrichment_source="fallback"
                )

                # Find or create company (handles deduplication)
                company = await company_service.find_or_create_company(company_create)

                logger.info(f"✅ Created fallback company: {company_name}")

                return {
                    "success": True,
                    "company_id": company.id,
                    "company_data": company
                }

        except Exception as e:
            logger.error(f"❌ Company enrichment failed for {company_name}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _enrich_contacts(self, company_id: str, apollo_company_id: str, company_domain: str) -> Dict[str, Any]:
        """Enrich and store contact data for a company"""
        try:
            # Search for contacts using Apollo
            apollo_contacts = await self._apollo_people_search(apollo_company_id, company_domain)
            
            contacts_created = 0
            for contact_data in apollo_contacts:
                try:
                    # Create contact
                    contact_create = ContactCreate(
                        name=contact_data["name"],
                        email=contact_data["email"],
                        title=contact_data["title"],
                        company_id=company_id,
                        phone=contact_data["phone"],
                        linkedin_url=contact_data["linkedin_url"],
                        department=contact_data["department"],
                        seniority=contact_data["seniority"],
                        apollo_id=contact_data["apollo_id"],
                        enrichment_source="apollo",
                        confidence_score=0.9  # High confidence for Apollo data
                    )
                    
                    # Find or create contact (handles deduplication)
                    contact = await contact_service.find_or_create_contact(contact_create)
                    contacts_created += 1
                    
                except Exception as e:
                    logger.warning(f"⚠️ Failed to create contact {contact_data.get('name', 'Unknown')}: {e}")
                    continue
            
            logger.info(f"✅ Created/found {contacts_created} contacts for company {company_id}")
            
            return {
                "success": True,
                "contacts_count": contacts_created
            }
            
        except Exception as e:
            logger.error(f" Contact enrichment failed for company {company_id}: {e}")
            return {
                "success": False,
                "contacts_count": 0,
                "error": str(e)
            }

    def _generate_fallback_company_data(self, company_name: str) -> Dict[str, Any]:
        """Generate fallback company data when Apollo API doesn't have information"""

        # Generate a basic domain from company name
        domain_name = company_name.lower().replace(" ", "").replace(".", "").replace(",", "")
        domain_name = ''.join(c for c in domain_name if c.isalnum())

        # Common domain extensions for different company types
        if any(word in company_name.lower() for word in ["university", "college", "school"]):
            domain = f"{domain_name}.edu"
            industry = "Education"
            size = "1000-5000"
        elif any(word in company_name.lower() for word in ["government", "gov", "federal", "state"]):
            domain = f"{domain_name}.gov"
            industry = "Government"
            size = "5000+"
        elif any(word in company_name.lower() for word in ["nonprofit", "foundation", "charity"]):
            domain = f"{domain_name}.org"
            industry = "Non-profit"
            size = "100-500"
        else:
            domain = f"{domain_name}.com"
            industry = "Technology"  # Default industry
            size = "100-1000"  # Default size

        # Generate basic description
        description = f"{company_name} is a company in the {industry.lower()} industry."

        return {
            "name": company_name,
            "domain": domain,
            "website": f"https://{domain}",
            "industry": industry,
            "size": size,
            "headquarters": "Unknown",
            "description": description
        }


# Global service instance
enrichment_service = EnrichmentService()
