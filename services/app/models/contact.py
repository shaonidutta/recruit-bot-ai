from pydantic import BaseModel, Field, EmailStr
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


class Contact(BaseModel):
    """Contact model for storing enriched contact data"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(..., description="Contact full name")
    email: EmailStr = Field(..., description="Contact email address")
    title: Optional[str] = Field(None, description="Job title/position")
    company_id: PyObjectId = Field(..., description="Reference to Company document")
    
    # Additional contact information
    phone: Optional[str] = Field(None, description="Phone number")
    linkedin_url: Optional[str] = Field(None, description="LinkedIn profile URL")
    department: Optional[str] = Field(None, description="Department/team")
    seniority: Optional[str] = Field(None, description="Seniority level (junior, senior, executive)")
    
    # External API IDs for deduplication
    apollo_id: Optional[str] = Field(None, description="Apollo.io person ID")
    # snov_id: Optional[str] = Field(None, description="Snov.io contact ID")  # Removed - not implemented
    
    # Metadata
    enrichment_source: str = Field(default="manual", description="Source of enrichment (apollo, manual)")
    confidence_score: Optional[float] = Field(None, description="Confidence score from enrichment API")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john.doe@google.com",
                "title": "Software Engineer",
                "company_id": "507f1f77bcf86cd799439011",
                "phone": "+1-555-123-4567",
                "linkedin_url": "https://linkedin.com/in/johndoe",
                "department": "Engineering",
                "seniority": "senior",
                "apollo_id": "apollo_person_123",
                "enrichment_source": "apollo",
                "confidence_score": 0.95
            }
        }


class ContactCreate(BaseModel):
    """Schema for creating a new contact"""
    name: str
    email: EmailStr
    title: Optional[str] = None
    company_id: str  # Will be converted to PyObjectId
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    department: Optional[str] = None
    seniority: Optional[str] = None
    apollo_id: Optional[str] = None
    snov_id: Optional[str] = None
    enrichment_source: str = "manual"
    confidence_score: Optional[float] = None


class ContactUpdate(BaseModel):
    """Schema for updating an existing contact"""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    title: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    department: Optional[str] = None
    seniority: Optional[str] = None
    apollo_id: Optional[str] = None
    snov_id: Optional[str] = None
    enrichment_source: Optional[str] = None
    confidence_score: Optional[float] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ContactResponse(BaseModel):
    """Schema for contact API responses"""
    id: str
    name: str
    email: str
    title: Optional[str] = None  # Make optional
    company_id: str
    phone: Optional[str] = None  # Make optional
    linkedin_url: Optional[str] = None  # Make optional
    department: Optional[str] = None  # Make optional
    seniority: Optional[str] = None  # Make optional
    apollo_id: Optional[str] = None  # Make optional
    snov_id: Optional[str] = None  # Make optional
    enrichment_source: str
    confidence_score: Optional[float] = None  # Make optional
    created_at: datetime
    updated_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439012",
                "name": "John Doe",
                "email": "john.doe@google.com",
                "title": "Software Engineer",
                "company_id": "507f1f77bcf86cd799439011",
                "phone": "+1-555-123-4567",
                "linkedin_url": "https://linkedin.com/in/johndoe",
                "department": "Engineering",
                "seniority": "senior",
                "apollo_id": "apollo_person_123",
                "snov_id": None,
                "enrichment_source": "apollo",
                "confidence_score": 0.95,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        }


class ContactWithCompany(ContactResponse):
    """Contact response with embedded company information"""
    company: Optional[dict] = Field(None, description="Company information")
    
    class Config:
        json_schema_extra = {
            "example": {
                **ContactResponse.Config.json_schema_extra["example"],
                "company": {
                    "id": "507f1f77bcf86cd799439011",
                    "name": "Google Inc.",
                    "domain": "google.com",
                    "industry": "Technology"
                }
            }
        }
