"""Candidate Routes
RESTful API endpoints for candidate management
Provides CRUD operations for candidate profiles and search functionality
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from ..models.candidate import (
    CandidateService, 
    CandidateResponse, 
    CandidateCreate, 
    CandidateUpdate
)
from ..models.user import UserInDB
from ..auth.dependencies import get_current_user
from ..utils.response_helper import send_success, send_error, send_not_found_error

router = APIRouter()


@router.get("/candidates")
async def get_candidates(
    skip: int = Query(0, ge=0, description="Number of candidates to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of candidates to return"),
    search: Optional[str] = Query(None, description="Search by name, role, or company"),
    skills: Optional[str] = Query(None, description="Filter by skills (comma-separated)"),
    active_only: bool = Query(True, description="Return only active candidates"),
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get all candidates with optional filtering and pagination
    GET /api/v1/candidates
    """
    try:
        if search or skills:
            # Parse skills if provided
            skills_list = [s.strip() for s in skills.split(",")] if skills else None
            candidates = await CandidateService.search_candidates(
                query=search or "",
                skills=skills_list,
                skip=skip,
                limit=limit
            )
        else:
            candidates = await CandidateService.find_all(
                skip=skip,
                limit=limit,
                active_only=active_only
            )
        
        # Convert to response format
        candidate_responses = [
            CandidateService.to_response(candidate).dict() 
            for candidate in candidates
        ]
        
        return send_success(
            data={
                "candidates": candidate_responses,
                "total": len(candidate_responses),
                "skip": skip,
                "limit": limit
            },
            message=f"Retrieved {len(candidate_responses)} candidates"
        )
    except Exception as e:
        return send_error(f"Failed to retrieve candidates: {str(e)}", 500)


@router.get("/candidates/{candidate_id}")
async def get_candidate(
    candidate_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get specific candidate by ID
    GET /api/v1/candidates/{candidate_id}
    """
    try:
        candidate = await CandidateService.find_by_id(candidate_id)
        if not candidate:
            return send_not_found_error("Candidate not found")
        
        return send_success(
            data={"candidate": CandidateService.to_response(candidate).dict()},
            message="Candidate retrieved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        return send_error(f"Failed to retrieve candidate: {str(e)}", 500)


@router.post("/candidates")
async def create_candidate(
    candidate_data: CandidateCreate,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Create a new candidate
    POST /api/v1/candidates
    """
    try:
        # Check if candidate with email already exists
        existing_candidate = await CandidateService.find_by_email(candidate_data.email)
        if existing_candidate:
            return send_error("Candidate with this email already exists", 400)
        
        # Create new candidate
        new_candidate = await CandidateService.create_candidate(candidate_data)
        
        return send_success(
            data={"candidate": CandidateService.to_response(new_candidate).dict()},
            message="Candidate created successfully",
            status_code=201
        )
    except Exception as e:
        return send_error(f"Failed to create candidate: {str(e)}", 500)


@router.put("/candidates/{candidate_id}")
async def update_candidate(
    candidate_id: str,
    candidate_data: CandidateUpdate,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Update an existing candidate
    PUT /api/v1/candidates/{candidate_id}
    """
    try:
        # Check if candidate exists
        existing_candidate = await CandidateService.find_by_id(candidate_id)
        if not existing_candidate:
            return send_not_found_error("Candidate not found")
        
        # Check if email is being updated and if it conflicts
        if candidate_data.email and candidate_data.email != existing_candidate.email:
            email_conflict = await CandidateService.find_by_email(candidate_data.email)
            if email_conflict:
                return send_error("Another candidate with this email already exists", 400)
        
        # Update candidate
        updated_candidate = await CandidateService.update_candidate(candidate_id, candidate_data)
        if not updated_candidate:
            return send_error("Failed to update candidate", 500)
        
        return send_success(
            data={"candidate": CandidateService.to_response(updated_candidate).dict()},
            message="Candidate updated successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        return send_error(f"Failed to update candidate: {str(e)}", 500)


@router.delete("/candidates/{candidate_id}")
async def delete_candidate(
    candidate_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Soft delete a candidate (set is_active to False)
    DELETE /api/v1/candidates/{candidate_id}
    """
    try:
        # Check if candidate exists
        existing_candidate = await CandidateService.find_by_id(candidate_id)
        if not existing_candidate:
            return send_not_found_error("Candidate not found")
        
        # Soft delete by setting is_active to False
        update_data = CandidateUpdate(is_active=False)
        updated_candidate = await CandidateService.update_candidate(candidate_id, update_data)
        
        if not updated_candidate:
            return send_error("Failed to delete candidate", 500)
        
        return send_success(
            data={"candidate_id": candidate_id},
            message="Candidate deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        return send_error(f"Failed to delete candidate: {str(e)}", 500)


@router.get("/candidates/search")
async def search_candidates(
    q: str = Query(..., description="Search query"),
    skills: Optional[str] = Query(None, description="Skills filter (comma-separated)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Search candidates by name, role, company, or skills
    GET /api/v1/candidates/search?q=python&skills=react,node
    """
    try:
        # Parse skills if provided
        skills_list = [s.strip() for s in skills.split(",")] if skills else None
        
        candidates = await CandidateService.search_candidates(
            query=q,
            skills=skills_list,
            skip=skip,
            limit=limit
        )
        
        # Convert to response format
        candidate_responses = [
            CandidateService.to_response(candidate).dict() 
            for candidate in candidates
        ]
        
        return send_success(
            data={
                "candidates": candidate_responses,
                "total": len(candidate_responses),
                "query": q,
                "skills_filter": skills_list,
                "skip": skip,
                "limit": limit
            },
            message=f"Found {len(candidate_responses)} candidates matching search criteria"
        )
    except Exception as e:
        return send_error(f"Search failed: {str(e)}", 500)


@router.get("/candidates/export")
async def export_candidates(
    format: str = Query("json", regex="^(json|csv)$", description="Export format"),
    active_only: bool = Query(True, description="Export only active candidates"),
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Export candidates data
    GET /api/v1/candidates/export?format=json
    """
    try:
        candidates = await CandidateService.find_all(
            skip=0,
            limit=10000,  # Large limit for export
            active_only=active_only
        )
        
        if format == "json":
            candidate_responses = [
                CandidateService.to_response(candidate).dict() 
                for candidate in candidates
            ]
            
            return send_success(
                data={
                    "candidates": candidate_responses,
                    "total": len(candidate_responses),
                    "export_format": "json",
                    "active_only": active_only
                },
                message=f"Exported {len(candidate_responses)} candidates"
            )
        
        # CSV format would require additional implementation
        # For now, return JSON format
        return send_error("CSV export not yet implemented", 501)
        
    except Exception as e:
        return send_error(f"Export failed: {str(e)}", 500)


@router.get("/candidates/stats")
async def get_candidate_stats(
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get candidate statistics
    GET /api/v1/candidates/stats
    """
    try:
        # Get all candidates for stats
        all_candidates = await CandidateService.find_all(skip=0, limit=10000, active_only=False)
        active_candidates = [c for c in all_candidates if c.is_active]
        
        # Calculate basic stats
        total_candidates = len(all_candidates)
        active_count = len(active_candidates)
        inactive_count = total_candidates - active_count
        
        # Skills distribution
        skills_count = {}
        for candidate in active_candidates:
            for skill in candidate.skills:
                skills_count[skill] = skills_count.get(skill, 0) + 1
        
        # Top skills (top 10)
        top_skills = sorted(skills_count.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Experience distribution
        experience_ranges = {
            "0-2 years": 0,
            "3-5 years": 0,
            "6-10 years": 0,
            "10+ years": 0,
            "Not specified": 0
        }
        
        for candidate in active_candidates:
            exp = candidate.experience_years
            if exp is None:
                experience_ranges["Not specified"] += 1
            elif exp <= 2:
                experience_ranges["0-2 years"] += 1
            elif exp <= 5:
                experience_ranges["3-5 years"] += 1
            elif exp <= 10:
                experience_ranges["6-10 years"] += 1
            else:
                experience_ranges["10+ years"] += 1
        
        return send_success(
            data={
                "total_candidates": total_candidates,
                "active_candidates": active_count,
                "inactive_candidates": inactive_count,
                "top_skills": top_skills,
                "experience_distribution": experience_ranges
            },
            message="Candidate statistics retrieved successfully"
        )
    except Exception as e:
        return send_error(f"Failed to get candidate stats: {str(e)}", 500)