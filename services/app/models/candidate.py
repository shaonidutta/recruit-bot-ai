"""
Candidate Model
For storing candidate profiles and matching with jobs
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, EmailStr
from bson import ObjectId
from ..config.database import get_database
from ..config.constants import COLLECTIONS

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

class CandidateBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    email: EmailStr
    phone: Optional[str] = None
    location: Optional[str] = None
    skills: List[str] = []
    experience_years: Optional[int] = None
    current_role: Optional[str] = None
    current_company: Optional[str] = None
    education: Optional[str] = None
    resume_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    salary_expectation: Optional[str] = None
    availability: Optional[str] = None  # immediate, 2weeks, 1month, etc.
    remote_preference: Optional[bool] = None
    is_active: bool = True

class CandidateCreate(CandidateBase):
    pass

class CandidateUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    skills: Optional[List[str]] = None
    experience_years: Optional[int] = None
    current_role: Optional[str] = None
    current_company: Optional[str] = None
    education: Optional[str] = None
    resume_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    salary_expectation: Optional[str] = None
    availability: Optional[str] = None
    remote_preference: Optional[bool] = None
    is_active: Optional[bool] = None

class CandidateInDB(CandidateBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class CandidateResponse(CandidateBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class JobMatch(BaseModel):
    """Model for job-candidate matching results"""
    candidate_id: str
    job_id: str
    candidate_name: str
    job_title: str
    company_name: str
    overall_score: float
    skill_match: float
    experience_match: float
    match_details: Optional[dict] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CandidateService:
    """Candidate service for database operations"""
    
    @staticmethod
    def get_collection():
        """Get candidates collection"""
        db = get_database()
        return db[COLLECTIONS.get("candidates", "candidates")]
    
    @classmethod
    async def create_candidate(cls, candidate_data: CandidateCreate) -> CandidateInDB:
        """Create a new candidate"""
        collection = cls.get_collection()
        
        # Create candidate document
        candidate_dict = candidate_data.dict()
        candidate_dict.update({
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        })
        
        # Insert candidate
        result = await collection.insert_one(candidate_dict)
        candidate_dict["_id"] = result.inserted_id
        
        return CandidateInDB(**candidate_dict)
    
    @classmethod
    async def find_by_id(cls, candidate_id: str) -> Optional[CandidateInDB]:
        """Find candidate by ID"""
        collection = cls.get_collection()
        
        try:
            object_id = ObjectId(candidate_id)
            candidate_doc = await collection.find_one({"_id": object_id})
            
            if candidate_doc:
                return CandidateInDB(**candidate_doc)
        except Exception:
            pass
        
        return None
    
    @classmethod
    async def find_by_email(cls, email: str) -> Optional[CandidateInDB]:
        """Find candidate by email"""
        collection = cls.get_collection()
        candidate_doc = await collection.find_one({"email": email})
        
        if candidate_doc:
            return CandidateInDB(**candidate_doc)
        return None
    
    @classmethod
    async def find_all(cls, skip: int = 0, limit: int = 100, active_only: bool = True) -> List[CandidateInDB]:
        """Find all candidates with pagination"""
        collection = cls.get_collection()

        query = {"is_active": True} if active_only else {}
        cursor = collection.find(query).sort("created_at", -1).skip(skip).limit(limit)

        candidates = []
        async for candidate_doc in cursor:
            candidates.append(CandidateInDB(**candidate_doc))

        return candidates

    @classmethod
    async def get_all_candidates(cls) -> List[Dict[str, Any]]:
        """Get all candidates as dictionaries for matching"""
        candidates = await cls.find_all(limit=1000)  # Get more candidates for matching
        return [
            {
                "id": str(candidate.id),
                "name": f"{candidate.first_name} {candidate.last_name}",
                "email": candidate.email,
                "skills": candidate.skills,
                "experience_years": candidate.experience_years or 0,
                "current_role": candidate.current_role,
                "location": candidate.location
            }
            for candidate in candidates
        ]
    
    @classmethod
    async def update_candidate(cls, candidate_id: str, update_data: CandidateUpdate) -> Optional[CandidateInDB]:
        """Update candidate"""
        collection = cls.get_collection()
        
        try:
            object_id = ObjectId(candidate_id)
            
            # Prepare update data
            update_dict = {k: v for k, v in update_data.dict(exclude_unset=True).items() if v is not None}
            
            if update_dict:
                update_dict["updated_at"] = datetime.utcnow()
                
                await collection.update_one(
                    {"_id": object_id},
                    {"$set": update_dict}
                )
            
            return await cls.find_by_id(candidate_id)
        except Exception:
            return None
    
    @classmethod
    async def search_candidates(cls, query: str, skills: List[str] = None, skip: int = 0, limit: int = 100) -> List[CandidateInDB]:
        """Search candidates by name, skills, or role"""
        collection = cls.get_collection()
        
        search_conditions = [{"is_active": True}]
        
        if query:
            search_conditions.append({
                "$or": [
                    {"first_name": {"$regex": query, "$options": "i"}},
                    {"last_name": {"$regex": query, "$options": "i"}},
                    {"current_role": {"$regex": query, "$options": "i"}},
                    {"current_company": {"$regex": query, "$options": "i"}}
                ]
            })
        
        if skills:
            search_conditions.append({
                "skills": {"$in": [skill.lower() for skill in skills]}
            })
        
        search_query = {"$and": search_conditions}
        cursor = collection.find(search_query).sort("created_at", -1).skip(skip).limit(limit)
        
        candidates = []
        async for candidate_doc in cursor:
            candidates.append(CandidateInDB(**candidate_doc))
        
        return candidates
    
    @classmethod
    def to_response(cls, candidate: CandidateInDB) -> CandidateResponse:
        """Convert CandidateInDB to CandidateResponse"""
        return CandidateResponse(
            id=str(candidate.id),
            first_name=candidate.first_name,
            last_name=candidate.last_name,
            email=candidate.email,
            phone=candidate.phone,
            location=candidate.location,
            skills=candidate.skills,
            experience_years=candidate.experience_years,
            current_role=candidate.current_role,
            current_company=candidate.current_company,
            education=candidate.education,
            resume_url=candidate.resume_url,
            linkedin_url=candidate.linkedin_url,
            github_url=candidate.github_url,
            portfolio_url=candidate.portfolio_url,
            salary_expectation=candidate.salary_expectation,
            availability=candidate.availability,
            remote_preference=candidate.remote_preference,
            is_active=candidate.is_active,
            created_at=candidate.created_at,
            updated_at=candidate.updated_at
        )
