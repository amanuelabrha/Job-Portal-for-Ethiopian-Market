"""Seed Ethiopian cities, categories, sample employer jobs, and admin user."""
from __future__ import annotations

import logging

from app.database import SessionLocal, engine, Base
from app.models import Company, Job, JobSeekerProfile, JobType, User, UserRole
from app.security import hash_password

logger = logging.getLogger(__name__)

ETHIOPIAN_CITIES = [
    "Addis Ababa",
    "Bahir Dar",
    "Mekelle",
    "Hawassa",
    "Dire Dawa",
    "Gondar",
    "Adama",
    "Jimma",
    "Dessie",
    "Jijiga",
]

JOB_CATEGORIES = [
    "Technology",
    "Finance",
    "Healthcare",
    "Education",
    "Engineering",
    "Sales & Marketing",
    "NGO",
    "Hospitality",
    "Government",
    "Manufacturing",
]


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(User).filter(User.email == "admin@ethiojobs.et").first():
            logger.info("Seed already applied (admin exists).")
            return

        admin = User(
            email="admin@ethiojobs.et",
            phone=None,
            hashed_password=hash_password("Admin12345!"),
            role=UserRole.admin,
        )
        db.add(admin)

        emp_user = User(
            email="employer@ethiojobs.et",
            hashed_password=hash_password("Employer123!"),
            role=UserRole.employer,
        )
        db.add(emp_user)
        db.flush()

        company = Company(
            owner_user_id=emp_user.id,
            name="Ethio Tech Solutions",
            description="Sample employer — software and fintech in Addis Ababa.",
            website="https://example.et",
            verified=True,
        )
        db.add(company)
        db.flush()

        jobs_data = [
            (
                "Senior Backend Engineer",
                "ሲኒየር ባክኤንድ መሐንዲስ",
                "Build APIs with FastAPI/PostgreSQL. Remote-friendly within Ethiopia.",
                "FastAPI, PostgreSQL, Docker experience. English required; Amharic a plus.",
                "Technology",
                "Addis Ababa",
                80_000,
                120_000,
                JobType.full_time,
            ),
            (
                "Field Sales Representative",
                None,
                "Represent our FMCG brand across Addis and regional cities.",
                "2+ years sales, valid driving license, Amharic fluency.",
                "Sales & Marketing",
                "Hawassa",
                18_000,
                28_000,
                JobType.full_time,
            ),
            (
                "Remote Customer Support",
                None,
                "Support customers via chat and phone, UTC+3 hours.",
                "Strong Amharic and English, empathy, prior BPO experience preferred.",
                "Technology",
                "Addis Ababa",
                12_000,
                18_000,
                JobType.remote,
            ),
        ]
        for title_en, title_am, desc, req, cat, city, smin, smax, jt in jobs_data:
            db.add(
                Job(
                    company_id=company.id,
                    title_en=title_en,
                    title_am=title_am,
                    description_en=desc,
                    description_am=None,
                    requirements_en=req,
                    requirements_am=None,
                    category=cat,
                    city=city,
                    salary_min_etb=smin,
                    salary_max_etb=smax,
                    job_type=jt,
                    is_published=True,
                    is_premium=title_en.startswith("Senior"),
                )
            )

        seeker = User(
            email="seeker@ethiojobs.et",
            hashed_password=hash_password("Seeker123!"),
            role=UserRole.job_seeker,
        )
        db.add(seeker)
        db.flush()
        db.add(
            JobSeekerProfile(
                user_id=seeker.id,
                full_name="Meron Tadesse",
                headline="Full-stack developer",
                bio="Passionate about products for the Ethiopian market.",
                portfolio_urls=["https://github.com/example"],
            )
        )

        db.commit()
        logger.info("Seed complete: %d cities, %d categories", len(ETHIOPIAN_CITIES), len(JOB_CATEGORIES))
    finally:
        db.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seed()
