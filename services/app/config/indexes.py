"""
Database Indexes Configuration
Creates optimal indexes for companies, contacts, and jobs collections
Based on MongoDB best practices for query optimization
"""
import asyncio
import logging
from motor.motor_asyncio import AsyncIOMotorDatabase
from .database import get_database
from .constants import COLLECTIONS

logger = logging.getLogger(__name__)


async def create_companies_indexes(db: AsyncIOMotorDatabase):
    """Create indexes for companies collection"""
    collection = db[COLLECTIONS["companies"]]
    
    # Primary lookup indexes
    await collection.create_index("domain", unique=True, sparse=True, name="idx_companies_domain")
    await collection.create_index("name", name="idx_companies_name")
    
    # External API deduplication
    await collection.create_index("apollo_id", unique=True, sparse=True, name="idx_companies_apollo_id")
    
    # Temporal indexes
    await collection.create_index([("created_at", -1)], name="idx_companies_created_at")
    await collection.create_index([("updated_at", -1)], name="idx_companies_updated_at")
    
    # Compound indexes for common queries
    await collection.create_index([("domain", 1), ("name", 1)], name="idx_companies_domain_name")
    
    logger.info("✅ Created companies collection indexes")


async def create_contacts_indexes(db: AsyncIOMotorDatabase):
    """Create indexes for contacts collection"""
    collection = db[COLLECTIONS["contacts"]]
    
    # Primary lookup indexes
    await collection.create_index("email", unique=True, name="idx_contacts_email")
    await collection.create_index("company_id", name="idx_contacts_company_id")
    
    # External API deduplication
    await collection.create_index("apollo_id", unique=True, sparse=True, name="idx_contacts_apollo_id")
    await collection.create_index("snov_id", unique=True, sparse=True, name="idx_contacts_snov_id")
    
    # Temporal indexes
    await collection.create_index([("created_at", -1)], name="idx_contacts_created_at")
    await collection.create_index([("updated_at", -1)], name="idx_contacts_updated_at")
    
    # Compound indexes for common queries
    await collection.create_index([("company_id", 1), ("title", 1)], name="idx_contacts_company_title")
    await collection.create_index([("company_id", 1), ("seniority", 1)], name="idx_contacts_company_seniority")
    await collection.create_index([("company_id", 1), ("department", 1)], name="idx_contacts_company_department")
    await collection.create_index([("company_id", 1), ("created_at", -1)], name="idx_contacts_company_created")
    
    logger.info("✅ Created contacts collection indexes")


async def create_jobs_indexes(db: AsyncIOMotorDatabase):
    """Create indexes for jobs collection (updated for company relationships)"""
    collection = db[COLLECTIONS["jobs"]]
    
    # Existing indexes (keep for backward compatibility)
    await collection.create_index("url", unique=True, name="idx_jobs_url")
    await collection.create_index([("created_at", -1)], name="idx_jobs_created_at")
    await collection.create_index([("company", 1)], name="idx_jobs_company")
    await collection.create_index([("location", 1)], name="idx_jobs_location")
    await collection.create_index([("is_active", 1)], name="idx_jobs_is_active")
    
    # NEW: Company relationship indexes
    await collection.create_index("company_id", name="idx_jobs_company_id")
    await collection.create_index([("company_id", 1), ("created_at", -1)], name="idx_jobs_company_created")
    await collection.create_index([("company_id", 1), ("is_active", 1)], name="idx_jobs_company_active")
    
    # Search and filtering indexes
    await collection.create_index([("title", "text"), ("description", "text")], name="idx_jobs_text_search")
    await collection.create_index([("skills_required", 1)], name="idx_jobs_skills")
    await collection.create_index([("experience_level", 1)], name="idx_jobs_experience")
    await collection.create_index([("job_type", 1)], name="idx_jobs_type")
    await collection.create_index([("remote_allowed", 1)], name="idx_jobs_remote")
    
    # Compound indexes for common queries
    await collection.create_index([("is_active", 1), ("created_at", -1)], name="idx_jobs_active_created")
    await collection.create_index([("location", 1), ("is_active", 1)], name="idx_jobs_location_active")
    
    logger.info("✅ Created jobs collection indexes")


async def create_all_indexes():
    """Create all database indexes"""
    try:
        from .database import connect_to_mongo, get_database

        # Ensure database connection
        await connect_to_mongo()
        db = get_database()

        if db is None:
            raise ValueError("Database connection not established")

        logger.info("🔧 Creating database indexes...")

        # Create indexes for all collections
        await create_companies_indexes(db)
        await create_contacts_indexes(db)
        await create_jobs_indexes(db)

        logger.info("✅ All database indexes created successfully")

    except Exception as e:
        logger.error(f"❌ Failed to create database indexes: {e}")
        raise


async def drop_all_indexes():
    """Drop all custom indexes (for development/testing)"""
    try:
        db = await get_database()
        
        logger.info("🗑️ Dropping all custom indexes...")
        
        # Drop indexes for all collections (except _id)
        for collection_name in [COLLECTIONS["companies"], COLLECTIONS["contacts"], COLLECTIONS["jobs"]]:
            collection = db[collection_name]
            indexes = await collection.list_indexes().to_list(length=None)
            
            for index in indexes:
                index_name = index.get("name")
                if index_name and index_name != "_id_":  # Don't drop the default _id index
                    try:
                        await collection.drop_index(index_name)
                        logger.info(f"Dropped index: {collection_name}.{index_name}")
                    except Exception as e:
                        logger.warning(f"Failed to drop index {collection_name}.{index_name}: {e}")
        
        logger.info("✅ All custom indexes dropped successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to drop indexes: {e}")
        raise


async def list_all_indexes():
    """List all indexes for debugging"""
    try:
        db = await get_database()
        
        for collection_name in [COLLECTIONS["companies"], COLLECTIONS["contacts"], COLLECTIONS["jobs"]]:
            collection = db[collection_name]
            indexes = await collection.list_indexes().to_list(length=None)
            
            logger.info(f"\n📋 Indexes for {collection_name}:")
            for index in indexes:
                logger.info(f"  - {index.get('name')}: {index.get('key')}")
                
    except Exception as e:
        logger.error(f"❌ Failed to list indexes: {e}")


if __name__ == "__main__":
    # For testing - run this script directly to create indexes
    asyncio.run(create_all_indexes())
