"""
Job Model
Converted from backend/src/models/job.js
Extended with additional fields for comprehensive job data
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
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
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")
        return field_schema

class JobBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    company: str = Field(..., min_length=1, max_length=100)
    url: str = Field(..., min_length=1)  # Changed from HttpUrl to str for MongoDB compatibility
    description: Optional[str] = None
    location: Optional[str] = None
    source: Optional[str] = None  # linkedin, indeed, etc.
    requirements: Optional[List[str]] = []
    salary_range: Optional[str] = None
    job_type: Optional[str] = None  # full-time, part-time, contract, etc.
    experience_level: Optional[str] = None  # entry, mid, senior, etc.
    remote_allowed: Optional[bool] = False
    posted_date: Optional[datetime] = None
    is_active: bool = True

    # Additional fields for enrichment and parsing
    skills_required: Optional[List[str]] = []
    experience_years: Optional[int] = None
    company_id: Optional[PyObjectId] = None  # Reference to Company document (NEW)
    company_data: Optional[dict] = None  # Enriched company information (DEPRECATED - use company_id)
    parsed_data: Optional[dict] = None   # Parsed job description data
    via: Optional[str] = None            # Source platform (from scraping)
    raw_data: Optional[dict] = None      # Original scraped data
    processing_status: Optional[str] = "discovered"  # discovered, enriched, parsed, matched

class JobCreate(JobBase):
    pass

class JobUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    company: Optional[str] = Field(None, min_length=1, max_length=100)
    url: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    requirements: Optional[List[str]] = None
    salary_range: Optional[str] = None
    job_type: Optional[str] = None
    experience_level: Optional[str] = None
    remote_allowed: Optional[bool] = None
    is_active: Optional[bool] = None

    # Additional fields for enrichment and parsing
    skills_required: Optional[List[str]] = None
    experience_years: Optional[int] = None
    company_id: Optional[PyObjectId] = None  # Reference to Company document (NEW)
    company_data: Optional[dict] = None
    parsed_data: Optional[dict] = None
    via: Optional[str] = None
    raw_data: Optional[dict] = None
    processing_status: Optional[str] = None

class JobInDB(JobBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class JobResponse(JobBase):
    id: str
    scraped_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class JobService:
    """Job service for database operations"""
    
    @staticmethod
    def get_collection():
        """Get jobs collection"""
        db = get_database()
        return db[COLLECTIONS["jobs"]]
    
    @classmethod
    async def create_job(cls, job_data: JobCreate) -> JobInDB:
        """Create a new job"""
        collection = cls.get_collection()
        
        # Create job document
        job_dict = job_data.dict()
        job_dict.update({
            "scraped_at": datetime.utcnow(),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        })
        
        # Insert job
        result = await collection.insert_one(job_dict)
        job_dict["_id"] = result.inserted_id
        
        return JobInDB(**job_dict)
    
    @classmethod
    async def create_many_jobs(cls, jobs_data: List[JobCreate]) -> List[JobInDB]:
        """Create multiple jobs"""
        if not jobs_data:
            return []
        
        collection = cls.get_collection()
        
        # Prepare job documents
        job_docs = []
        for job_data in jobs_data:
            job_dict = job_data.dict()
            job_dict.update({
                "scraped_at": datetime.utcnow(),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
            job_docs.append(job_dict)
        
        # Insert jobs
        result = await collection.insert_many(job_docs)
        
        # Return created jobs
        created_jobs = []
        for i, job_dict in enumerate(job_docs):
            job_dict["_id"] = result.inserted_ids[i]
            created_jobs.append(JobInDB(**job_dict))
        
        return created_jobs
    
    @classmethod
    async def find_by_id(cls, job_id: str) -> Optional[JobInDB]:
        """Find job by ID"""
        collection = cls.get_collection()
        
        try:
            object_id = ObjectId(job_id)
            job_doc = await collection.find_one({"_id": object_id})
            
            if job_doc:
                return JobInDB(**job_doc)
        except Exception:
            pass
        
        return None
    
    @classmethod
    async def find_by_url(cls, url: str) -> Optional[JobInDB]:
        """Find job by URL (to avoid duplicates)"""
        collection = cls.get_collection()
        job_doc = await collection.find_one({"url": url})
        
        if job_doc:
            return JobInDB(**job_doc)
        return None
    
    @classmethod
    async def find_all(cls, skip: int = 0, limit: int = 100, active_only: bool = True) -> List[JobInDB]:
        """Find all jobs with pagination"""
        collection = cls.get_collection()
        
        query = {"is_active": True} if active_only else {}
        cursor = collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
        
        jobs = []
        async for job_doc in cursor:
            jobs.append(JobInDB(**job_doc))
        
        return jobs
    
    @classmethod
    async def update_job(cls, job_id: str, update_data: JobUpdate) -> Optional[JobInDB]:
        """Update job"""
        collection = cls.get_collection()
        
        try:
            object_id = ObjectId(job_id)
            
            # Prepare update data
            update_dict = {k: v for k, v in update_data.dict(exclude_unset=True).items() if v is not None}
            
            if update_dict:
                update_dict["updated_at"] = datetime.utcnow()
                
                await collection.update_one(
                    {"_id": object_id},
                    {"$set": update_dict}
                )
            
            return await cls.find_by_id(job_id)
        except Exception:
            return None
    
    @classmethod
    async def count_jobs(cls, active_only: bool = True) -> int:
        """Count total jobs"""
        collection = cls.get_collection()
        query = {"is_active": True} if active_only else {}
        return await collection.count_documents(query)
    
    @classmethod
    async def search_jobs(cls, query: str, skip: int = 0, limit: int = 100) -> List[JobInDB]:
        """Search jobs by title, company, or description"""
        collection = cls.get_collection()
        
        search_query = {
            "$and": [
                {"is_active": True},
                {
                    "$or": [
                        {"title": {"$regex": query, "$options": "i"}},
                        {"company": {"$regex": query, "$options": "i"}},
                        {"description": {"$regex": query, "$options": "i"}}
                    ]
                }
            ]
        }
        
        cursor = collection.find(search_query).sort("created_at", -1).skip(skip).limit(limit)
        
        jobs = []
        async for job_doc in cursor:
            jobs.append(JobInDB(**job_doc))
        
        return jobs
    
    @classmethod
    def to_response(cls, job: JobInDB) -> JobResponse:
        """Convert JobInDB to JobResponse"""
        return JobResponse(
            id=str(job.id),
            title=job.title,
            company=job.company,
            url=job.url,
            description=job.description,
            location=job.location,
            source=job.source,
            requirements=job.requirements,
            salary_range=job.salary_range,
            job_type=job.job_type,
            experience_level=job.experience_level,
            remote_allowed=job.remote_allowed,
            posted_date=job.posted_date,
            is_active=job.is_active,
            skills_required=job.skills_required,
            experience_years=job.experience_years,
            company_data=job.company_data,
            parsed_data=job.parsed_data,
            via=job.via,
            raw_data=job.raw_data,
            processing_status=job.processing_status,
            scraped_at=job.scraped_at,
            created_at=job.created_at,
            updated_at=job.updated_at
        )
