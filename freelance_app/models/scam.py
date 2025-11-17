"""
Scam report model
"""

from sqlalchemy import (
    Column, Integer, String, TIMESTAMP,
    ForeignKey, ARRAY, Text, CheckConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base


class ScamReport(Base):
    __tablename__ = 'scam_reports'

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey('clients.id'), index=True)
    reporter_user_id = Column(Integer, ForeignKey('users.id'))
    job_id = Column(Integer, ForeignKey('jobs.id'))
    report_type = Column(String(100))
    description = Column(Text, nullable=False)
    evidence_urls = Column(ARRAY(Text))
    status = Column(String(50), default='pending', server_default='pending', index=True)
    verified_by_admin = Column(Integer, ForeignKey('users.id'))
    verified_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, server_default=func.now())
    upvotes = Column(Integer, default=0, server_default='0')
    downvotes = Column(Integer, default=0, server_default='0')

    # Relationships
    client = relationship('Client', back_populates='scam_reports', foreign_keys=[client_id])
    reporter = relationship('User', back_populates='scam_reports', foreign_keys=[reporter_user_id])
    job = relationship('Job', back_populates='scam_reports')

    __table_args__ = (
        CheckConstraint(
            "report_type IN ('scam', 'fake', 'non_payment', 'harassment', 'other')",
            name='check_report_type'
        ),
        CheckConstraint(
            "status IN ('pending', 'verified', 'rejected')",
            name='check_report_status'
        ),
    )

    def __repr__(self):
        return f"<ScamReport(id={self.id}, client_id={self.client_id}, type='{self.report_type}', status='{self.status}')>"
