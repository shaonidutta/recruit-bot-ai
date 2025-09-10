"""
Match Model
For storing job-candidate matches
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
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

class MatchBase(BaseModel):
    job_id: str
    candidate_id: str
    match_score: float = Field(..., ge=0.0, le=1.0)
    match_reasons: List[str] = []
    is_active: bool = True

class MatchCreate(MatchBase):
    pass

class MatchInDB(MatchBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class MatchResponse(MatchBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

class MatchService:
    """Match service for database operations"""
    
    @staticmethod
    def get_collection():
        """Get matches collection"""
        db = get_database()
        return db[COLLECTIONS.get("matches", "matches")]
    
    @classmethod
    async def create_match(cls, match_data: Dict[str, Any]) -> MatchInDB:
        """Create a new match"""
        collection = cls.get_collection()
        
        # Create match document
        match_dict = {
            "job_id": match_data.get("job_id"),
            "candidate_id": match_data.get("candidate_id"),
            "match_score": match_data.get("match_score", 0.0),
            "match_reasons": match_data.get("match_reasons", []),
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await collection.insert_one(match_dict)
        match_dict["_id"] = result.inserted_id
        
        return MatchInDB(**match_dict)
    
    @classmethod
    async def find_matches_for_job(cls, job_id: str) -> List[MatchInDB]:
        """Find all matches for a job"""
        collection = cls.get_collection()
        cursor = collection.find({"job_id": job_id, "is_active": True}).sort("match_score", -1)
        
        matches = []
        async for match_doc in cursor:
            matches.append(MatchInDB(**match_doc))
        
        return matches
    
    @classmethod
    async def find_matches_for_candidate(cls, candidate_id: str) -> List[MatchInDB]:
        """Find all matches for a candidate"""
        collection = cls.get_collection()
        cursor = collection.find({"candidate_id": candidate_id, "is_active": True}).sort("match_score", -1)
        
        matches = []
        async for match_doc in cursor:
            matches.append(MatchInDB(**match_doc))
        
        return matches

    @classmethod
    async def count_matches(cls, active_only: bool = True) -> int:
        """Count total matches"""
        collection = cls.get_collection()
        filter_query = {"is_active": True} if active_only else {}
        return await collection.count_documents(filter_query)
