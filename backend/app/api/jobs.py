import hashlib
import json
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.deps import get_current_user, get_redis, require_roles
from app.models import Application, ApplicationStatus, Company, Job, JobSeekerProfile, JobType, JobView, User, UserRole
from app.schemas import ApplicationCreate, ApplicationOut, JobListFilters, JobOut
from app.services.matching import build_job_text, build_candidate_text, compute_match_score

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/jobs", tags=["jobs"])


def _job_to_out(job: Job) -> JobOut:
    company_name = job.company.name if job.company else ""
    return JobOut(
        id=job.id,
        company_id=job.company_id,
        company_name=company_name,
        title_en=job.title_en,
        title_am=job.title_am,
        description_en=job.description_en,
        description_am=job.description_am,
        requirements_en=job.requirements_en,
        requirements_am=job.requirements_am,
        category=job.category,
        city=job.city,
        salary_min_etb=job.salary_min_etb,
        salary_max_etb=job.salary_max_etb,
        job_type=job.job_type.value,
        deadline=job.deadline,
        is_premium=job.is_premium,
        view_count=job.view_count,
        application_count=job.application_count_cached,
        created_at=job.created_at,
    )


@router.get("", response_model=list[JobOut])
def list_jobs(
    city: Optional[str] = None,
    category: Optional[str] = None,
    salary_min: Optional[int] = None,
    salary_max: Optional[int] = None,
    job_type: Optional[str] = None,
    q: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    redis_client=Depends(get_redis),
):
    """Public job search — cached in Redis for low-bandwidth regions."""
    filters = JobListFilters(
        city=city, category=category, salary_min=salary_min, salary_max=salary_max, job_type=job_type, q=q
    )
    cache_key = f"jobs:list:{hashlib.md5(json.dumps(filters.model_dump(), sort_keys=True).encode()).hexdigest()}:{page}:{page_size}"
    cached = redis_client.get(cache_key)
    if cached:
        data = json.loads(cached)
        return [JobOut.model_validate(x) for x in data]

    query = (
        db.query(Job)
        .options(joinedload(Job.company))
        .filter(Job.is_published.is_(True))
        .order_by(Job.is_premium.desc(), Job.created_at.desc())
    )
    if city:
        query = query.filter(Job.city.ilike(f"%{city}%"))
    if category:
        query = query.filter(Job.category.ilike(f"%{category}%"))
    if salary_min is not None:
        query = query.filter(or_(Job.salary_max_etb.is_(None), Job.salary_max_etb >= salary_min))
    if salary_max is not None:
        query = query.filter(or_(Job.salary_min_etb.is_(None), Job.salary_min_etb <= salary_max))
    if job_type:
        query = query.filter(Job.job_type == JobType(job_type))
    if q:
        like = f"%{q}%"
        query = query.filter(or_(Job.title_en.ilike(like), Job.description_en.ilike(like)))

    rows = query.offset((page - 1) * page_size).limit(page_size).all()
    out = [_job_to_out(j) for j in rows]
    redis_client.setex(cache_key, 60, json.dumps([o.model_dump(mode="json") for o in out], default=str))
    return out


@router.get("/{job_id}", response_model=JobOut)
def get_job(job_id: int, request: Request, db: Session = Depends(get_db)):
    job = db.query(Job).options(joinedload(Job.company)).filter(Job.id == job_id).first()
    if not job or not job.is_published:
        raise HTTPException(404, "Job not found")
    # analytics: simple view tracking (hashed IP for privacy)
    ip = request.client.host if request.client else "anon"
    vk = hashlib.sha256(ip.encode()).hexdigest()[:16]
    db.add(JobView(job_id=job.id, viewer_key=vk))
    job.view_count += 1
    db.commit()
    return _job_to_out(job)


@router.post("/{job_id}/apply", response_model=ApplicationOut)
def apply_job(
    job_id: int,
    body: ApplicationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.job_seeker)),
):
    job = db.query(Job).options(joinedload(Job.company)).filter(Job.id == job_id).first()
    if not job or not job.is_published:
        raise HTTPException(404, "Job not found")
    exists = (
        db.query(Application).filter(Application.job_id == job.id, Application.seeker_user_id == user.id).first()
    )
    if exists:
        raise HTTPException(409, "Already applied")

    profile = (
        db.query(JobSeekerProfile)
        .options(joinedload(JobSeekerProfile.skills))
        .filter(JobSeekerProfile.user_id == user.id)
        .first()
    )
    if not profile:
        raise HTTPException(400, "Complete your profile first")

    resume_snap = profile.resume_path if body.use_profile_resume else None
    if body.use_profile_resume and not resume_snap:
        raise HTTPException(400, "No resume on profile")

    job_text = build_job_text(job.title_en, job.description_en, job.requirements_en)
    skills = [s.name for s in profile.skills]
    cand_text = build_candidate_text(
        f"{profile.headline}\n{profile.bio or ''}",
        profile.resume_text or "",
        skills,
    )
    score = compute_match_score(job_text, cand_text)

    app = Application(
        job_id=job.id,
        seeker_user_id=user.id,
        cover_letter=body.cover_letter,
        resume_path_snapshot=resume_snap,
        match_score=score,
        status=ApplicationStatus.submitted,
    )
    db.add(app)
    job.application_count_cached += 1
    db.commit()
    db.refresh(app)
    return ApplicationOut(
        id=app.id,
        job_id=app.job_id,
        status=app.status.value,
        match_score=app.match_score,
        created_at=app.created_at,
        job_title=job.title_en,
    )
