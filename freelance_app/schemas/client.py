"""
Client-related Pydantic schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class ClientBase(BaseModel):
    name: Optional[str] = None
    company_name: Optional[str] = None
    profile_url: Optional[str] = None
    location: Optional[str] = None
    timezone: Optional[str] = None


class ClientCreate(ClientBase):
    platform_id: int
    external_client_id: str
    account_created_date: Optional[datetime] = None
    verified_payment: bool = False
    total_jobs_posted: int = 0
    total_hires: int = 0
    total_spent: Decimal = Decimal(0)
    average_rating: Optional[Decimal] = None
    review_count: int = 0
    average_response_time: Optional[int] = None
    hire_rate: Optional[Decimal] = None
    avg_project_value: Optional[Decimal] = None
    repeat_hire_rate: Optional[Decimal] = None


class ClientResponse(ClientBase):
    id: int
    platform_id: int
    external_client_id: str
    account_created_date: Optional[datetime]
    verified_payment: bool
    total_jobs_posted: int
    total_hires: int
    total_spent: Decimal
    average_rating: Optional[Decimal]
    review_count: int
    average_response_time: Optional[int]
    hire_rate: Optional[Decimal]
    avg_project_value: Optional[Decimal]
    repeat_hire_rate: Optional[Decimal]
    last_active: Optional[datetime]
    trust_score: Optional[int]
    trust_score_updated_at: Optional[datetime]
    is_flagged: bool
    flag_reason: Optional[str]
    last_updated: datetime

    class Config:
        from_attributes = True


# Client Review
class ClientReviewCreate(BaseModel):
    client_id: int
    freelancer_name: Optional[str] = None
    rating: int = Field(..., ge=1, le=5)
    review_text: Optional[str] = None
    project_title: Optional[str] = None
    project_value: Optional[Decimal] = None
    review_date: Optional[datetime] = None


class ClientReviewResponse(BaseModel):
    id: int
    client_id: int
    freelancer_name: Optional[str]
    rating: int
    review_text: Optional[str]
    project_title: Optional[str]
    project_value: Optional[Decimal]
    review_date: Optional[datetime]
    sentiment_score: Optional[Decimal]
    key_themes: Optional[List[str]]
    created_at: datetime

    class Config:
        from_attributes = True


# Red Flag
class ClientRedFlagCreate(BaseModel):
    client_id: int
    flag_type: str
    severity: str = Field(..., pattern="^(low|medium|high|critical)$")
    description: Optional[str] = None


class ClientRedFlagResponse(BaseModel):
    id: int
    client_id: int
    flag_type: str
    severity: str
    description: Optional[str]
    detected_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


# Company Research
class CompanyResearchResponse(BaseModel):
    id: int
    client_id: int
    company_name: Optional[str]
    linkedin_url: Optional[str]
    linkedin_verified: bool
    linkedin_employee_count: Optional[int]
    website_url: Optional[str]
    website_verified: bool
    twitter_url: Optional[str]
    facebook_url: Optional[str]
    instagram_url: Optional[str]
    social_media_presence_score: Optional[int]
    business_registration_found: bool
    recent_news_count: int
    digital_footprint_score: Optional[int]
    research_data: Optional[dict]
    researched_at: datetime
    last_updated: datetime

    class Config:
        from_attributes = True


# Vetting Report
class ClientVettingReport(BaseModel):
    client: ClientResponse
    trust_score: int
    trust_score_breakdown: dict
    strengths: List[str]
    concerns: List[str]
    red_flags: List[ClientRedFlagResponse]
    reviews_summary: dict
    common_themes: List[str]
    company_research: Optional[CompanyResearchResponse]
    recommendation: str


# Scam Report
class ScamReportCreate(BaseModel):
    client_id: Optional[int] = None
    job_id: Optional[int] = None
    report_type: str = Field(..., pattern="^(scam|fake|non_payment|harassment|other)$")
    description: str = Field(..., min_length=10)
    evidence_urls: Optional[List[str]] = None


class ScamReportResponse(BaseModel):
    id: int
    client_id: Optional[int]
    reporter_user_id: Optional[int]
    job_id: Optional[int]
    report_type: str
    description: str
    evidence_urls: Optional[List[str]]
    status: str
    verified_by_admin: Optional[int]
    verified_at: Optional[datetime]
    created_at: datetime
    upvotes: int
    downvotes: int

    class Config:
        from_attributes = True


class ScamReportVote(BaseModel):
    vote_type: str = Field(..., pattern="^(upvote|downvote)$")
