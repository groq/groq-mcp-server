"""
Scam Reports API routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from models.base import get_db
from models.user import User
from models.scam import ScamReport
from models.client import Client
from models.job import Job
from schemas.client import (
    ScamReportCreate,
    ScamReportResponse,
    ScamReportVote
)
from utils.auth import get_current_user

router = APIRouter()


@router.get("", response_model=List[ScamReportResponse])
async def list_scam_reports(
    status_filter: Optional[str] = Query(None, pattern="^(pending|verified|rejected)$"),
    client_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    List scam reports (public endpoint with filters)
    """
    query = db.query(ScamReport)

    # Apply filters
    if status_filter:
        query = query.filter(ScamReport.status == status_filter)

    if client_id:
        query = query.filter(ScamReport.client_id == client_id)

    # Order by created date (newest first)
    query = query.order_by(ScamReport.created_at.desc())

    # Pagination
    offset = (page - 1) * page_size
    reports = query.offset(offset).limit(page_size).all()

    return reports


@router.get("/{report_id}", response_model=ScamReportResponse)
async def get_scam_report(
    report_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific scam report
    """
    report = db.query(ScamReport).filter(ScamReport.id == report_id).first()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scam report not found"
        )

    return report


@router.post("", response_model=ScamReportResponse, status_code=status.HTTP_201_CREATED)
async def create_scam_report(
    report_data: ScamReportCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new scam report
    """
    # Validate client exists if client_id provided
    if report_data.client_id:
        client = db.query(Client).filter(Client.id == report_data.client_id).first()
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found"
            )

    # Validate job exists if job_id provided
    if report_data.job_id:
        job = db.query(Job).filter(Job.id == report_data.job_id).first()
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )

    # Create report
    scam_report = ScamReport(
        client_id=report_data.client_id,
        reporter_user_id=current_user.id,
        job_id=report_data.job_id,
        report_type=report_data.report_type,
        description=report_data.description,
        evidence_urls=report_data.evidence_urls,
        status='pending'
    )

    db.add(scam_report)
    db.commit()
    db.refresh(scam_report)

    # If client_id provided, flag the client
    if report_data.client_id:
        client = db.query(Client).filter(Client.id == report_data.client_id).first()
        if client:
            client.is_flagged = True
            client.flag_reason = f"Scam report: {report_data.report_type}"
            db.commit()

    return scam_report


@router.post("/{report_id}/vote", response_model=ScamReportResponse)
async def vote_on_report(
    report_id: int,
    vote_data: ScamReportVote,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Vote on a scam report (upvote or downvote)
    """
    report = db.query(ScamReport).filter(ScamReport.id == report_id).first()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scam report not found"
        )

    # Update vote count
    if vote_data.vote_type == "upvote":
        report.upvotes += 1
    elif vote_data.vote_type == "downvote":
        report.downvotes += 1

    db.commit()
    db.refresh(report)

    return report


@router.put("/{report_id}/verify", response_model=ScamReportResponse)
async def verify_scam_report(
    report_id: int,
    verified: bool,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Verify or reject a scam report (admin only)
    TODO: Add admin role check
    """
    report = db.query(ScamReport).filter(ScamReport.id == report_id).first()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scam report not found"
        )

    # Update report status
    report.status = 'verified' if verified else 'rejected'
    report.verified_by_admin = current_user.id
    report.verified_at = datetime.utcnow()

    db.commit()
    db.refresh(report)

    return report


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scam_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a scam report (only reporter or admin can delete)
    """
    report = db.query(ScamReport).filter(ScamReport.id == report_id).first()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scam report not found"
        )

    # Check if user is the reporter (or admin - TODO: add admin check)
    if report.reporter_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own reports"
        )

    db.delete(report)
    db.commit()

    return None
