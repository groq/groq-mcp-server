"""
Company research model
"""

from sqlalchemy import (
    Column, Integer, String, Boolean, TIMESTAMP,
    ForeignKey, Text, CheckConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB
from .base import Base


class CompanyResearch(Base):
    __tablename__ = 'company_research'

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey('clients.id', ondelete='CASCADE'), unique=True, nullable=False, index=True)
    company_name = Column(String(255))
    linkedin_url = Column(Text)
    linkedin_verified = Column(Boolean, default=False, server_default='false')
    linkedin_employee_count = Column(Integer)
    website_url = Column(Text)
    website_verified = Column(Boolean, default=False, server_default='false')
    twitter_url = Column(Text)
    facebook_url = Column(Text)
    instagram_url = Column(Text)
    social_media_presence_score = Column(Integer)
    business_registration_found = Column(Boolean, default=False, server_default='false')
    recent_news_count = Column(Integer, default=0, server_default='0')
    digital_footprint_score = Column(Integer)
    research_data = Column(JSONB)  # Store full research JSON
    researched_at = Column(TIMESTAMP, server_default=func.now())
    last_updated = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    client = relationship('Client', back_populates='company_research')

    __table_args__ = (
        CheckConstraint(
            'social_media_presence_score >= 0 AND social_media_presence_score <= 100',
            name='check_social_media_score'
        ),
        CheckConstraint(
            'digital_footprint_score >= 0 AND digital_footprint_score <= 100',
            name='check_digital_footprint_score'
        ),
    )

    def __repr__(self):
        return f"<CompanyResearch(client_id={self.client_id}, company='{self.company_name}')>"
