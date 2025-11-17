"""
Trust Score Service - Calculate client trust scores
"""

from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Dict

from models.client import Client
from config import settings


class TrustScoreService:
    """
    Calculate trust scores for clients based on multiple factors
    Trust score range: 0-100
    """

    def __init__(self, db: Session):
        self.db = db
        self.weights = settings.TRUST_SCORE_WEIGHTS

    def calculate_trust_score(self, client_id: int) -> Client:
        """
        Calculate comprehensive trust score for a client
        Returns updated client object
        """
        client = self.db.query(Client).filter(Client.id == client_id).first()

        if not client:
            raise ValueError(f"Client {client_id} not found")

        # Calculate individual component scores
        components = {
            "account_age": self._score_account_age(client),
            "payment_verification": self._score_payment_verification(client),
            "total_spent": self._score_total_spent(client),
            "hire_rate": self._score_hire_rate(client),
            "average_rating": self._score_average_rating(client),
            "response_time": self._score_response_time(client),
            "completion_rate": self._score_completion_rate(client),
        }

        # Calculate weighted trust score
        trust_score = 0
        for component, score in components.items():
            weight = self.weights.get(component, 0)
            trust_score += (score * weight) / 100

        # Round to integer
        trust_score = int(round(trust_score))

        # Update client
        client.trust_score = trust_score
        client.trust_score_updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(client)

        return client

    def get_trust_score_breakdown(self, client_id: int) -> Dict[str, int]:
        """
        Get detailed breakdown of trust score components
        """
        client = self.db.query(Client).filter(Client.id == client_id).first()

        if not client:
            raise ValueError(f"Client {client_id} not found")

        breakdown = {
            "account_age": self._score_account_age(client),
            "payment_verification": self._score_payment_verification(client),
            "total_spent": self._score_total_spent(client),
            "hire_rate": self._score_hire_rate(client),
            "average_rating": self._score_average_rating(client),
            "response_time": self._score_response_time(client),
            "completion_rate": self._score_completion_rate(client),
        }

        # Add weighted scores
        weighted_breakdown = {}
        for component, score in breakdown.items():
            weight = self.weights.get(component, 0)
            weighted_score = int((score * weight) / 100)
            weighted_breakdown[component] = {
                "raw_score": score,
                "weight": weight,
                "weighted_score": weighted_score
            }

        return weighted_breakdown

    def _score_account_age(self, client: Client) -> int:
        """
        Score based on account age (0-100)
        - Less than 1 month: 20
        - 1-3 months: 40
        - 3-6 months: 60
        - 6-12 months: 80
        - 1+ years: 100
        """
        if not client.account_created_date:
            return 0

        age = datetime.utcnow() - client.account_created_date
        days = age.days

        if days < 30:
            return 20
        elif days < 90:
            return 40
        elif days < 180:
            return 60
        elif days < 365:
            return 80
        else:
            return 100

    def _score_payment_verification(self, client: Client) -> int:
        """
        Score based on payment verification (0-100)
        - Verified: 100
        - Not verified: 0
        """
        return 100 if client.verified_payment else 0

    def _score_total_spent(self, client: Client) -> int:
        """
        Score based on total amount spent (0-100)
        - $0-$500: 20
        - $500-$2,000: 40
        - $2,000-$10,000: 60
        - $10,000-$50,000: 80
        - $50,000+: 100
        """
        spent = float(client.total_spent or 0)

        if spent < 500:
            return 20
        elif spent < 2000:
            return 40
        elif spent < 10000:
            return 60
        elif spent < 50000:
            return 80
        else:
            return 100

    def _score_hire_rate(self, client: Client) -> int:
        """
        Score based on hire-to-post ratio (0-100)
        hire_rate = (total_hires / total_jobs_posted) * 100
        """
        if not client.hire_rate:
            # Calculate if not stored
            if client.total_jobs_posted > 0:
                hire_rate = (client.total_hires / client.total_jobs_posted) * 100
            else:
                return 0
        else:
            hire_rate = float(client.hire_rate)

        # Convert percentage to score
        # 0-20%: 20
        # 20-40%: 40
        # 40-60%: 60
        # 60-80%: 80
        # 80-100%: 100
        if hire_rate < 20:
            return 20
        elif hire_rate < 40:
            return 40
        elif hire_rate < 60:
            return 60
        elif hire_rate < 80:
            return 80
        else:
            return 100

    def _score_average_rating(self, client: Client) -> int:
        """
        Score based on average rating (0-100)
        Rating is typically 1-5 stars
        Convert to 0-100 scale: (rating / 5) * 100
        """
        if not client.average_rating:
            return 0

        rating = float(client.average_rating)

        # Convert 1-5 scale to 0-100
        score = (rating / 5.0) * 100

        return int(round(score))

    def _score_response_time(self, client: Client) -> int:
        """
        Score based on average response time in hours (0-100)
        - < 1 hour: 100
        - 1-6 hours: 80
        - 6-24 hours: 60
        - 24-48 hours: 40
        - > 48 hours: 20
        """
        if not client.average_response_time:
            return 50  # Neutral if unknown

        hours = client.average_response_time

        if hours < 1:
            return 100
        elif hours < 6:
            return 80
        elif hours < 24:
            return 60
        elif hours < 48:
            return 40
        else:
            return 20

    def _score_completion_rate(self, client: Client) -> int:
        """
        Score based on project completion rate (0-100)
        Completion rate = hires / posted jobs
        This is similar to hire rate but focuses on successful completions
        """
        if client.total_jobs_posted == 0:
            return 0

        completion_rate = (client.total_hires / client.total_jobs_posted) * 100

        # Map to score (higher is better)
        if completion_rate >= 90:
            return 100
        elif completion_rate >= 70:
            return 80
        elif completion_rate >= 50:
            return 60
        elif completion_rate >= 30:
            return 40
        else:
            return 20

    def get_trust_level_label(self, trust_score: int) -> str:
        """
        Convert trust score to human-readable label
        """
        if trust_score >= 80:
            return "Excellent"
        elif trust_score >= 60:
            return "Good"
        elif trust_score >= 40:
            return "Fair"
        elif trust_score >= 20:
            return "Poor"
        else:
            return "Very Poor"

    def get_strengths_and_concerns(self, client: Client) -> tuple:
        """
        Get list of client strengths and concerns based on metrics
        Returns (strengths: List[str], concerns: List[str])
        """
        strengths = []
        concerns = []

        # Payment verification
        if client.verified_payment:
            strengths.append("Verified payment method")
        else:
            concerns.append("Payment method not verified")

        # Total spent
        spent = float(client.total_spent or 0)
        if spent >= 50000:
            strengths.append(f"${int(spent):,}+ total spent")
        elif spent >= 10000:
            strengths.append(f"${int(spent):,} total spent")
        elif spent < 500:
            concerns.append("Low total spending on platform")

        # Total hires
        if client.total_hires >= 20:
            strengths.append(f"{client.total_hires} successful hires")
        elif client.total_hires < 5:
            concerns.append("Few successful hires")

        # Average rating
        if client.average_rating:
            rating = float(client.average_rating)
            if rating >= 4.5:
                strengths.append(f"{rating:.1f}/5 average rating")
            elif rating < 3.5:
                concerns.append(f"Low average rating ({rating:.1f}/5)")

        # Account age
        if client.account_created_date:
            age = datetime.utcnow() - client.account_created_date
            years = age.days / 365
            if years >= 1:
                strengths.append(f"Active for {int(years)} year{'s' if years >= 2 else ''}")
            elif age.days < 30:
                concerns.append("New account (less than 1 month)")

        # Hire rate
        if client.hire_rate:
            hire_rate = float(client.hire_rate)
            if hire_rate >= 70:
                strengths.append(f"{int(hire_rate)}% hire rate")
            elif hire_rate < 30:
                concerns.append(f"Low hire rate ({int(hire_rate)}%)")

        # Response time
        if client.average_response_time:
            hours = client.average_response_time
            if hours < 6:
                strengths.append(f"Fast response time ({hours}h avg)")
            elif hours > 48:
                concerns.append(f"Slow response time ({hours}h avg)")

        return strengths, concerns
