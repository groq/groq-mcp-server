"""
Configuration settings for AI Freelance Search App
"""

import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from typing import Optional

load_dotenv()


class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "AI Freelance Search App"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # API
    API_PREFIX: str = "/api"
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://freelance_user:freelance_pass@localhost:5432/freelance_db"
    )
    SQL_ECHO: bool = os.getenv("SQL_ECHO", "false").lower() == "true"

    # Redis (for caching and task queue)
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # JWT Authentication
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Groq API
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL_CHAT: str = "llama-3.3-70b-versatile"
    GROQ_MODEL_COMPOUND: str = "compound-beta"
    GROQ_MODEL_COMPOUND_DEEP: str = "compound-beta-deep"

    # Scraping
    SCRAPER_USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    SCRAPER_REQUEST_DELAY: int = 2  # seconds between requests
    SCRAPER_MAX_RETRIES: int = 3

    # Email (for notifications)
    SMTP_HOST: Optional[str] = os.getenv("SMTP_HOST")
    SMTP_PORT: Optional[int] = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: Optional[str] = os.getenv("SMTP_USER")
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD")
    EMAIL_FROM: Optional[str] = os.getenv("EMAIL_FROM")

    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:5173",  # Vite default
        "http://127.0.0.1:3000",
    ]

    # Subscription limits
    FREE_TIER_VETTING_REPORTS: int = 5
    PRO_TIER_VETTING_REPORTS: int = -1  # unlimited
    PREMIUM_TIER_VETTING_REPORTS: int = -1  # unlimited

    # Trust score weights (sum should be 100)
    TRUST_SCORE_WEIGHTS: dict = {
        "account_age": 20,
        "payment_verification": 15,
        "total_spent": 15,
        "hire_rate": 15,
        "average_rating": 20,
        "response_time": 10,
        "completion_rate": 5,
    }

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
