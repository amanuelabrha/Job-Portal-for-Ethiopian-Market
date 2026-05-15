"""Rich demo dataset for presentations — Ethiopian market sample data."""
from __future__ import annotations

import logging
import sys
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.database import Base, SessionLocal, engine
from app.demo_constants import (
    DEMO_ADMIN_EMAIL,
    DEMO_ADMIN_PASSWORD,
    DEMO_EMPLOYER_EMAIL,
    DEMO_EMPLOYER_PASSWORD,
    DEMO_SEEKER_EMAIL,
    DEMO_SEEKER_NAME,
    DEMO_SEEKER_PASSWORD,
    DEMO_SEEKER_PHONE,
)
from app.models import (
    Application,
    ApplicationStatus,
    Company,
    Education,
    Experience,
    Job,
    JobAlert,
    JobSeekerProfile,
    JobType,
    JobView,
    Skill,
    User,
    UserRole,
)
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

AMANUEL_RESUME_TEXT = """
Amanuel Abrha
Software Engineer | Addis Ababa, Ethiopia
amanuelabrha02@gmail.com | +251 911 234 567

SUMMARY
Full-stack developer building products for the Ethiopian market. Experience with React,
Next.js, Python, FastAPI, PostgreSQL, and mobile-first web apps.

EXPERIENCE
Junior Software Engineer — Ethio Digital Labs, Addis Ababa (2023–2025)
Built job portal and payment integrations; REST APIs; Docker deployments.

Intern Developer — Addis Tech Hub (2022–2023)
React dashboards, Amharic localization, ETB pricing modules.

EDUCATION
BSc Computer Science — Addis Ababa University (2022)

SKILLS
Python, JavaScript, TypeScript, React, Next.js, FastAPI, SQL, PostgreSQL, Redis,
Docker, Git, Amharic, English
""".strip()


def _clear_demo_data(db: Session) -> None:
    """Remove all rows so --force can rebuild a clean showcase dataset."""
    db.query(Application).delete()
    db.query(JobView).delete()
    db.query(JobAlert).delete()
    db.query(Job).delete()
    db.query(Skill).delete()
    db.query(Education).delete()
    db.query(Experience).delete()
    db.query(JobSeekerProfile).delete()
    db.query(Company).delete()
    db.query(User).delete()
    db.commit()


def _add_skills(db: Session, profile: JobSeekerProfile, names: list[str]) -> None:
    for name in names:
        db.add(Skill(profile_id=profile.id, name=name))


def seed(force: bool = False) -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        demo_exists = db.query(User).filter(User.email == DEMO_SEEKER_EMAIL).first()
        if demo_exists and not force:
            logger.info("Demo data already loaded (%s). Run: python -m app.seed --force", DEMO_SEEKER_EMAIL)
            return
        if force or demo_exists:
            logger.info("Rebuilding demo database…")
            _clear_demo_data(db)

        pw = hash_password(DEMO_SEEKER_PASSWORD)

        admin = User(
            email=DEMO_ADMIN_EMAIL,
            hashed_password=hash_password(DEMO_ADMIN_PASSWORD),
            role=UserRole.admin,
            preferred_locale="en",
        )
        db.add(admin)

        # --- Employers & companies ---
        employers_spec = [
            (
                DEMO_EMPLOYER_EMAIL,
                hash_password(DEMO_EMPLOYER_PASSWORD),
                "Ethio Tech Solutions PLC",
                "Leading software and fintech employer in Addis Ababa. Builds digital services for Ethiopian businesses.",
                "https://ethiotech.example.et",
            ),
            (
                "hr@dashenbank.et",
                hash_password("Dashen123!"),
                "Dashen Bank",
                "One of Ethiopia's largest private banks — careers in finance, IT, and branch operations nationwide.",
                "https://dashenbanksc.com",
            ),
            (
                "careers@tomoca.et",
                hash_password("Tomoca123!"),
                "Tomoca Coffee",
                "Iconic Addis Ababa coffee brand — hospitality, retail, and supply chain roles.",
                "https://tomocacoffee.com",
            ),
            (
                "jobs@hawassa-industrial.et",
                hash_password("Hawassa123!"),
                "Hawassa Industrial Park",
                "Manufacturing and export-oriented jobs in Hawassa and surrounding areas.",
                None,
            ),
        ]
        companies: list[Company] = []
        for email, hpw, cname, cdesc, web in employers_spec:
            u = User(email=email, hashed_password=hpw, role=UserRole.employer, preferred_locale="en")
            db.add(u)
            db.flush()
            c = Company(
                owner_user_id=u.id,
                name=cname,
                description=cdesc,
                website=web,
                verified=True,
            )
            db.add(c)
            db.flush()
            companies.append(c)

        deadline = datetime.now(timezone.utc) + timedelta(days=45)
        jobs_spec: list[tuple] = [
            # (company_idx, title_en, title_am, desc, req, cat, city, smin, smax, jtype, premium, views, apps)
            (
                0,
                "Senior Full-Stack Developer",
                "ሲኒየር ፉል-ስታክ ገንቢ",
                "Design and ship features for our Ethiopia job platform and employer dashboards. Stack: React, Next.js, FastAPI, PostgreSQL, Redis. Hybrid from Bole, Addis Ababa.",
                "3+ years web development. Python or Node backend. Amharic UI experience is a plus. Portfolio required.",
                "Technology",
                "Addis Ababa",
                45_000,
                75_000,
                JobType.full_time,
                True,
                420,
                18,
            ),
            (
                0,
                "DevOps Engineer",
                "የዴቭኦፕስ መሐንዲስ",
                "Maintain CI/CD, Docker, and AWS deployments for Ethiopian customers. On-call rotation shared across team (UTC+3).",
                "Docker, Linux, GitHub Actions, basic Terraform. Experience with low-bandwidth optimization preferred.",
                "Technology",
                "Addis Ababa",
                50_000,
                85_000,
                JobType.full_time,
                False,
                210,
                9,
            ),
            (
                0,
                "UI/UX Designer (Amharic)",
                "የ UI/UX ዲዛይነር",
                "Create mobile-first flows for job seekers and employers. Must design for Amharic script and ETB salary displays.",
                "Figma, design systems, 2+ years product design. Samples in English and Amharic.",
                "Technology",
                "Addis Ababa",
                28_000,
                42_000,
                JobType.full_time,
                False,
                156,
                11,
            ),
            (
                1,
                "Junior Banking Officer",
                "ጁኒየር ባንክ ኦፊሰር",
                "Customer service and account operations at branches in Addis Ababa. Training provided on core banking systems.",
                "Bachelor's in Business, Finance, or related. Fluent Amharic and English. Fresh graduates welcome.",
                "Finance",
                "Addis Ababa",
                12_000,
                18_000,
                JobType.full_time,
                False,
                890,
                67,
            ),
            (
                1,
                "IT Support Specialist",
                "የአይቲ ድጋፍ ስፔሻሊስት",
                "Support branch networks, ATMs, and digital banking apps across Ethiopia.",
                "Diploma or degree in IT. Troubleshooting Windows/Linux. Driver's license preferred.",
                "Finance",
                "Bahir Dar",
                15_000,
                22_000,
                JobType.full_time,
                False,
                134,
                8,
            ),
            (
                2,
                "Barista & Shift Lead",
                "ባሪስታ እና ሽፍት መሪ",
                "Prepare specialty coffee, train new staff, maintain quality at our Kazanchis flagship store.",
                "1+ year hospitality. Friendly service. Amharic required.",
                "Hospitality",
                "Addis Ababa",
                8_000,
                12_000,
                JobType.full_time,
                False,
                340,
                44,
            ),
            (
                2,
                "Supply Chain Coordinator",
                None,
                "Coordinate green coffee logistics from regions to Addis roasting facilities.",
                "Excel, communication skills, willingness to travel to Sidama and Yirgacheffe areas.",
                "Manufacturing",
                "Addis Ababa",
                14_000,
                20_000,
                JobType.full_time,
                False,
                88,
                5,
            ),
            (
                3,
                "Production Line Supervisor",
                "የምርት መስመር ተቆጣጣሪ",
                "Supervise textile production lines; safety and quality KPIs.",
                "Engineering or industrial experience 2+ years. Leadership in factory setting.",
                "Manufacturing",
                "Hawassa",
                16_000,
                24_000,
                JobType.full_time,
                False,
                201,
                14,
            ),
            (
                3,
                "Warehouse Associate",
                None,
                "Inventory, packing, and ERP data entry. Day shift.",
                "High school or TVET. Basic English. Physical stamina.",
                "Manufacturing",
                "Hawassa",
                7_000,
                10_000,
                JobType.part_time,
                False,
                95,
                22,
            ),
            (
                0,
                "Remote Customer Success (ET)",
                "የደንበኞች ስኬት",
                "Support employers posting jobs via chat, email, and phone. Work from anywhere in Ethiopia (UTC+3).",
                "Excellent Amharic and English. CRM experience. Empathy and clear writing.",
                "Sales & Marketing",
                "Addis Ababa",
                11_000,
                16_000,
                JobType.remote,
                False,
                178,
                12,
            ),
            (
                1,
                "Data Analyst — Digital Banking",
                "የውሂብ ተንታኝ",
                "Build dashboards for mobile money and branch performance using SQL and Python.",
                "SQL, Excel, Python or R. Statistics coursework. Portfolio of 1–2 projects.",
                "Finance",
                "Addis Ababa",
                22_000,
                35_000,
                JobType.full_time,
                True,
                267,
                15,
            ),
            (
                0,
                "Mobile App Developer (Flutter)",
                None,
                "Ship Android-first apps for Ethiopian users on slower networks. Integrate Chapa/Telebirr payment stubs.",
                "Flutter/Dart, REST APIs, offline-first patterns.",
                "Technology",
                "Addis Ababa",
                35_000,
                55_000,
                JobType.contract,
                False,
                143,
                7,
            ),
        ]

        created_jobs: list[Job] = []
        for spec in jobs_spec:
            cidx, title_en, title_am, desc, req, cat, city, smin, smax, jt, prem, views, apps = spec
            j = Job(
                company_id=companies[cidx].id,
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
                deadline=deadline,
                is_published=True,
                is_premium=prem,
                view_count=views,
                application_count_cached=apps,
            )
            db.add(j)
            db.flush()
            created_jobs.append(j)

        # --- Primary demo seeker: Amanuel ---
        amanuel = User(
            email=DEMO_SEEKER_EMAIL,
            phone=DEMO_SEEKER_PHONE,
            hashed_password=pw,
            role=UserRole.job_seeker,
            preferred_locale="en",
        )
        db.add(amanuel)
        db.flush()

        amanuel_profile = JobSeekerProfile(
            user_id=amanuel.id,
            full_name=DEMO_SEEKER_NAME,
            headline="Full-Stack Developer · React & Python · Addis Ababa",
            bio=(
                "I build scalable web applications for the Ethiopian market — bilingual UI (English/Amharic), "
                "ETB payments, and mobile-first design. Open to full-time and remote roles across Ethiopia."
            ),
            portfolio_urls=[
                "https://github.com/amanuelabrha",
                "https://linkedin.com/in/amanuelabrha",
            ],
            resume_text=AMANUEL_RESUME_TEXT,
            parsed_cv={
                "skills_guess": ["Python", "React", "Next.js", "FastAPI", "PostgreSQL", "TypeScript"],
                "education_guess": [{"institution": "Addis Ababa University", "degree": "BSc Computer Science"}],
            },
        )
        db.add(amanuel_profile)
        db.flush()

        _add_skills(
            db,
            amanuel_profile,
            [
                "Python",
                "JavaScript",
                "TypeScript",
                "React",
                "Next.js",
                "FastAPI",
                "PostgreSQL",
                "Redis",
                "Docker",
                "Git",
                "Amharic",
                "English",
                "REST APIs",
                "Tailwind CSS",
            ],
        )
        for inst, deg, field, yr in [
            ("Addis Ababa University", "BSc", "Computer Science", 2022),
            ("Ethio National School", "High School", "Natural Science", 2018),
        ]:
            db.add(
                Education(
                    profile_id=amanuel_profile.id,
                    institution=inst,
                    degree=deg,
                    field=field,
                    year_end=yr,
                )
            )
        for comp, title, desc, sy, ey in [
            (
                "Ethio Digital Labs",
                "Junior Software Engineer",
                "Built APIs and employer dashboards for Ethiopian clients.",
                2023,
                2025,
            ),
            (
                "Addis Tech Hub",
                "Intern Developer",
                "React apps with Amharic localization and ETB formatting.",
                2022,
                2023,
            ),
        ]:
            db.add(
                Experience(
                    profile_id=amanuel_profile.id,
                    company=comp,
                    title=title,
                    description=desc,
                    start_year=sy,
                    end_year=ey,
                )
            )

        # --- Second seeker for employer applicant lists ---
        meron = User(
            email="meron.tadesse@example.et",
            phone="+251922345678",
            hashed_password=hash_password("Demo12345!"),
            role=UserRole.job_seeker,
            preferred_locale="am",
        )
        db.add(meron)
        db.flush()
        meron_p = JobSeekerProfile(
            user_id=meron.id,
            full_name="Meron Tadesse",
            headline="Product Manager · NGO & EdTech",
            bio="Experienced PM focused on education and NGO programs in Ethiopia.",
            portfolio_urls=["https://linkedin.com/in/meron-example"],
            resume_text="Meron Tadesse product manager agile amharic english NGO education",
        )
        db.add(meron_p)
        db.flush()
        _add_skills(db, meron_p, ["Product Management", "Agile", "Amharic", "English", "Stakeholder Management"])

        # --- Applications for Amanuel (showcase pipeline) ---
        job_fullstack = created_jobs[0]
        job_devops = created_jobs[1]
        job_remote = created_jobs[9]
        job_data = created_jobs[10]

        applications_spec = [
            (job_fullstack.id, amanuel.id, ApplicationStatus.shortlisted, 0.78, "Excited to contribute to Ethio Tech's platform."),
            (job_devops.id, amanuel.id, ApplicationStatus.submitted, 0.52, None),
            (job_remote.id, amanuel.id, ApplicationStatus.submitted, 0.61, "Available for remote work from Addis Ababa."),
            (job_data.id, amanuel.id, ApplicationStatus.rejected, 0.41, None),
            (job_fullstack.id, meron.id, ApplicationStatus.submitted, 0.35, "Career switch — eager to learn engineering practices."),
        ]
        for jid, uid, status, score, cover in applications_spec:
            db.add(
                Application(
                    job_id=jid,
                    seeker_user_id=uid,
                    status=status,
                    match_score=score,
                    cover_letter=cover,
                    resume_path_snapshot="demo/resume.pdf",
                )
            )

        db.add(
            JobAlert(
                seeker_user_id=amanuel.id,
                name="Addis Tech Jobs",
                criteria={
                    "city": "Addis Ababa",
                    "category": "Technology",
                    "salary_min": 30000,
                    "job_type": "full_time",
                    "keywords": "developer",
                },
                notify_email=True,
                notify_sms=True,
            )
        )
        db.add(
            JobAlert(
                seeker_user_id=amanuel.id,
                name="Remote roles",
                criteria={"job_type": "remote", "keywords": "remote"},
                notify_email=True,
                notify_sms=False,
            )
        )

        db.commit()
        logger.info(
            "Demo seed complete: seeker=%s | %d jobs | %d companies",
            DEMO_SEEKER_EMAIL,
            len(created_jobs),
            len(companies),
        )
    finally:
        db.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    force = "--force" in sys.argv
    seed(force=force)
