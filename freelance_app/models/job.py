"""
Job-related SQLAlchemy models
"""

from sqlalchemy import (
    Column, Integer, String, Boolean, TIMESTAMP,
    ForeignKey, DECIMAL, ARRAY, Text, CheckConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base


class Job(Base):
    __tablename__ = 'jobs'

    id = Column(Integer, primary_key=True, index=True)
    platform_id = Column(Integer, ForeignKey('freelance_platforms.id'), index=True)
    external_job_id = Column(String(255))
    title = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(255), index=True)
    subcategory = Column(String(255))
    skills_required = Column(ARRAY(Text))
    job_type = Column(String(50))
    budget_min = Column(DECIMAL(10, 2))
    budget_max = Column(DECIMAL(10, 2))
    hourly_rate = Column(DECIMAL(10, 2))
    fixed_price = Column(DECIMAL(10, 2))
    duration = Column(String(100))
    experience_level = Column(String(50))
    client_id = Column(Integer, ForeignKey('clients.id'), index=True)
    location = Column(String(255))
    timezone = Column(String(100))
    posted_date = Column(TIMESTAMP, index=True)
    deadline = Column(TIMESTAMP)
    applicants_count = Column(Integer, default=0, server_default='0')
    url = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True, server_default='true', index=True)
    scraped_at = Column(TIMESTAMP, server_default=func.now())
    last_updated = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    ai_summary = Column(Text)

    # Relationships
    platform = relationship('FreelancePlatform', back_populates='jobs')
    client = relationship('Client', back_populates='jobs')
    applications = relationship('JobApplication', back_populates='job', cascade='all, delete-orphan')
    scam_reports = relationship('ScamReport', back_populates='job')

    __table_args__ = (
        CheckConstraint(
            "job_type IN ('hourly', 'fixed', 'both')",
            name='check_job_type'
        ),
        CheckConstraint(
            "experience_level IN ('entry', 'intermediate', 'expert', 'any')",
            name='check_experience_level'
        ),
    )

    def __repr__(self):
        return f"<Job(id={self.id}, title='{self.title[:30]}...', platform_id={self.platform_id})>"


class JobApplication(Base):
    __tablename__ = 'job_applications'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    job_id = Column(Integer, ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False, index=True)
    applied_at = Column(TIMESTAMP, server_default=func.now())
    status = Column(String(50), default='applied', server_default='applied', index=True)
    notes = Column(Text)

    # Relationships
    user = relationship('User', back_populates='applications')
    job = relationship('Job', back_populates='applications')

    __table_args__ = (
        CheckConstraint(
            "status IN ('applied', 'shortlisted', 'hired', 'rejected')",
            name='check_application_status'
        ),
    )

    def __repr__(self):
        return f"<JobApplication(user_id={self.user_id}, job_id={self.job_id}, status='{self.status}')>"
