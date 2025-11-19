"""
Job-related Pydantic schemas
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime


class JobBase(BaseModel):
    title: str
    description: str
    category: Optional[str] = None
    subcategory: Optional[str] = None
    skills_required: Optional[List[str]] = None
    job_type: Optional[str] = Field(None, pattern="^(hourly|fixed|both)$")
    budget_min: Optional[float] = Field(None, ge=0)
    budget_max: Optional[float] = Field(None, ge=0)
    hourly_rate: Optional[float] = Field(None, ge=0)
    fixed_price: Optional[float] = Field(None, ge=0)
    duration: Optional[str] = None
    experience_level: Optional[str] = Field(None, pattern="^(entry|intermediate|expert|any)$")
    location: Optional[str] = None
    timezone: Optional[str] = None


class JobCreate(JobBase):
    platform_id: int
    external_job_id: str
    client_id: Optional[int] = None
    url: str
    posted_date: Optional[datetime] = None
    deadline: Optional[datetime] = None
    applicants_count: Optional[int] = 0


class JobResponse(JobBase):
    id: int
    platform_id: int
    external_job_id: str
    client_id: Optional[int]
    url: str
    posted_date: Optional[datetime]
    deadline: Optional[datetime]
    applicants_count: int
    is_active: bool
    scraped_at: datetime
    last_updated: datetime
    ai_summary: Optional[str]

    class Config:
        from_attributes = True


class JobSearchRequest(BaseModel):
    query: Optional[str] = None
    skills: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    job_type: Optional[str] = Field(None, pattern="^(hourly|fixed|both)$")
    min_hourly_rate: Optional[float] = Field(None, ge=0)
    max_hourly_rate: Optional[float] = Field(None, ge=0)
    min_fixed_price: Optional[float] = Field(None, ge=0)
    max_fixed_price: Optional[float] = Field(None, ge=0)
    experience_level: Optional[str] = Field(None, pattern="^(entry|intermediate|expert|any)$")
    platform_ids: Optional[List[int]] = None
    location: Optional[str] = None
    min_trust_score: Optional[int] = Field(None, ge=0, le=100)
    posted_after: Optional[datetime] = None
    is_active: Optional[bool] = True
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


class JobSearchResponse(BaseModel):
    jobs: List[JobResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class JobApplicationCreate(BaseModel):
    job_id: int
    notes: Optional[str] = None


class JobApplicationResponse(BaseModel):
    id: int
    user_id: int
    job_id: int
    applied_at: datetime
    status: str
    notes: Optional[str]

    class Config:
        from_attributes = True


class SavedSearchCreate(BaseModel):
    name: str = Field(..., max_length=255)
    search_query: Optional[str] = None
    filters: Optional[dict] = None
    alert_enabled: bool = True


class SavedSearchResponse(BaseModel):
    id: int
    user_id: int
    name: str
    search_query: Optional[str]
    filters: Optional[dict]
    alert_enabled: bool
    created_at: datetime
    last_triggered: Optional[datetime]

    class Config:
        from_attributes = True
