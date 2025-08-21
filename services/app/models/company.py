from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from bson import ObjectId


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
    def __get_pydantic_json_schema__(cls, field_schema, handler):
        field_schema.update(type="string")
        return field_schema


class Company(BaseModel):
    """Company model for storing enriched company data"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(..., description="Company name")
    domain: Optional[str] = Field(None, description="Company domain (e.g., google.com)")
    website: Optional[str] = Field(None, description="Company website URL")
    industry: Optional[str] = Field(None, description="Company industry")
    size: Optional[str] = Field(None, description="Company size (e.g., '1000-5000 employees')")
    headquarters: Optional[str] = Field(None, description="Company headquarters location")
    description: Optional[str] = Field(None, description="Company description")
    
    # External API IDs for deduplication
    apollo_id: Optional[str] = Field(None, description="Apollo.io organization ID")
    
    # Metadata
    enrichment_source: str = Field(default="manual", description="Source of enrichment (apollo, manual, etc.)")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "name": "Google Inc.",
                "domain": "google.com",
                "website": "https://www.google.com",
                "industry": "Technology",
                "size": "10000+ employees",
                "headquarters": "Mountain View, CA, USA",
                "apollo_id": "apollo_123456",
                "enrichment_source": "apollo"
            }
        }


class CompanyCreate(BaseModel):
    """Schema for creating a new company"""
    name: str
    domain: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    size: Optional[str] = None
    headquarters: Optional[str] = None
    description: Optional[str] = None
    apollo_id: Optional[str] = None
    enrichment_source: str = "manual"


class CompanyUpdate(BaseModel):
    """Schema for updating an existing company"""
    name: Optional[str] = None
    domain: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    size: Optional[str] = None
    headquarters: Optional[str] = None
    description: Optional[str] = None
    apollo_id: Optional[str] = None
    enrichment_source: Optional[str] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class CompanyResponse(BaseModel):
    """Schema for company API responses"""
    id: str
    name: str
    domain: Optional[str]
    website: Optional[str]
    industry: Optional[str]
    size: Optional[str]
    headquarters: Optional[str]
    description: Optional[str]
    apollo_id: Optional[str]
    enrichment_source: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "name": "Google Inc.",
                "domain": "google.com",
                "website": "https://www.google.com",
                "industry": "Technology",
                "size": "10000+ employees",
                "headquarters": "Mountain View, CA, USA",
                "apollo_id": "apollo_123456",
                "enrichment_source": "apollo",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        }
