"""Notify seekers when a new job matches saved JobAlert criteria (email/SMS)."""
from __future__ import annotations

import logging
from typing import Any

from sqlalchemy.orm import Session

from app.models import Job, JobAlert, User
from app.services.notifications import send_email, send_sms

logger = logging.getLogger(__name__)


def _matches(criteria: dict[str, Any], job: Job) -> bool:
    if criteria.get("city") and criteria["city"].lower() != job.city.lower():
        return False
    if criteria.get("category") and criteria["category"].lower() != job.category.lower():
        return False
    if criteria.get("job_type") and criteria["job_type"] != job.job_type.value:
        return False
    smin = criteria.get("salary_min")
    if smin is not None and job.salary_max_etb is not None and job.salary_max_etb < int(smin):
        return False
    smax = criteria.get("salary_max")
    if smax is not None and job.salary_min_etb is not None and job.salary_min_etb > int(smax):
        return False
    kw = criteria.get("keywords")
    if kw:
        blob = f"{job.title_en} {job.description_en}".lower()
        if str(kw).lower() not in blob:
            return False
    return True


async def dispatch_job_alerts(db: Session, job: Job) -> None:
    alerts = db.query(JobAlert).filter(JobAlert.is_active.is_(True)).all()
    for a in alerts:
        if not _matches(a.criteria or {}, job):
            continue
        user = db.query(User).filter(User.id == a.seeker_user_id).first()
        if not user:
            continue
        subject = f"New job match: {job.title_en}"
        html = f"<p>A new job may match your alert <b>{a.name}</b>.</p><p>{job.title_en} — {job.city}</p>"
        if a.notify_email and user.email:
            try:
                await send_email(user.email, subject, html)
            except Exception as e:
                logger.exception("email alert failed: %s", e)
        if a.notify_sms and user.phone:
            body = f"Job alert: {job.title_en} in {job.city}. Log in to apply."
            phone = user.phone if user.phone.startswith("+") else f"+251{user.phone.lstrip('0')}"
            try:
                await send_sms(phone, body)
            except Exception as e:
                logger.exception("sms alert failed: %s", e)
