"""
Clients API routes - including vetting reports
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from models.base import get_db
from models.user import User
from models.client import Client, ClientReview, ClientRedFlag
from models.company import CompanyResearch
from schemas.client import (
    ClientResponse,
    ClientReviewResponse,
    ClientRedFlagResponse,
    CompanyResearchResponse,
    ClientVettingReport
)
from utils.auth import get_current_user
from services.vetting_service import VettingService
from services.trust_score_service import TrustScoreService

router = APIRouter()


@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: int,
    db: Session = Depends(get_db)
):
    """
    Get client details by ID
    """
    client = db.query(Client).filter(Client.id == client_id).first()

    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )

    return client


@router.get("/{client_id}/reviews", response_model=List[ClientReviewResponse])
async def get_client_reviews(
    client_id: int,
    db: Session = Depends(get_db)
):
    """
    Get client reviews
    """
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )

    reviews = db.query(ClientReview).filter(
        ClientReview.client_id == client_id
    ).all()

    return reviews


@router.get("/{client_id}/red-flags", response_model=List[ClientRedFlagResponse])
async def get_client_red_flags(
    client_id: int,
    db: Session = Depends(get_db)
):
    """
    Get client red flags
    """
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )

    red_flags = db.query(ClientRedFlag).filter(
        ClientRedFlag.client_id == client_id,
        ClientRedFlag.is_active == True
    ).all()

    return red_flags


@router.get("/{client_id}/company-research", response_model=CompanyResearchResponse)
async def get_company_research(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get company research for a client
    """
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )

    research = db.query(CompanyResearch).filter(
        CompanyResearch.client_id == client_id
    ).first()

    if not research:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No company research available for this client"
        )

    return research


@router.get("/{client_id}/vetting-report", response_model=ClientVettingReport)
async def get_vetting_report(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive client vetting report
    This is a CORE FEATURE of the application
    """
    # Check if client exists
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )

    # Check subscription limits (free tier: 5 reports per month)
    if current_user.subscription_tier == 'free':
        # TODO: Implement monthly report limit tracking
        pass

    # Initialize vetting service
    vetting_service = VettingService(db)

    # Generate comprehensive vetting report
    try:
        report = await vetting_service.generate_vetting_report(client_id)
        return report
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating vetting report: {str(e)}"
        )


@router.post("/{client_id}/research", response_model=CompanyResearchResponse)
async def trigger_company_research(
    client_id: int,
    db: Session = Depends(get_current_user),
    current_user: User = Depends(get_current_user)
):
    """
    Trigger company research for a client (Pro/Premium feature)
    """
    # Check subscription tier
    if current_user.subscription_tier == 'free':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Company research is a Pro/Premium feature"
        )

    # Check if client exists
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )

    # Trigger research
    vetting_service = VettingService(db)

    try:
        research = await vetting_service.perform_company_research(client_id)
        return research
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error performing company research: {str(e)}"
        )


@router.post("/{client_id}/recalculate-trust-score")
async def recalculate_trust_score(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Recalculate trust score for a client
    """
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )

    trust_score_service = TrustScoreService(db)
    updated_client = trust_score_service.calculate_trust_score(client_id)

    return {
        "client_id": client_id,
        "trust_score": updated_client.trust_score,
        "updated_at": updated_client.trust_score_updated_at
    }
