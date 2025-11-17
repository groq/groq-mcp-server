"""
Freelance platform model
"""

from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base


class FreelancePlatform(Base):
    __tablename__ = 'freelance_platforms'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    base_url = Column(Text, nullable=False)
    logo_url = Column(Text)
    has_api = Column(Boolean, default=False, server_default='false')
    scraper_enabled = Column(Boolean, default=True, server_default='true')
    last_scraped = Column(TIMESTAMP)
    is_active = Column(Boolean, default=True, server_default='true')
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    jobs = relationship('Job', back_populates='platform')
    clients = relationship('Client', back_populates='platform')

    def __repr__(self):
        return f"<FreelancePlatform(id={self.id}, name='{self.name}')>"
