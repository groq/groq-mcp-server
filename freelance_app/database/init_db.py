"""
Database initialization script
Run this to create all database tables
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.base import Base, engine, init_db, drop_db
from models import (
    User, UserSkill, UserPreference,
    FreelancePlatform,
    Client, ClientReview, ClientRedFlag,
    Job, JobApplication,
    CompanyResearch,
    ScamReport,
    SavedSearch,
    UserAnalytics, PlatformAnalytics
)


def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created successfully!")

        # Print created tables
        print("\nCreated tables:")
        for table in Base.metadata.sorted_tables:
            print(f"  - {table.name}")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        raise


def drop_tables():
    """Drop all database tables (use with caution!)"""
    print("⚠️  WARNING: This will delete all database tables and data!")
    confirm = input("Type 'yes' to confirm: ")

    if confirm.lower() == 'yes':
        print("Dropping all tables...")
        try:
            Base.metadata.drop_all(bind=engine)
            print("✅ All tables dropped successfully!")
        except Exception as e:
            print(f"❌ Error dropping tables: {e}")
            raise
    else:
        print("Operation cancelled.")


def reset_db():
    """Drop and recreate all tables"""
    print("⚠️  WARNING: This will delete all data and recreate tables!")
    confirm = input("Type 'yes' to confirm: ")

    if confirm.lower() == 'yes':
        drop_tables()
        create_tables()
    else:
        print("Operation cancelled.")


def seed_platforms():
    """Seed initial freelance platforms"""
    from sqlalchemy.orm import Session
    from models.base import SessionLocal

    db = SessionLocal()

    try:
        # Check if platforms already exist
        existing = db.query(FreelancePlatform).count()
        if existing > 0:
            print(f"Platforms already seeded ({existing} platforms found)")
            return

        platforms = [
            FreelancePlatform(
                name="Upwork",
                base_url="https://www.upwork.com",
                has_api=False,
                scraper_enabled=True
            ),
            FreelancePlatform(
                name="Freelancer",
                base_url="https://www.freelancer.com",
                has_api=False,
                scraper_enabled=True
            ),
            FreelancePlatform(
                name="Fiverr",
                base_url="https://www.fiverr.com",
                has_api=False,
                scraper_enabled=True
            ),
            FreelancePlatform(
                name="Guru",
                base_url="https://www.guru.com",
                has_api=False,
                scraper_enabled=True
            ),
        ]

        db.add_all(platforms)
        db.commit()
        print(f"✅ Seeded {len(platforms)} freelance platforms")

    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding platforms: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Database management script')
    parser.add_argument('action', choices=['create', 'drop', 'reset', 'seed'],
                       help='Action to perform: create, drop, reset, or seed')

    args = parser.parse_args()

    if args.action == 'create':
        create_tables()
    elif args.action == 'drop':
        drop_tables()
    elif args.action == 'reset':
        reset_db()
    elif args.action == 'seed':
        seed_platforms()
