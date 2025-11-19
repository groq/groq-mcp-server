"""
SQLAlchemy models for AI Freelance Search App
"""

from .user import User, UserSkill, UserPreference
from .platform import FreelancePlatform
from .client import Client, ClientReview, ClientRedFlag
from .job import Job, JobApplication
from .company import CompanyResearch
from .scam import ScamReport
from .search import SavedSearch
from .analytics import UserAnalytics, PlatformAnalytics

__all__ = [
    'User',
    'UserSkill',
    'UserPreference',
    'FreelancePlatform',
    'Client',
    'ClientReview',
    'ClientRedFlag',
    'Job',
    'JobApplication',
    'CompanyResearch',
    'ScamReport',
    'SavedSearch',
    'UserAnalytics',
    'PlatformAnalytics',
]
