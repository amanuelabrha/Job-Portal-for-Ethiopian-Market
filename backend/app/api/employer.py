import logging
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.database import SessionLocal, get_db
from app.deps import get_current_user, get_redis, require_roles
from app.models import (
    Application,
    ApplicationStatus,
    Company,
    Job,
    JobSeekerProfile,
    JobType,
    Message,
    User,
    UserRole,
)
from app.schemas import (
    AnalyticsSummary,
    ApplicantOut,
    ApplicationStatusUpdate,
    CompanyOut,
    CompanyUpdate,
    JobCreate,
    JobOut,
    JobUpdate,
    MessageCreate,
)
from app.services.job_alerts import dispatch_job_alerts
from app.services.matching import batch_scores, build_candidate_text, build_job_text

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/employer", tags=["employer"])


def _company_for(user: User, db: Session) -> Company:
    c = db.query(Company).filter(Company.owner_user_id == user.id).first()
    if not c:
        raise HTTPException(400, "Company not initialized")
    return c


def _job_out(job: Job) -> JobOut:
    return JobOut(
        id=job.id,
        company_id=job.company_id,
        company_name=job.company.name if job.company else "",
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


async def _notify_new_job(job_id: int) -> None:
    db = SessionLocal()
    try:
        job = db.query(Job).options(joinedload(Job.company)).filter(Job.id == job_id).first()
        if job:
            await dispatch_job_alerts(db, job)
            db.commit()
    finally:
        db.close()


def _bust_job_cache(redis_client) -> None:
    for k in redis_client.scan_iter("jobs:list:*"):
        redis_client.delete(k)


@router.get("/company", response_model=CompanyOut)
def get_company(db: Session = Depends(get_db), user: User = Depends(require_roles(UserRole.employer))):
    c = _company_for(user, db)
    return CompanyOut.model_validate(c)


@router.patch("/company", response_model=CompanyOut)
def patch_company(
    body: CompanyUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.employer)),
):
    c = _company_for(user, db)
    if body.name is not None:
        c.name = body.name
    if body.description is not None:
        c.description = body.description
    if body.website is not None:
        c.website = body.website
    db.commit()
    db.refresh(c)
    return CompanyOut.model_validate(c)


@router.post("/jobs", response_model=JobOut)
def create_job(
    body: JobCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    redis_client=Depends(get_redis),
    user: User = Depends(require_roles(UserRole.employer)),
):
    c = _company_for(user, db)
    try:
        jt = JobType(body.job_type)
    except ValueError as e:
        raise HTTPException(400, "Invalid job_type") from e
    job = Job(
        company_id=c.id,
        title_en=body.title_en,
        title_am=body.title_am,
        description_en=body.description_en,
        description_am=body.description_am,
        requirements_en=body.requirements_en,
        requirements_am=body.requirements_am,
        category=body.category,
        city=body.city,
        salary_min_etb=body.salary_min_etb,
        salary_max_etb=body.salary_max_etb,
        job_type=jt,
        deadline=body.deadline,
        is_published=body.is_published,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    job = db.query(Job).options(joinedload(Job.company)).filter(Job.id == job.id).first()
    _bust_job_cache(redis_client)
    background_tasks.add_task(_notify_new_job, job.id)
    return _job_out(job)


@router.get("/jobs", response_model=list[JobOut])
def my_jobs(db: Session = Depends(get_db), user: User = Depends(require_roles(UserRole.employer))):
    c = _company_for(user, db)
    rows = db.query(Job).options(joinedload(Job.company)).filter(Job.company_id == c.id).order_by(Job.created_at.desc()).all()
    return [_job_out(j) for j in rows]


@router.patch("/jobs/{job_id}", response_model=JobOut)
def update_job(
    job_id: int,
    body: JobUpdate,
    db: Session = Depends(get_db),
    redis_client=Depends(get_redis),
    user: User = Depends(require_roles(UserRole.employer)),
):
    c = _company_for(user, db)
    job = db.query(Job).options(joinedload(Job.company)).filter(Job.id == job_id, Job.company_id == c.id).first()
    if not job:
        raise HTTPException(404, "Job not found")
    data = body.model_dump(exclude_unset=True)
    if "job_type" in data and data["job_type"] is not None:
        try:
            job.job_type = JobType(data["job_type"])
        except ValueError as e:
            raise HTTPException(400, "Invalid job_type") from e
        del data["job_type"]
    for k, v in data.items():
        setattr(job, k, v)
    db.commit()
    db.refresh(job)
    _bust_job_cache(redis_client)
    return _job_out(job)


@router.get("/jobs/{job_id}/applicants", response_model=list[ApplicantOut])
def applicants(
    job_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.employer)),
):
    c = _company_for(user, db)
    job = db.query(Job).filter(Job.id == job_id, Job.company_id == c.id).first()
    if not job:
        raise HTTPException(404, "Job not found")
    apps = db.query(Application).filter(Application.job_id == job.id).all()
    job_text = build_job_text(job.title_en, job.description_en, job.requirements_en)
    cand_texts: list[str] = []
    meta: list[tuple[Application, User, str]] = []
    for a in apps:
        u = db.query(User).filter(User.id == a.seeker_user_id).first()
        if not u:
            continue
        prof = (
            db.query(JobSeekerProfile)
            .options(joinedload(JobSeekerProfile.skills))
            .filter(JobSeekerProfile.user_id == u.id)
            .first()
            if u
            else None
        )
        skills = [s.name for s in prof.skills] if prof else []
        blob = f"{prof.headline}\n{prof.bio or ''}" if prof else ""
        rt = prof.resume_text or "" if prof else ""
        ct = build_candidate_text(blob, rt, skills)
        cand_texts.append(ct)
        meta.append((a, u, prof.full_name if prof else ""))
    scores = batch_scores(job_text, cand_texts) if cand_texts else []
    out: list[ApplicantOut] = []
    for i, (a, u, name) in enumerate(meta):
        sc = float(scores[i]) if len(scores) else None
        a.match_score = sc
        out.append(
            ApplicantOut(
                application_id=a.id,
                seeker_user_id=a.seeker_user_id,
                full_name=name or (u.email if u else ""),
                email=u.email if u else None,
                match_score=sc,
                status=a.status.value,
                created_at=a.created_at,
            )
        )
    db.commit()
    out.sort(key=lambda x: x.match_score or 0.0, reverse=True)
    return out


@router.patch("/applications/{application_id}")
def update_application_status(
    application_id: int,
    body: ApplicationStatusUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.employer)),
):
    c = _company_for(user, db)
    app = (
        db.query(Application)
        .join(Job)
        .filter(Application.id == application_id, Job.company_id == c.id)
        .first()
    )
    if not app:
        raise HTTPException(404, "Application not found")
    try:
        app.status = ApplicationStatus(body.status)
    except ValueError as e:
        raise HTTPException(400, "Invalid status") from e
    db.commit()
    return {"ok": True}


@router.post("/messages")
def send_message(
    body: MessageCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.employer)),
):
    msg = Message(
        from_user_id=user.id,
        to_user_id=body.to_user_id,
        application_id=body.application_id,
        body=body.body,
    )
    db.add(msg)
    db.commit()
    return {"id": msg.id}


@router.get("/jobs/{job_id}/analytics", response_model=AnalyticsSummary)
def job_analytics(
    job_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.employer)),
):
    from app.models import JobView

    c = _company_for(user, db)
    job = db.query(Job).filter(Job.id == job_id, Job.company_id == c.id).first()
    if not job:
        raise HTTPException(404, "Job not found")
    views = db.query(JobView).filter(JobView.job_id == job.id).count()
    apps = db.query(Application).filter(Application.job_id == job.id).count()
    conv = (apps / views) if views else 0.0
    return AnalyticsSummary(total_views=views, total_applications=apps, conversion_rate=round(conv, 4))
