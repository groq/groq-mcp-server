"""
User-related Pydantic schemas for API request/response validation
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from datetime import datetime


# User Registration
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    full_name: Optional[str] = Field(None, max_length=255)

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        return v


# User Login
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# Token Response
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# User Profile Response
class UserProfile(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    profile_picture_url: Optional[str]
    subscription_tier: str
    created_at: datetime
    last_login: Optional[datetime]
    email_verified: bool

    class Config:
        from_attributes = True


# User Profile Update
class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = Field(None, max_length=255)
    profile_picture_url: Optional[str] = None


# User Skill
class UserSkillCreate(BaseModel):
    skill_name: str = Field(..., max_length=255)
    proficiency_level: int = Field(..., ge=1, le=5)


class UserSkillResponse(BaseModel):
    id: int
    skill_name: str
    proficiency_level: int
    created_at: datetime

    class Config:
        from_attributes = True


# User Preferences
class UserPreferenceUpdate(BaseModel):
    min_hourly_rate: Optional[float] = Field(None, ge=0)
    max_hourly_rate: Optional[float] = Field(None, ge=0)
    min_fixed_price: Optional[float] = Field(None, ge=0)
    preferred_project_duration: Optional[str] = None
    preferred_locations: Optional[List[str]] = None
    preferred_timezones: Optional[List[str]] = None
    notification_enabled: Optional[bool] = None
    email_alerts: Optional[bool] = None
    push_alerts: Optional[bool] = None
    alert_frequency: Optional[str] = Field(None, pattern="^(realtime|daily|weekly)$")


class UserPreferenceResponse(BaseModel):
    id: int
    user_id: int
    min_hourly_rate: Optional[float]
    max_hourly_rate: Optional[float]
    min_fixed_price: Optional[float]
    preferred_project_duration: Optional[str]
    preferred_locations: Optional[List[str]]
    preferred_timezones: Optional[List[str]]
    notification_enabled: bool
    email_alerts: bool
    push_alerts: bool
    alert_frequency: str
    updated_at: datetime

    class Config:
        from_attributes = True


# User with Full Details
class UserDetailResponse(UserProfile):
    skills: List[UserSkillResponse] = []
    preferences: Optional[UserPreferenceResponse] = None

    class Config:
        from_attributes = True
