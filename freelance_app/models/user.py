"""
User-related SQLAlchemy models
"""

from sqlalchemy import (
    Column, Integer, String, Boolean, TIMESTAMP,
    ForeignKey, DECIMAL, ARRAY, Text, CheckConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    profile_picture_url = Column(Text)
    subscription_tier = Column(
        String(50),
        default='free',
        server_default='free'
    )
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    last_login = Column(TIMESTAMP)
    is_active = Column(Boolean, default=True, server_default='true')
    email_verified = Column(Boolean, default=False, server_default='false')
    two_factor_enabled = Column(Boolean, default=False, server_default='false')

    # Relationships
    skills = relationship('UserSkill', back_populates='user', cascade='all, delete-orphan')
    preferences = relationship('UserPreference', back_populates='user', uselist=False, cascade='all, delete-orphan')
    saved_searches = relationship('SavedSearch', back_populates='user', cascade='all, delete-orphan')
    applications = relationship('JobApplication', back_populates='user', cascade='all, delete-orphan')
    scam_reports = relationship('ScamReport', back_populates='reporter', foreign_keys='ScamReport.reporter_user_id')
    analytics = relationship('UserAnalytics', back_populates='user', cascade='all, delete-orphan')

    __table_args__ = (
        CheckConstraint(
            "subscription_tier IN ('free', 'pro', 'premium')",
            name='check_subscription_tier'
        ),
    )

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', tier='{self.subscription_tier}')>"


class UserSkill(Base):
    __tablename__ = 'user_skills'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    skill_name = Column(String(255), nullable=False)
    proficiency_level = Column(Integer)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    user = relationship('User', back_populates='skills')

    __table_args__ = (
        CheckConstraint(
            'proficiency_level >= 1 AND proficiency_level <= 5',
            name='check_proficiency_level'
        ),
    )

    def __repr__(self):
        return f"<UserSkill(user_id={self.user_id}, skill='{self.skill_name}', level={self.proficiency_level})>"


class UserPreference(Base):
    __tablename__ = 'user_preferences'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    min_hourly_rate = Column(DECIMAL(10, 2))
    max_hourly_rate = Column(DECIMAL(10, 2))
    min_fixed_price = Column(DECIMAL(10, 2))
    preferred_project_duration = Column(String(50))
    preferred_locations = Column(ARRAY(Text))
    preferred_timezones = Column(ARRAY(Text))
    notification_enabled = Column(Boolean, default=True, server_default='true')
    email_alerts = Column(Boolean, default=True, server_default='true')
    push_alerts = Column(Boolean, default=True, server_default='true')
    alert_frequency = Column(String(50), default='realtime', server_default='realtime')
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship('User', back_populates='preferences')

    __table_args__ = (
        CheckConstraint(
            "alert_frequency IN ('realtime', 'daily', 'weekly')",
            name='check_alert_frequency'
        ),
    )

    def __repr__(self):
        return f"<UserPreference(user_id={self.user_id}, alert_frequency='{self.alert_frequency}')>"
