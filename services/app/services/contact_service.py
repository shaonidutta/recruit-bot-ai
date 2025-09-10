"""
Contact Service
Handles CRUD operations for contacts with duplicate checking and company relationships
"""
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..config.database import get_database
from ..config.constants import COLLECTIONS
from ..models.contact import Contact, ContactCreate, ContactUpdate, ContactResponse, ContactWithCompany

logger = logging.getLogger(__name__)


class ContactService:
    """Service for managing contact data with duplicate checking and company relationships"""
    
    def __init__(self):
        self.db: Optional[AsyncIOMotorDatabase] = None
        self.collection_name = COLLECTIONS["contacts"]
        self.companies_collection_name = COLLECTIONS["companies"]
    
    async def _get_db(self) -> AsyncIOMotorDatabase:
        """Get database connection"""
        if self.db is None:
            self.db = get_database()  # get_database() is not async
        return self.db
    
    async def _get_collection(self):
        """Get contacts collection"""
        db = await self._get_db()
        return db[self.collection_name]
    
    async def _get_companies_collection(self):
        """Get companies collection"""
        db = await self._get_db()
        return db[self.companies_collection_name]
    
    # CRUD Operations
    
    async def create_contact(self, contact_data: ContactCreate) -> ContactResponse:
        """Create a new contact"""
        try:
            collection = await self._get_collection()
            
            # Convert company_id string to ObjectId
            contact_dict = contact_data.dict()
            contact_dict["company_id"] = ObjectId(contact_data.company_id)
            
            # Convert to Contact model for validation
            contact = Contact(**contact_dict)
            
            # Insert into database
            result = await collection.insert_one(contact.dict(by_alias=True))
            
            # Fetch the created contact
            created_contact = await collection.find_one({"_id": result.inserted_id})
            
            logger.info(f"✅ Created contact: {contact.name} (ID: {result.inserted_id})")
            
            return ContactResponse(
                id=str(created_contact["_id"]),
                company_id=str(created_contact["company_id"]),
                **{k: v for k, v in created_contact.items() if k not in ["_id", "company_id"]}
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to create contact {contact_data.name}: {e}")
            raise
    
    async def get_contact_by_id(self, contact_id: str) -> Optional[ContactResponse]:
        """Get contact by ID"""
        try:
            collection = await self._get_collection()
            contact = await collection.find_one({"_id": ObjectId(contact_id)})
            
            if contact:
                return ContactResponse(
                    id=str(contact["_id"]),
                    company_id=str(contact["company_id"]),
                    **{k: v for k, v in contact.items() if k not in ["_id", "company_id"]}
                )
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to get contact {contact_id}: {e}")
            return None
    
    async def get_contact_with_company(self, contact_id: str) -> Optional[ContactWithCompany]:
        """Get contact with embedded company information"""
        try:
            collection = await self._get_collection()
            companies_collection = await self._get_companies_collection()
            
            # Aggregation pipeline to join with companies
            pipeline = [
                {"$match": {"_id": ObjectId(contact_id)}},
                {
                    "$lookup": {
                        "from": self.companies_collection_name,
                        "localField": "company_id",
                        "foreignField": "_id",
                        "as": "company"
                    }
                },
                {"$unwind": {"path": "$company", "preserveNullAndEmptyArrays": True}}
            ]
            
            cursor = collection.aggregate(pipeline)
            result = await cursor.to_list(length=1)
            
            if result:
                contact_data = result[0]
                company_data = contact_data.get("company")
                
                # Format company data
                company_info = None
                if company_data:
                    company_info = {
                        "id": str(company_data["_id"]),
                        "name": company_data.get("name"),
                        "domain": company_data.get("domain"),
                        "industry": company_data.get("industry")
                    }
                
                return ContactWithCompany(
                    id=str(contact_data["_id"]),
                    company_id=str(contact_data["company_id"]),
                    company=company_info,
                    **{k: v for k, v in contact_data.items() if k not in ["_id", "company_id", "company"]}
                )
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to get contact with company {contact_id}: {e}")
            return None
    
    async def update_contact(self, contact_id: str, update_data: ContactUpdate) -> Optional[ContactResponse]:
        """Update an existing contact"""
        try:
            collection = await self._get_collection()
            
            # Prepare update data
            update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
            update_dict["updated_at"] = datetime.utcnow()
            
            # Update contact
            result = await collection.update_one(
                {"_id": ObjectId(contact_id)},
                {"$set": update_dict}
            )
            
            if result.modified_count > 0:
                # Fetch updated contact
                updated_contact = await collection.find_one({"_id": ObjectId(contact_id)})
                logger.info(f"✅ Updated contact: {contact_id}")
                
                return ContactResponse(
                    id=str(updated_contact["_id"]),
                    company_id=str(updated_contact["company_id"]),
                    **{k: v for k, v in updated_contact.items() if k not in ["_id", "company_id"]}
                )
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to update contact {contact_id}: {e}")
            return None
    
    async def delete_contact(self, contact_id: str) -> bool:
        """Delete a contact"""
        try:
            collection = await self._get_collection()
            result = await collection.delete_one({"_id": ObjectId(contact_id)})
            
            if result.deleted_count > 0:
                logger.info(f"✅ Deleted contact: {contact_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to delete contact {contact_id}: {e}")
            return False
    
    # Duplicate Checking Methods
    
    async def find_by_email(self, email: str) -> Optional[ContactResponse]:
        """Find contact by email (primary deduplication method)"""
        try:
            collection = await self._get_collection()
            contact = await collection.find_one({"email": email})
            
            if contact:
                logger.info(f"🔍 Found existing contact by email: {email}")
                return ContactResponse(
                    id=str(contact["_id"]),
                    company_id=str(contact["company_id"]),
                    **{k: v for k, v in contact.items() if k not in ["_id", "company_id"]}
                )
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to find contact by email {email}: {e}")
            return None
    
    async def find_by_apollo_id(self, apollo_id: str) -> Optional[ContactResponse]:
        """Find contact by Apollo ID (API deduplication)"""
        try:
            collection = await self._get_collection()
            contact = await collection.find_one({"apollo_id": apollo_id})
            
            if contact:
                logger.info(f"🔍 Found existing contact by Apollo ID: {apollo_id}")
                return ContactResponse(
                    id=str(contact["_id"]),
                    company_id=str(contact["company_id"]),
                    **{k: v for k, v in contact.items() if k not in ["_id", "company_id"]}
                )
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to find contact by Apollo ID {apollo_id}: {e}")
            return None
    
    # async def find_by_snov_id(self, snov_id: str) -> Optional[ContactResponse]:
    #     """Find contact by Snov ID (API deduplication) - REMOVED: Snov.io not implemented"""
    #     pass
    
    # Company Relationship Methods
    
    async def get_contacts_by_company_id(self, company_id: str, skip: int = 0, limit: int = 100) -> List[ContactResponse]:
        """Get all contacts for a specific company"""
        try:
            collection = await self._get_collection()
            cursor = collection.find({"company_id": ObjectId(company_id)}).skip(skip).limit(limit).sort("created_at", -1)
            
            contacts = []
            async for contact in cursor:
                contacts.append(ContactResponse(
                    id=str(contact["_id"]),
                    company_id=str(contact["company_id"]),
                    **{k: v for k, v in contact.items() if k not in ["_id", "company_id"]}
                ))
            
            return contacts
            
        except Exception as e:
            logger.error(f"❌ Failed to get contacts for company {company_id}: {e}")
            return []
    
    async def find_or_create_contact(self, contact_data: ContactCreate) -> ContactResponse:
        """Find existing contact or create new one (upsert logic)"""
        try:
            # Try to find by email first
            existing = await self.find_by_email(contact_data.email)
            if existing:
                logger.info(f"🔄 Using existing contact (email): {existing.name}")
                return existing
            
            # Try to find by Apollo ID
            if contact_data.apollo_id:
                existing = await self.find_by_apollo_id(contact_data.apollo_id)
                if existing:
                    logger.info(f"🔄 Using existing contact (Apollo): {existing.name}")
                    return existing
            
            # # Try to find by Snov ID - REMOVED: Snov.io not implemented
            # if contact_data.snov_id:
            #     existing = await self.find_by_snov_id(contact_data.snov_id)
            #     if existing:
            #         logger.info(f"🔄 Using existing contact (Snov): {existing.name}")
            #         return existing
            
            # Create new contact
            logger.info(f"🆕 Creating new contact: {contact_data.name}")
            return await self.create_contact(contact_data)
            
        except Exception as e:
            logger.error(f"❌ Failed to find or create contact {contact_data.name}: {e}")
            raise
    
    async def search_contacts(self, query: str, company_id: Optional[str] = None) -> List[ContactResponse]:
        """Search contacts by name or email"""
        try:
            collection = await self._get_collection()
            
            # Build search filter
            search_filter = {
                "$or": [
                    {"name": {"$regex": query, "$options": "i"}},
                    {"email": {"$regex": query, "$options": "i"}}
                ]
            }
            
            # Add company filter if specified
            if company_id:
                search_filter["company_id"] = ObjectId(company_id)
            
            cursor = collection.find(search_filter).limit(50)
            
            contacts = []
            async for contact in cursor:
                contacts.append(ContactResponse(
                    id=str(contact["_id"]),
                    company_id=str(contact["company_id"]),
                    **{k: v for k, v in contact.items() if k not in ["_id", "company_id"]}
                ))
            
            return contacts
            
        except Exception as e:
            logger.error(f"❌ Failed to search contacts: {e}")
            return []
    
    async def get_all_contacts(self, limit: int = 50, skip: int = 0) -> List[ContactResponse]:
        """Fetch all contacts (simple pagination)"""
        try:
            collection = await self._get_collection()
            cursor = collection.find({}).sort("created_at", -1).skip(skip).limit(limit)
            results: List[ContactResponse] = []
            async for doc in cursor:
                results.append(ContactResponse(
                    id=str(doc["_id"]),
                    company_id=str(doc.get("company_id", "")),  # Use .get() with a default
                    **{k: v for k, v in doc.items() if k not in ["_id", "company_id"]}
                ))

            return results
        except Exception as e:
            logger.error(f"❌ Failed to get_all_contacts: {e}")
            return []


# Global service instance
contact_service = ContactService()
