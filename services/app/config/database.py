"""
Database configuration and connection management
Converted from backend/src/config/database.js
"""
import os
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure
import logging

logger = logging.getLogger(__name__)

class Database:
    client: Optional[AsyncIOMotorClient] = None
    database: Optional[AsyncIOMotorDatabase] = None

db = Database()

async def connect_to_mongo():
    """Connect to MongoDB database"""
    try:
        # Get MongoDB URI from environment variables
        mongo_uri = os.getenv("MONGODB_URI_TEST") if os.getenv("NODE_ENV") == "test" else os.getenv("MONGODB_URI")

        if not mongo_uri:
            logger.warning("⚠️ MongoDB URI is not defined - running without database")
            return

        logger.info("🔄 Connecting to MongoDB...")

        # Hide credentials in logs for security
        safe_uri = mongo_uri.replace(mongo_uri.split("@")[0].split("//")[1], "***:***") if "@" in mongo_uri else mongo_uri
        logger.info(f" Database URI: {safe_uri}")

        # Connect to MongoDB with Motor AsyncIOMotorClient - Optimized for Render
        db.client = AsyncIOMotorClient(
            mongo_uri,
            maxPoolSize=5,  # Reduced pool size for free tier
            serverSelectionTimeoutMS=1000,  # Very fast timeout for Render
            socketTimeoutMS=5000,  # Quick socket timeout
            connectTimeoutMS=1000,  # Quick connection timeout
        )

        # Test the connection with a simple ping
        await db.client.admin.command('ping')

        # Extract database name from URI or use default
        # For MongoDB Atlas URIs without explicit database name, use default
        if "/" in mongo_uri and not mongo_uri.endswith("/"):
            db_name = mongo_uri.split("/")[-1].split("?")[0]
            if not db_name:  # If empty after splitting
                db_name = "ai_recruitment"
        else:
            db_name = "ai_recruitment"

        db.database = db.client[db_name]

        logger.info(f" MongoDB Connected successfully!")
        logger.info(f" Database Name: {db_name}")

    except ConnectionFailure as e:
        logger.warning(f"⚠️ Database connection failed: {e}")
        logger.warning("⚠️ Running without database connection")
        db.client = None
        db.database = None
    except Exception as e:
        logger.warning(f"⚠️ Database connection failed: {e}")
        logger.warning("⚠️ Running without database connection")
        db.client = None
        db.database = None

async def close_mongo_connection():
    """Close MongoDB connection"""
    if db.client:
        db.client.close()
        logger.info("🔴 MongoDB connection closed")

def get_database():
    """Get database instance"""
    if db.database is None:
        logger.warning("⚠️ Database is not connected - returning None")
    return db.database

def is_connected() -> bool:
    """Check if database is connected"""
    return db.client is not None and db.database is not None

async def get_connection_status() -> str:
    """Get connection status"""
    if db.client is None:
        return "disconnected"
    try:
        # This will raise an exception if not connected
        await db.client.server_info()
        return "connected"
    except:
        return "disconnected"

def ensure_database_connection():
    """Ensure database connection is available, raise exception if not"""
    if db.database is None:
        raise ConnectionError("Database connection is not available. Please check your MongoDB connection.")
    return db.database
