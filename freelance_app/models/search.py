"""
Saved search model
"""

from sqlalchemy import (
    Column, Integer, String, Boolean, TIMESTAMP,
    ForeignKey, Text
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB
from .base import Base


class SavedSearch(Base):
    __tablename__ = 'saved_searches'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    search_query = Column(Text)
    filters = Column(JSONB)  # Store filter parameters as JSON
    alert_enabled = Column(Boolean, default=True, server_default='true')
    created_at = Column(TIMESTAMP, server_default=func.now())
    last_triggered = Column(TIMESTAMP)

    # Relationships
    user = relationship('User', back_populates='saved_searches')

    def __repr__(self):
        return f"<SavedSearch(id={self.id}, user_id={self.user_id}, name='{self.name}')>"
