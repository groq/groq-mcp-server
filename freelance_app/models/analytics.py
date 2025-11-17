"""
Analytics-related models
"""

from sqlalchemy import (
    Column, Integer, String, TIMESTAMP, Date,
    ForeignKey, DECIMAL
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB
from .base import Base


class UserAnalytics(Base):
    __tablename__ = 'user_analytics'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    date = Column(Date, nullable=False)
    jobs_viewed = Column(Integer, default=0, server_default='0')
    jobs_applied = Column(Integer, default=0, server_default='0')
    vetting_reports_viewed = Column(Integer, default=0, server_default='0')
    avg_client_trust_score = Column(DECIMAL(5, 2))
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    user = relationship('User', back_populates='analytics')

    def __repr__(self):
        return f"<UserAnalytics(user_id={self.user_id}, date={self.date})>"


class PlatformAnalytics(Base):
    __tablename__ = 'platform_analytics'

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, unique=True, index=True)
    total_jobs_scraped = Column(Integer, default=0, server_default='0')
    total_active_jobs = Column(Integer, default=0, server_default='0')
    avg_hourly_rate = Column(DECIMAL(10, 2))
    avg_fixed_price = Column(DECIMAL(10, 2))
    top_skills = Column(JSONB)  # {skill_name: count}
    top_categories = Column(JSONB)  # {category: count}
    created_at = Column(TIMESTAMP, server_default=func.now())

    def __repr__(self):
        return f"<PlatformAnalytics(date={self.date}, total_jobs={self.total_jobs_scraped})>"
