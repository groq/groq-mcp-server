"""
Jobs API routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime
import math

from models.base import get_db
from models.user import User
from models.job import Job, JobApplication
from models.search import SavedSearch
from models.client import Client
from schemas.job import (
    JobResponse,
    JobSearchRequest,
    JobSearchResponse,
    JobApplicationCreate,
    JobApplicationResponse,
    SavedSearchCreate,
    SavedSearchResponse
)
from utils.auth import get_current_user
from services.ai_service import AIService

router = APIRouter()


@router.get("", response_model=JobSearchResponse)
async def list_jobs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    skills: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    min_hourly_rate: Optional[float] = Query(None, ge=0),
    max_hourly_rate: Optional[float] = Query(None, ge=0),
    min_fixed_price: Optional[float] = Query(None, ge=0),
    max_fixed_price: Optional[float] = Query(None, ge=0),
    job_type: Optional[str] = Query(None),
    experience_level: Optional[str] = Query(None),
    min_trust_score: Optional[int] = Query(None, ge=0, le=100),
    is_active: bool = Query(True),
    db: Session = Depends(get_db)
):
    """
    List jobs with filters
    """
    # Build query
    query = db.query(Job).filter(Job.is_active == is_active)

    # Apply filters
    if skills:
        skill_list = [s.strip() for s in skills.split(',')]
        query = query.filter(Job.skills_required.overlap(skill_list))

    if category:
        query = query.filter(Job.category == category)

    if min_hourly_rate is not None:
        query = query.filter(Job.hourly_rate >= min_hourly_rate)

    if max_hourly_rate is not None:
        query = query.filter(Job.hourly_rate <= max_hourly_rate)

    if min_fixed_price is not None:
        query = query.filter(Job.fixed_price >= min_fixed_price)

    if max_fixed_price is not None:
        query = query.filter(Job.fixed_price <= max_fixed_price)

    if job_type:
        query = query.filter(Job.job_type == job_type)

    if experience_level:
        query = query.filter(Job.experience_level == experience_level)

    if min_trust_score is not None:
        query = query.join(Client).filter(Client.trust_score >= min_trust_score)

    # Order by posted date (newest first)
    query = query.order_by(Job.posted_date.desc())

    # Count total
    total = query.count()

    # Pagination
    offset = (page - 1) * page_size
    jobs = query.offset(offset).limit(page_size).all()

    return {
        "jobs": jobs,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": math.ceil(total / page_size) if total > 0 else 0
    }


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: int,
    db: Session = Depends(get_db)
):
    """
    Get job details by ID
    """
    job = db.query(Job).filter(Job.id == job_id).first()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    return job


@router.post("/search", response_model=JobSearchResponse)
async def ai_search_jobs(
    search_request: JobSearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    AI-powered natural language job search
    """
    # Build query
    query = db.query(Job).filter(Job.is_active == search_request.is_active)

    # If natural language query is provided, use AI to extract filters
    if search_request.query:
        # TODO: Implement AI-powered query parsing
        # For now, use simple text search
        query = query.filter(
            or_(
                Job.title.ilike(f"%{search_request.query}%"),
                Job.description.ilike(f"%{search_request.query}%")
            )
        )

    # Apply filters
    if search_request.skills:
        query = query.filter(Job.skills_required.overlap(search_request.skills))

    if search_request.categories:
        query = query.filter(Job.category.in_(search_request.categories))

    if search_request.job_type:
        query = query.filter(Job.job_type == search_request.job_type)

    if search_request.min_hourly_rate is not None:
        query = query.filter(Job.hourly_rate >= search_request.min_hourly_rate)

    if search_request.max_hourly_rate is not None:
        query = query.filter(Job.hourly_rate <= search_request.max_hourly_rate)

    if search_request.min_fixed_price is not None:
        query = query.filter(Job.fixed_price >= search_request.min_fixed_price)

    if search_request.max_fixed_price is not None:
        query = query.filter(Job.fixed_price <= search_request.max_fixed_price)

    if search_request.experience_level:
        query = query.filter(Job.experience_level == search_request.experience_level)

    if search_request.platform_ids:
        query = query.filter(Job.platform_id.in_(search_request.platform_ids))

    if search_request.location:
        query = query.filter(Job.location.ilike(f"%{search_request.location}%"))

    if search_request.min_trust_score is not None:
        query = query.join(Client).filter(Client.trust_score >= search_request.min_trust_score)

    if search_request.posted_after:
        query = query.filter(Job.posted_date >= search_request.posted_after)

    # Order by relevance (for now, use posted date)
    query = query.order_by(Job.posted_date.desc())

    # Count total
    total = query.count()

    # Pagination
    offset = (search_request.page - 1) * search_request.page_size
    jobs = query.offset(offset).limit(search_request.page_size).all()

    return {
        "jobs": jobs,
        "total": total,
        "page": search_request.page,
        "page_size": search_request.page_size,
        "total_pages": math.ceil(total / search_request.page_size) if total > 0 else 0
    }


@router.post("/{job_id}/apply", response_model=JobApplicationResponse)
async def apply_to_job(
    job_id: int,
    application_data: JobApplicationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Apply to a job
    """
    # Check if job exists
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    # Check if already applied
    existing_application = db.query(JobApplication).filter(
        JobApplication.user_id == current_user.id,
        JobApplication.job_id == job_id
    ).first()

    if existing_application:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already applied to this job"
        )

    # Create application
    application = JobApplication(
        user_id=current_user.id,
        job_id=job_id,
        notes=application_data.notes,
        status='applied'
    )

    db.add(application)
    db.commit()
    db.refresh(application)

    return application


@router.get("/applications/me", response_model=List[JobApplicationResponse])
async def get_my_applications(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's job applications
    """
    return current_user.applications


# Saved Searches
@router.get("/saved-searches/list", response_model=List[SavedSearchResponse])
async def list_saved_searches(
    current_user: User = Depends(get_current_user)
):
    """
    List user's saved searches
    """
    return current_user.saved_searches


@router.post("/saved-searches", response_model=SavedSearchResponse, status_code=status.HTTP_201_CREATED)
async def create_saved_search(
    search_data: SavedSearchCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new saved search
    """
    saved_search = SavedSearch(
        user_id=current_user.id,
        name=search_data.name,
        search_query=search_data.search_query,
        filters=search_data.filters,
        alert_enabled=search_data.alert_enabled
    )

    db.add(saved_search)
    db.commit()
    db.refresh(saved_search)

    return saved_search


@router.delete("/saved-searches/{search_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_saved_search(
    search_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a saved search
    """
    saved_search = db.query(SavedSearch).filter(
        SavedSearch.id == search_id,
        SavedSearch.user_id == current_user.id
    ).first()

    if not saved_search:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved search not found"
        )

    db.delete(saved_search)
    db.commit()

    return None
