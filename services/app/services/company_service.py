"""
Company Service
Handles CRUD operations for companies with duplicate checking and enrichment
"""
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..config.database import get_database
from ..config.constants import COLLECTIONS
from ..models.company import Company, CompanyCreate, CompanyUpdate, CompanyResponse

logger = logging.getLogger(__name__)


class CompanyService:
    """Service for managing company data with duplicate checking"""
    
    def __init__(self):
        self.db: Optional[AsyncIOMotorDatabase] = None
        self.collection_name = COLLECTIONS["companies"]
    
    async def _get_db(self) -> AsyncIOMotorDatabase:
        """Get database connection"""
        if self.db is None:
            self.db = get_database()  # get_database() is not async
        return self.db
    
    async def _get_collection(self):
        """Get companies collection"""
        db = await self._get_db()
        return db[self.collection_name]
    
    # CRUD Operations
    
    async def create_company(self, company_data: CompanyCreate) -> CompanyResponse:
        """Create a new company"""
        try:
            collection = await self._get_collection()
            
            # Convert to Company model for validation
            company = Company(**company_data.dict())
            
            # Insert into database
            result = await collection.insert_one(company.dict(by_alias=True))
            
            # Fetch the created company
            created_company = await collection.find_one({"_id": result.inserted_id})
            
            logger.info(f"✅ Created company: {company.name} (ID: {result.inserted_id})")
            
            return CompanyResponse(
                id=str(created_company["_id"]),
                **{k: v for k, v in created_company.items() if k != "_id"}
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to create company {company_data.name}: {e}")
            raise
    
    async def get_company_by_id(self, company_id: str) -> Optional[CompanyResponse]:
        """Get company by ID"""
        try:
            collection = await self._get_collection()
            company = await collection.find_one({"_id": ObjectId(company_id)})
            
            if company:
                return CompanyResponse(
                    id=str(company["_id"]),
                    **{k: v for k, v in company.items() if k != "_id"}
                )
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to get company {company_id}: {e}")
            return None
    
    async def update_company(self, company_id: str, update_data: CompanyUpdate) -> Optional[CompanyResponse]:
        """Update an existing company"""
        try:
            collection = await self._get_collection()
            
            # Prepare update data
            update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
            update_dict["updated_at"] = datetime.utcnow()
            
            # Update company
            result = await collection.update_one(
                {"_id": ObjectId(company_id)},
                {"$set": update_dict}
            )
            
            if result.modified_count > 0:
                # Fetch updated company
                updated_company = await collection.find_one({"_id": ObjectId(company_id)})
                logger.info(f"✅ Updated company: {company_id}")
                
                return CompanyResponse(
                    id=str(updated_company["_id"]),
                    **{k: v for k, v in updated_company.items() if k != "_id"}
                )
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to update company {company_id}: {e}")
            return None
    
    async def delete_company(self, company_id: str) -> bool:
        """Delete a company"""
        try:
            collection = await self._get_collection()
            result = await collection.delete_one({"_id": ObjectId(company_id)})
            
            if result.deleted_count > 0:
                logger.info(f"✅ Deleted company: {company_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to delete company {company_id}: {e}")
            return False
    
    # Duplicate Checking Methods
    
    async def find_by_domain(self, domain: str) -> Optional[CompanyResponse]:
        """Find company by domain (primary deduplication method)"""
        try:
            collection = await self._get_collection()
            company = await collection.find_one({"domain": domain})
            
            if company:
                logger.info(f"🔍 Found existing company by domain: {domain}")
                return CompanyResponse(
                    id=str(company["_id"]),
                    **{k: v for k, v in company.items() if k != "_id"}
                )
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to find company by domain {domain}: {e}")
            return None
    
    async def find_by_name(self, name: str) -> Optional[CompanyResponse]:
        """Find company by name (secondary deduplication method)"""
        try:
            collection = await self._get_collection()
            
            # Case-insensitive search
            company = await collection.find_one({"name": {"$regex": f"^{name}$", "$options": "i"}})
            
            if company:
                logger.info(f"🔍 Found existing company by name: {name}")
                return CompanyResponse(
                    id=str(company["_id"]),
                    **{k: v for k, v in company.items() if k != "_id"}
                )
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to find company by name {name}: {e}")
            return None
    
    async def find_by_apollo_id(self, apollo_id: str) -> Optional[CompanyResponse]:
        """Find company by Apollo ID (API deduplication)"""
        try:
            collection = await self._get_collection()
            company = await collection.find_one({"apollo_id": apollo_id})
            
            if company:
                logger.info(f"🔍 Found existing company by Apollo ID: {apollo_id}")
                return CompanyResponse(
                    id=str(company["_id"]),
                    **{k: v for k, v in company.items() if k != "_id"}
                )
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to find company by Apollo ID {apollo_id}: {e}")
            return None
    
    # Advanced Operations
    
    async def find_or_create_company(self, company_data: CompanyCreate) -> CompanyResponse:
        """Find existing company or create new one (upsert logic)"""
        try:
            # Try to find by domain first
            if company_data.domain:
                existing = await self.find_by_domain(company_data.domain)
                if existing:
                    logger.info(f"🔄 Using existing company (domain): {existing.name}")
                    return existing
            
            # Try to find by Apollo ID
            if company_data.apollo_id:
                existing = await self.find_by_apollo_id(company_data.apollo_id)
                if existing:
                    logger.info(f"🔄 Using existing company (Apollo): {existing.name}")
                    return existing
            
            # Try to find by name (fuzzy match)
            existing = await self.find_by_name(company_data.name)
            if existing:
                logger.info(f"🔄 Using existing company (name): {existing.name}")
                return existing
            
            # Create new company
            logger.info(f"🆕 Creating new company: {company_data.name}")
            return await self.create_company(company_data)
            
        except Exception as e:
            logger.error(f"❌ Failed to find or create company {company_data.name}: {e}")
            raise
    
    async def list_companies(self, skip: int = 0, limit: int = 100) -> List[CompanyResponse]:
        """List companies with pagination"""
        try:
            collection = await self._get_collection()
            cursor = collection.find().skip(skip).limit(limit).sort("created_at", -1)
            
            companies = []
            async for company in cursor:
                companies.append(CompanyResponse(
                    id=str(company["_id"]),
                    **{k: v for k, v in company.items() if k != "_id"}
                ))
            
            return companies
            
        except Exception as e:
            logger.error(f"❌ Failed to list companies: {e}")
            return []
    
    async def search_companies(self, query: str) -> List[CompanyResponse]:
        """Search companies by name or domain"""
        try:
            collection = await self._get_collection()
            
            # Text search on name and domain
            cursor = collection.find({
                "$or": [
                    {"name": {"$regex": query, "$options": "i"}},
                    {"domain": {"$regex": query, "$options": "i"}}
                ]
            }).limit(50)
            
            companies = []
            async for company in cursor:
                companies.append(CompanyResponse(
                    id=str(company["_id"]),
                    **{k: v for k, v in company.items() if k != "_id"}
                ))
            
            return companies
            
        except Exception as e:
            logger.error(f"❌ Failed to search companies: {e}")
            return []


# Global service instance
company_service = CompanyService()
