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
    def __get_pydantic_json_schema__(cls, field_schema, handler):
        field_schema.update(type="string")
        return field_schema

class JobBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    company: str = Field(..., min_length=1, max_length=100)
    url: Optional[str] = Field(None)  # Optional URL field for MongoDB compatibility
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
    company_id: Optional[str] = None  # Reference to Company document (NEW)
    company_data: Optional[dict] = None  # Enriched company information (DEPRECATED - use company_id)
    parsed_data: Optional[dict] = None   # Parsed job data
    via: Optional[str] = None            # Source platform (from scraping)
    raw_data: Optional[dict] = None      # Original scraped data
    processing_status: Optional[str] = "discovered"  # discovered, enriched, parsed, matched
    workflow_id: Optional[str] = None    # ID of the workflow run that discovered this job

    # NEW: Enhanced salary fields
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None
    salary_type: Optional[str] = None  # "annual", "hourly", "contract"
    currency: Optional[str] = "USD"
    equity_mentioned: Optional[bool] = False
    benefits_mentioned: Optional[bool] = False

    # NEW: Enhanced skills fields
    technical_skills: Optional[List[str]] = []
    frameworks: Optional[List[str]] = []
    databases: Optional[List[str]] = []
    cloud_platforms: Optional[List[str]] = []
    tools: Optional[List[str]] = []
    methodologies: Optional[List[str]] = []
    soft_skills: Optional[List[str]] = []
    experience_years_required: Optional[int] = None
    education_requirements: Optional[List[str]] = []

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
    company_id: Optional[str] = None  # Reference to Company document (NEW)
    company_data: Optional[dict] = None
    parsed_data: Optional[dict] = None  # Parsed job data
    via: Optional[str] = None
    raw_data: Optional[dict] = None
    processing_status: Optional[str] = None
    workflow_id: Optional[str] = None

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
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

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
                # Convert ObjectId fields to strings for Pydantic validation
                if job_doc.get('company_id') and isinstance(job_doc['company_id'], ObjectId):
                    job_doc['company_id'] = str(job_doc['company_id'])

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
            # Convert ObjectId fields to strings for Pydantic validation
            if job_doc.get('company_id') and isinstance(job_doc['company_id'], ObjectId):
                job_doc['company_id'] = str(job_doc['company_id'])

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
            # Convert ObjectId fields to strings for Pydantic validation
            if job_doc.get('company_id') and isinstance(job_doc['company_id'], ObjectId):
                job_doc['company_id'] = str(job_doc['company_id'])

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
    async def find_by_workflow_id(cls, workflow_id: str, skip: int = 0, limit: int = 100) -> List[JobInDB]:
        """Find jobs by workflow_id (recent jobs from specific workflow run)"""
        collection = cls.get_collection()

        query = {"workflow_id": workflow_id, "is_active": True}
        cursor = collection.find(query).sort("created_at", -1).skip(skip).limit(limit)

        jobs = []
        async for job_doc in cursor:
            # Convert ObjectId fields to strings for Pydantic validation
            if job_doc.get('company_id') and isinstance(job_doc['company_id'], ObjectId):
                job_doc['company_id'] = str(job_doc['company_id'])

            jobs.append(JobInDB(**job_doc))

        return jobs

    @classmethod
    async def get_latest_workflow_id(cls) -> Optional[str]:
        """Get the most recent workflow_id"""
        collection = cls.get_collection()

        # Find the most recent job with a workflow_id
        cursor = collection.find(
            {"workflow_id": {"$ne": None}},
            {"workflow_id": 1}
        ).sort("created_at", -1).limit(1)

        async for doc in cursor:
            return doc.get("workflow_id")

        return None

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
            # Convert ObjectId fields to strings for Pydantic validation
            if job_doc.get('company_id') and isinstance(job_doc['company_id'], ObjectId):
                job_doc['company_id'] = str(job_doc['company_id'])

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
            workflow_id=job.workflow_id,
            scraped_at=job.scraped_at,
            created_at=job.created_at,
            updated_at=job.updated_at
        )

    @classmethod
    async def find_duplicate_job(cls, title: str, company: str, url: str = None) -> Optional[JobInDB]:
        """
        Check if a job already exists based on title, company, and optionally URL
        Returns the existing job if found, None otherwise
        """
        collection = cls.get_collection()

        try:
            # Create query to find potential duplicates
            query = {
                "title": {"$regex": f"^{title.strip()}$", "$options": "i"},  # Case-insensitive exact match
                "company": {"$regex": f"^{company.strip()}$", "$options": "i"},  # Case-insensitive exact match
                "is_active": True  # Only check active jobs
            }

            # If URL is provided, include it in the query
            if url and url.strip():
                query["url"] = url.strip()

            # Find the most recent matching job
            job_doc = await collection.find_one(query, sort=[("created_at", -1)])

            if job_doc:
                # Convert ObjectId fields to strings for Pydantic validation
                if job_doc.get('company_id') and isinstance(job_doc['company_id'], ObjectId):
                    job_doc['company_id'] = str(job_doc['company_id'])

                return JobInDB(**job_doc)

            return None

        except Exception as e:
            # Log error but don't fail the workflow
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error checking for duplicate job: {e}")
            return None

    @classmethod
    async def create_job_with_deduplication(cls, job_data: JobCreate) -> tuple[JobInDB, bool]:
        """
        Create a new job with deduplication check
        Returns (job, is_new) where is_new indicates if this is a newly created job
        """
        # Check for existing job
        existing_job = await cls.find_duplicate_job(
            title=job_data.title,
            company=job_data.company,
            url=job_data.url
        )

        if existing_job:
            # Job already exists, return existing job
            return existing_job, False

        # Job doesn't exist, create new one
        new_job = await cls.create_job(job_data)
        return new_job, True
