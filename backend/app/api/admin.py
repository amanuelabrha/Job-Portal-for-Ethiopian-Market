from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import require_roles
from app.models import Job, User, UserRole

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users")
def list_users(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin)),
):
    rows = db.query(User).order_by(User.id.desc()).limit(200).all()
    return [
        {
            "id": u.id,
            "email": u.email,
            "phone": u.phone,
            "role": u.role.value,
            "is_active": u.is_active,
        }
        for u in rows
    ]


@router.patch("/users/{user_id}/active")
def set_user_active(
    user_id: int,
    active: bool,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin)),
):
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(404, "User not found")
    u.is_active = active
    db.commit()
    return {"ok": True}


@router.get("/jobs")
def list_jobs_admin(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin)),
):
    rows = db.query(Job).order_by(Job.id.desc()).limit(200).all()
    return [
        {
            "id": j.id,
            "title_en": j.title_en,
            "city": j.city,
            "is_published": j.is_published,
            "is_premium": j.is_premium,
        }
        for j in rows
    ]
