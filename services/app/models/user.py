"""
User Model
Converted from backend/src/models/User.js
Pydantic models with Motor async MongoDB driver
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from bson import ObjectId
from ..config.database import get_database
from ..config.constants import COLLECTIONS
from ..auth.jwt_handler import hash_password, verify_password

class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        from pydantic_core import core_schema
        return core_schema.no_info_plain_validator_function(cls.validate)

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")
        return field_schema

class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None

class UserInDB(UserBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class UserResponse(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserProfile(BaseModel):
    id: str
    name: str
    email: str
    created_at: datetime
    updated_at: datetime

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class UserService:
    """User service for database operations"""
    
    @staticmethod
    def get_collection():
        """Get users collection"""
        db = get_database()
        return db[COLLECTIONS["users"]]
    
    @classmethod
    async def create_user(cls, user_data: UserCreate) -> UserInDB:
        """Create a new user"""
        collection = cls.get_collection()
        
        # Check if user already exists
        existing_user = await collection.find_one({"email": user_data.email})
        if existing_user:
            raise ValueError("User with this email already exists")
        
        # Hash password
        hashed_password = hash_password(user_data.password)
        
        # Create user document
        user_dict = {
            "name": user_data.name.strip(),
            "email": user_data.email.lower(),
            "password": hashed_password,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Insert user
        result = await collection.insert_one(user_dict)
        user_dict["_id"] = result.inserted_id
        
        return UserInDB(**user_dict)
    
    @classmethod
    async def find_by_email(cls, email: str) -> Optional[UserInDB]:
        """Find user by email"""
        collection = cls.get_collection()
        user_doc = await collection.find_one({"email": email.lower()})
        
        if user_doc:
            return UserInDB(**user_doc)
        return None
    
    @classmethod
    async def find_by_email_with_password(cls, email: str) -> Optional[UserInDB]:
        """Find user by email including password field"""
        collection = cls.get_collection()
        user_doc = await collection.find_one({"email": email.lower()})
        
        if user_doc:
            return UserInDB(**user_doc)
        return None
    
    @classmethod
    async def find_by_id(cls, user_id: str) -> Optional[UserInDB]:
        """Find user by ID"""
        collection = cls.get_collection()
        
        try:
            object_id = ObjectId(user_id)
            user_doc = await collection.find_one({"_id": object_id})
            
            if user_doc:
                return UserInDB(**user_doc)
        except Exception:
            pass
        
        return None
    
    @classmethod
    async def update_user(cls, user_id: str, update_data: UserUpdate) -> Optional[UserInDB]:
        """Update user"""
        collection = cls.get_collection()
        
        try:
            object_id = ObjectId(user_id)
            
            # Prepare update data
            update_dict = {}
            if update_data.name is not None:
                update_dict["name"] = update_data.name.strip()
            if update_data.email is not None:
                update_dict["email"] = update_data.email.lower()
            
            if update_dict:
                update_dict["updated_at"] = datetime.utcnow()
                
                await collection.update_one(
                    {"_id": object_id},
                    {"$set": update_dict}
                )
            
            return await cls.find_by_id(user_id)
        except Exception:
            return None
    
    @classmethod
    async def count_users(cls) -> int:
        """Count total users"""
        collection = cls.get_collection()
        return await collection.count_documents({})
    
    @classmethod
    def verify_password(cls, user: UserInDB, password: str) -> bool:
        """Verify user password"""
        return verify_password(password, user.password)
    
    @classmethod
    def to_response(cls, user: UserInDB) -> UserResponse:
        """Convert UserInDB to UserResponse"""
        return UserResponse(
            id=str(user.id),
            name=user.name,
            email=user.email,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
    
    @classmethod
    def to_profile(cls, user: UserInDB) -> UserProfile:
        """Convert UserInDB to UserProfile"""
        return UserProfile(
            id=str(user.id),
            name=user.name,
            email=user.email,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
