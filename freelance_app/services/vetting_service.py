"""
Vetting Service - Generate comprehensive client vetting reports
This is a CORE FEATURE of the application
"""

from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict, List, Any

from models.client import Client, ClientReview, ClientRedFlag
from models.company import CompanyResearch
from schemas.client import ClientVettingReport
from .ai_service import AIService
from .trust_score_service import TrustScoreService


class VettingService:
    """
    Generate comprehensive client vetting reports
    """

    def __init__(self, db: Session):
        self.db = db
        self.ai_service = AIService()
        self.trust_score_service = TrustScoreService(db)

    async def generate_vetting_report(self, client_id: int) -> ClientVettingReport:
        """
        Generate comprehensive client vetting report
        This is the main method that creates the vetting report
        """
        # Get client
        client = self.db.query(Client).filter(Client.id == client_id).first()
        if not client:
            raise ValueError(f"Client {client_id} not found")

        # Calculate/update trust score if needed
        if not client.trust_score or self._should_recalculate_trust_score(client):
            client = self.trust_score_service.calculate_trust_score(client_id)

        # Get trust score breakdown
        trust_score_breakdown = self.trust_score_service.get_trust_score_breakdown(client_id)

        # Get strengths and concerns
        strengths, concerns = self.trust_score_service.get_strengths_and_concerns(client)

        # Get red flags
        red_flags = self.db.query(ClientRedFlag).filter(
            ClientRedFlag.client_id == client_id,
            ClientRedFlag.is_active == True
        ).all()

        # Detect additional red flags using AI
        await self._detect_and_create_red_flags(client)
        red_flags = self.db.query(ClientRedFlag).filter(
            ClientRedFlag.client_id == client_id,
            ClientRedFlag.is_active == True
        ).all()

        # Get reviews
        reviews = self.db.query(ClientReview).filter(
            ClientReview.client_id == client_id
        ).all()

        # Analyze reviews
        reviews_summary = await self._analyze_reviews(reviews)

        # Get common themes
        common_themes = await self._extract_common_themes(reviews)

        # Get company research
        company_research = self.db.query(CompanyResearch).filter(
            CompanyResearch.client_id == client_id
        ).first()

        # Generate AI recommendation
        recommendation = await self.ai_service.generate_vetting_recommendation(
            trust_score=client.trust_score,
            strengths=strengths,
            concerns=concerns,
            red_flags=[f"{rf.flag_type}: {rf.description}" for rf in red_flags]
        )

        # Build vetting report
        vetting_report = ClientVettingReport(
            client=client,
            trust_score=client.trust_score,
            trust_score_breakdown=trust_score_breakdown,
            strengths=strengths,
            concerns=concerns,
            red_flags=red_flags,
            reviews_summary=reviews_summary,
            common_themes=common_themes,
            company_research=company_research,
            recommendation=recommendation
        )

        return vetting_report

    async def perform_company_research(self, client_id: int) -> CompanyResearch:
        """
        Perform comprehensive company research using Groq's compound-beta API
        """
        client = self.db.query(Client).filter(Client.id == client_id).first()
        if not client:
            raise ValueError(f"Client {client_id} not found")

        # Check if research already exists and is recent (< 30 days old)
        existing_research = self.db.query(CompanyResearch).filter(
            CompanyResearch.client_id == client_id
        ).first()

        if existing_research:
            days_old = (datetime.utcnow() - existing_research.last_updated).days
            if days_old < 30:
                return existing_research  # Return cached research

        # Perform AI-powered company research
        company_name = client.company_name or client.name
        if not company_name:
            raise ValueError("Client has no company name")

        research_data = await self.ai_service.research_company(
            company_name=company_name,
            additional_info=f"Location: {client.location}" if client.location else None
        )

        # Calculate social media presence score
        social_score = self._calculate_social_media_score(research_data)

        # Calculate digital footprint score
        digital_score = self._calculate_digital_footprint_score(research_data)

        # Create or update company research record
        if existing_research:
            # Update existing
            existing_research.company_name = company_name
            existing_research.linkedin_url = research_data.get("linkedin_url")
            existing_research.linkedin_verified = bool(research_data.get("linkedin_url"))
            existing_research.linkedin_employee_count = research_data.get("employee_count")
            existing_research.website_url = research_data.get("website_url")
            existing_research.website_verified = bool(research_data.get("website_url"))
            existing_research.twitter_url = research_data.get("twitter_url")
            existing_research.facebook_url = research_data.get("facebook_url")
            existing_research.instagram_url = research_data.get("instagram_url")
            existing_research.social_media_presence_score = social_score
            existing_research.recent_news_count = len(research_data.get("news_articles", []))
            existing_research.digital_footprint_score = digital_score
            existing_research.research_data = research_data
            existing_research.last_updated = datetime.utcnow()

            self.db.commit()
            self.db.refresh(existing_research)
            return existing_research
        else:
            # Create new
            company_research = CompanyResearch(
                client_id=client_id,
                company_name=company_name,
                linkedin_url=research_data.get("linkedin_url"),
                linkedin_verified=bool(research_data.get("linkedin_url")),
                linkedin_employee_count=research_data.get("employee_count"),
                website_url=research_data.get("website_url"),
                website_verified=bool(research_data.get("website_url")),
                twitter_url=research_data.get("twitter_url"),
                facebook_url=research_data.get("facebook_url"),
                instagram_url=research_data.get("instagram_url"),
                social_media_presence_score=social_score,
                recent_news_count=len(research_data.get("news_articles", [])),
                digital_footprint_score=digital_score,
                research_data=research_data
            )

            self.db.add(company_research)
            self.db.commit()
            self.db.refresh(company_research)

            return company_research

    async def _detect_and_create_red_flags(self, client: Client) -> List[ClientRedFlag]:
        """
        Use AI to detect red flags and create database records
        """
        # Prepare client data for AI analysis
        client_data = {
            "account_age_days": (datetime.utcnow() - client.account_created_date).days if client.account_created_date else 0,
            "total_jobs_posted": client.total_jobs_posted,
            "total_hires": client.total_hires,
            "hire_rate": float(client.hire_rate) if client.hire_rate else 0,
            "total_spent": float(client.total_spent),
            "average_rating": float(client.average_rating) if client.average_rating else 0,
            "verified_payment": client.verified_payment,
            "review_count": client.review_count
        }

        # Detect red flags using AI
        ai_red_flags = await self.ai_service.detect_red_flags(client_data)

        # Create red flag records
        created_flags = []
        for flag in ai_red_flags:
            # Check if this type of flag already exists
            existing = self.db.query(ClientRedFlag).filter(
                ClientRedFlag.client_id == client.id,
                ClientRedFlag.flag_type == flag.get("flag_type"),
                ClientRedFlag.is_active == True
            ).first()

            if not existing:
                new_flag = ClientRedFlag(
                    client_id=client.id,
                    flag_type=flag.get("flag_type"),
                    severity=flag.get("severity"),
                    description=flag.get("description")
                )
                self.db.add(new_flag)
                created_flags.append(new_flag)

        if created_flags:
            self.db.commit()

        return created_flags

    async def _analyze_reviews(self, reviews: List[ClientReview]) -> Dict[str, Any]:
        """
        Analyze reviews and generate summary
        """
        if not reviews:
            return {
                "total_reviews": 0,
                "average_rating": 0,
                "average_sentiment": 0,
                "positive_count": 0,
                "negative_count": 0,
                "neutral_count": 0
            }

        # Calculate sentiment for reviews that don't have it
        for review in reviews:
            if review.review_text and review.sentiment_score is None:
                sentiment = await self.ai_service.analyze_sentiment(review.review_text)
                review.sentiment_score = sentiment

        self.db.commit()

        # Calculate summary
        total_reviews = len(reviews)
        average_rating = sum(r.rating for r in reviews if r.rating) / total_reviews if total_reviews > 0 else 0
        average_sentiment = sum(float(r.sentiment_score or 0) for r in reviews) / total_reviews if total_reviews > 0 else 0

        positive_count = sum(1 for r in reviews if r.sentiment_score and r.sentiment_score > 0.3)
        negative_count = sum(1 for r in reviews if r.sentiment_score and r.sentiment_score < -0.3)
        neutral_count = total_reviews - positive_count - negative_count

        return {
            "total_reviews": total_reviews,
            "average_rating": round(average_rating, 2),
            "average_sentiment": round(average_sentiment, 2),
            "positive_count": positive_count,
            "negative_count": negative_count,
            "neutral_count": neutral_count
        }

    async def _extract_common_themes(self, reviews: List[ClientReview]) -> List[str]:
        """
        Extract common themes from reviews using AI
        """
        if not reviews:
            return []

        review_texts = [r.review_text for r in reviews if r.review_text]
        if not review_texts:
            return []

        themes = await self.ai_service.extract_themes_from_reviews(review_texts)
        return themes

    def _should_recalculate_trust_score(self, client: Client) -> bool:
        """
        Determine if trust score should be recalculated
        Recalculate if:
        - Never calculated before
        - More than 7 days old
        """
        if not client.trust_score_updated_at:
            return True

        days_old = (datetime.utcnow() - client.trust_score_updated_at).days
        return days_old > 7

    def _calculate_social_media_score(self, research_data: Dict[str, Any]) -> int:
        """
        Calculate social media presence score (0-100)
        """
        score = 0

        if research_data.get("linkedin_url"):
            score += 30
        if research_data.get("twitter_url"):
            score += 20
        if research_data.get("facebook_url"):
            score += 20
        if research_data.get("instagram_url"):
            score += 15
        if research_data.get("website_url"):
            score += 15

        return min(score, 100)

    def _calculate_digital_footprint_score(self, research_data: Dict[str, Any]) -> int:
        """
        Calculate overall digital footprint score (0-100)
        """
        score = 0

        # Website
        if research_data.get("website_url"):
            score += 25

        # LinkedIn with employee count
        if research_data.get("linkedin_url"):
            score += 20
            if research_data.get("employee_count", 0) > 10:
                score += 10

        # Social media presence
        social_count = sum([
            1 for key in ["twitter_url", "facebook_url", "instagram_url"]
            if research_data.get(key)
        ])
        score += social_count * 10

        # Recent news
        news_count = len(research_data.get("news_articles", []))
        if news_count > 0:
            score += min(news_count * 5, 15)

        # Business registration
        if research_data.get("business_registration"):
            score += 10

        return min(score, 100)
