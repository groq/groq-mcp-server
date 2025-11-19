"""
Pydantic schemas for API request/response validation
"""

from .user import (
    UserRegister,
    UserLogin,
    Token,
    UserProfile,
    UserProfileUpdate,
    UserSkillCreate,
    UserSkillResponse,
    UserPreferenceUpdate,
    UserPreferenceResponse,
    UserDetailResponse
)

from .job import (
    JobResponse,
    JobSearchRequest,
    JobSearchResponse,
    JobApplicationCreate,
    JobApplicationResponse,
    SavedSearchCreate,
    SavedSearchResponse
)

from .client import (
    ClientResponse,
    ClientReviewResponse,
    ClientRedFlagResponse,
    CompanyResearchResponse,
    ClientVettingReport,
    ScamReportCreate,
    ScamReportResponse,
    ScamReportVote
)

__all__ = [
    # User schemas
    'UserRegister',
    'UserLogin',
    'Token',
    'UserProfile',
    'UserProfileUpdate',
    'UserSkillCreate',
    'UserSkillResponse',
    'UserPreferenceUpdate',
    'UserPreferenceResponse',
    'UserDetailResponse',
    # Job schemas
    'JobResponse',
    'JobSearchRequest',
    'JobSearchResponse',
    'JobApplicationCreate',
    'JobApplicationResponse',
    'SavedSearchCreate',
    'SavedSearchResponse',
    # Client schemas
    'ClientResponse',
    'ClientReviewResponse',
    'ClientRedFlagResponse',
    'CompanyResearchResponse',
    'ClientVettingReport',
    'ScamReportCreate',
    'ScamReportResponse',
    'ScamReportVote',
]
