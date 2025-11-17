"""
Client-related SQLAlchemy models
"""

from sqlalchemy import (
    Column, Integer, String, Boolean, TIMESTAMP,
    ForeignKey, DECIMAL, ARRAY, Text, CheckConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base


class Client(Base):
    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True, index=True)
    platform_id = Column(Integer, ForeignKey('freelance_platforms.id'), index=True)
    external_client_id = Column(String(255))
    name = Column(String(255))
    company_name = Column(String(255))
    profile_url = Column(Text)
    account_created_date = Column(TIMESTAMP)
    location = Column(String(255))
    timezone = Column(String(100))
    verified_payment = Column(Boolean, default=False, server_default='false')
    total_jobs_posted = Column(Integer, default=0, server_default='0')
    total_hires = Column(Integer, default=0, server_default='0')
    total_spent = Column(DECIMAL(12, 2), default=0, server_default='0')
    average_rating = Column(DECIMAL(3, 2))
    review_count = Column(Integer, default=0, server_default='0')
    average_response_time = Column(Integer)  # in hours
    hire_rate = Column(DECIMAL(5, 2))
    avg_project_value = Column(DECIMAL(10, 2))
    repeat_hire_rate = Column(DECIMAL(5, 2))
    last_active = Column(TIMESTAMP)
    trust_score = Column(Integer, index=True)
    trust_score_updated_at = Column(TIMESTAMP)
    is_flagged = Column(Boolean, default=False, server_default='false', index=True)
    flag_reason = Column(Text)
    scraped_at = Column(TIMESTAMP, server_default=func.now())
    last_updated = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    platform = relationship('FreelancePlatform', back_populates='clients')
    jobs = relationship('Job', back_populates='client')
    reviews = relationship('ClientReview', back_populates='client', cascade='all, delete-orphan')
    red_flags = relationship('ClientRedFlag', back_populates='client', cascade='all, delete-orphan')
    company_research = relationship('CompanyResearch', back_populates='client', uselist=False, cascade='all, delete-orphan')
    scam_reports = relationship('ScamReport', back_populates='client')

    __table_args__ = (
        CheckConstraint(
            'trust_score >= 0 AND trust_score <= 100',
            name='check_trust_score_range'
        ),
    )

    def __repr__(self):
        return f"<Client(id={self.id}, name='{self.name}', trust_score={self.trust_score})>"


class ClientReview(Base):
    __tablename__ = 'client_reviews'

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey('clients.id', ondelete='CASCADE'), nullable=False, index=True)
    freelancer_name = Column(String(255))
    rating = Column(Integer, index=True)
    review_text = Column(Text)
    project_title = Column(String(255))
    project_value = Column(DECIMAL(10, 2))
    review_date = Column(TIMESTAMP)
    sentiment_score = Column(DECIMAL(3, 2))  # -1 to 1
    key_themes = Column(ARRAY(Text))
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    client = relationship('Client', back_populates='reviews')

    __table_args__ = (
        CheckConstraint(
            'rating >= 1 AND rating <= 5',
            name='check_rating_range'
        ),
    )

    def __repr__(self):
        return f"<ClientReview(client_id={self.client_id}, rating={self.rating})>"


class ClientRedFlag(Base):
    __tablename__ = 'client_red_flags'

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey('clients.id', ondelete='CASCADE'), nullable=False, index=True)
    flag_type = Column(String(100), nullable=False)
    severity = Column(String(50), index=True)
    description = Column(Text)
    detected_at = Column(TIMESTAMP, server_default=func.now())
    is_active = Column(Boolean, default=True, server_default='true')

    # Relationships
    client = relationship('Client', back_populates='red_flags')

    __table_args__ = (
        CheckConstraint(
            "severity IN ('low', 'medium', 'high', 'critical')",
            name='check_severity'
        ),
    )

    def __repr__(self):
        return f"<ClientRedFlag(client_id={self.client_id}, type='{self.flag_type}', severity='{self.severity}')>"
