import logging
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session, joinedload

from app.config import get_settings
from app.database import get_db
from app.deps import get_current_user, get_redis, require_roles
from app.models import (
    Application,
    Education,
    Experience,
    JobAlert,
    JobSeekerProfile,
    Skill,
    User,
    UserRole,
)
from app.schemas import JobAlertCreate, SeekerProfileOut, SeekerProfileUpdate, ApplicationOut
from app.services.cv_parser import parse_resume_bytes
from app.services.malware_scan import scan_bytes
from app.services.storage import save_resume_file

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/seeker", tags=["seeker"])


def _profile_out(p: JobSeekerProfile) -> SeekerProfileOut:
    return SeekerProfileOut(
        full_name=p.full_name,
        headline=p.headline,
        bio=p.bio,
        portfolio_urls=list(p.portfolio_urls or []),
        resume_path=p.resume_path,
        parsed_cv=p.parsed_cv,
        skills=[s.name for s in p.skills],
        preferred_locale=p.user.preferred_locale if p.user else "en",
    )


@router.get("/profile", response_model=SeekerProfileOut)
def get_profile(db: Session = Depends(get_db), user: User = Depends(require_roles(UserRole.job_seeker))):
    p = (
        db.query(JobSeekerProfile)
        .options(joinedload(JobSeekerProfile.skills), joinedload(JobSeekerProfile.user))
        .filter(JobSeekerProfile.user_id == user.id)
        .first()
    )
    if not p:
        raise HTTPException(404, "Profile missing")
    return _profile_out(p)


@router.patch("/profile", response_model=SeekerProfileOut)
def update_profile(
    body: SeekerProfileUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.job_seeker)),
):
    p = db.query(JobSeekerProfile).filter(JobSeekerProfile.user_id == user.id).first()
    if not p:
        raise HTTPException(404, "Profile missing")
    if body.full_name is not None:
        p.full_name = body.full_name
    if body.headline is not None:
        p.headline = body.headline
    if body.bio is not None:
        p.bio = body.bio
    if body.portfolio_urls is not None:
        p.portfolio_urls = body.portfolio_urls
    if body.preferred_locale is not None:
        user.preferred_locale = body.preferred_locale
    if body.skills is not None:
        db.query(Skill).filter(Skill.profile_id == p.id).delete()
        for name in body.skills:
            db.add(Skill(profile_id=p.id, name=name.strip()[:128]))
    if body.education is not None:
        db.query(Education).filter(Education.profile_id == p.id).delete()
        for e in body.education:
            db.add(
                Education(
                    profile_id=p.id,
                    institution=e.institution,
                    degree=e.degree,
                    field=e.field,
                    year_end=e.year_end,
                )
            )
    if body.experience is not None:
        db.query(Experience).filter(Experience.profile_id == p.id).delete()
        for x in body.experience:
            db.add(
                Experience(
                    profile_id=p.id,
                    company=x.company,
                    title=x.title,
                    description=x.description,
                    start_year=x.start_year,
                    end_year=x.end_year,
                )
            )
    db.commit()
    db.refresh(p)
    p = (
        db.query(JobSeekerProfile)
        .options(joinedload(JobSeekerProfile.skills), joinedload(JobSeekerProfile.user))
        .filter(JobSeekerProfile.user_id == user.id)
        .first()
    )
    return _profile_out(p)


@router.post("/resume")
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.job_seeker)),
):
    """Upload PDF/DOCX (max 5MB). Parses text + skills for matching — ET market often mixed-language."""
    settings = get_settings()
    if not file.filename:
        raise HTTPException(400, "Filename required")
    data = await file.read()
    max_b = settings.max_upload_mb * 1024 * 1024
    if len(data) > max_b:
        raise HTTPException(413, f"File too large (max {settings.max_upload_mb}MB)")
    ext = file.filename.lower().split(".")[-1]
    if ext not in ("pdf", "docx"):
        raise HTTPException(400, "Only PDF or DOCX allowed")
    try:
        scan_bytes(data)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e

    try:
        structured = parse_resume_bytes(file.filename, data)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e

    path = save_resume_file(file.filename, data)
    p = db.query(JobSeekerProfile).filter(JobSeekerProfile.user_id == user.id).first()
    if not p:
        raise HTTPException(404, "Profile missing")
    p.resume_path = path
    p.resume_text = structured.get("full_text", "")[:200_000]
    p.parsed_cv = structured
    # merge guessed skills if profile has few skills
    guess = structured.get("skills_guess") or []
    existing = {s.name.lower() for s in p.skills}
    for s in guess:
        if s.lower() not in existing:
            db.add(Skill(profile_id=p.id, name=s[:128]))
            existing.add(s.lower())
    db.commit()
    return {"resume_path": path, "parsed": structured}


@router.get("/applications", response_model=list[ApplicationOut])
def my_applications(db: Session = Depends(get_db), user: User = Depends(require_roles(UserRole.job_seeker))):
    rows = (
        db.query(Application)
        .options(joinedload(Application.job))
        .filter(Application.seeker_user_id == user.id)
        .order_by(Application.created_at.desc())
        .all()
    )
    out: list[ApplicationOut] = []
    for a in rows:
        out.append(
            ApplicationOut(
                id=a.id,
                job_id=a.job_id,
                status=a.status.value,
                match_score=a.match_score,
                created_at=a.created_at,
                job_title=a.job.title_en if a.job else None,
            )
        )
    return out


@router.post("/job-alerts")
def create_alert(
    body: JobAlertCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.job_seeker)),
):
    a = JobAlert(
        seeker_user_id=user.id,
        name=body.name,
        criteria=body.criteria,
        notify_email=body.notify_email,
        notify_sms=body.notify_sms,
    )
    db.add(a)
    db.commit()
    db.refresh(a)
    return {"id": a.id}


@router.get("/job-alerts")
def list_alerts(db: Session = Depends(get_db), user: User = Depends(require_roles(UserRole.job_seeker))):
    rows = db.query(JobAlert).filter(JobAlert.seeker_user_id == user.id).all()
    return [
        {
            "id": r.id,
            "name": r.name,
            "criteria": r.criteria,
            "notify_email": r.notify_email,
            "notify_sms": r.notify_sms,
            "is_active": r.is_active,
        }
        for r in rows
    ]
