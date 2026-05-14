import logging
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import Company, JobSeekerProfile, RefreshToken, User, UserRole
from app.schemas import GoogleAuthRequest, LoginRequest, RefreshRequest, RegisterRequest, TokenPair, UserOut
from app.security import create_access_token, create_refresh_token, hash_password, hash_token, verify_password

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenPair)
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    if not body.email and not body.phone:
        raise HTTPException(400, "Email or phone required")
    role = UserRole.job_seeker if body.role.value == "job_seeker" else UserRole.employer
    if body.email and db.query(User).filter(User.email == str(body.email)).first():
        raise HTTPException(409, "Email already registered")
    if body.phone and db.query(User).filter(User.phone == body.phone).first():
        raise HTTPException(409, "Phone already registered")

    user = User(
        email=str(body.email) if body.email else None,
        phone=body.phone,
        hashed_password=hash_password(body.password),
        role=role,
    )
    db.add(user)
    db.flush()
    if role == UserRole.job_seeker:
        db.add(JobSeekerProfile(user_id=user.id, full_name="", headline=""))
    else:
        db.add(Company(owner_user_id=user.id, name="My Company"))
    db.commit()
    db.refresh(user)
    return _issue_tokens(db, user)


@router.post("/login", response_model=TokenPair)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    if not body.email and not body.phone:
        raise HTTPException(400, "Email or phone required")
    q = db.query(User)
    user = None
    if body.email:
        user = q.filter(User.email == str(body.email)).first()
    if not user and body.phone:
        user = q.filter(User.phone == body.phone).first()
    if not user or not user.hashed_password or not verify_password(body.password, user.hashed_password):
        raise HTTPException(401, "Invalid credentials")
    return _issue_tokens(db, user)


@router.post("/google", response_model=TokenPair)
def google_auth(body: GoogleAuthRequest, db: Session = Depends(get_db)):
    from app.config import get_settings

    settings = get_settings()
    if not settings.google_client_id:
        raise HTTPException(503, "Google OAuth not configured")
    try:
        info = google_id_token.verify_oauth2_token(
            body.id_token,
            google_requests.Request(),
            settings.google_client_id,
        )
    except ValueError as e:
        raise HTTPException(401, f"Invalid Google token: {e}") from e
    sub = info.get("sub")
    email = info.get("email")
    if not sub:
        raise HTTPException(401, "Invalid token payload")
    user = db.query(User).filter(User.google_sub == sub).first()
    if not user and email:
        user = db.query(User).filter(User.email == email).first()
        if user:
            user.google_sub = sub
    if not user:
        # default new Google users to job_seeker; they can request employer upgrade (admin) in real product
        user = User(email=email, google_sub=sub, role=UserRole.job_seeker, hashed_password=None)
        db.add(user)
        db.flush()
        db.add(JobSeekerProfile(user_id=user.id, full_name=info.get("name") or "", headline=""))
    db.commit()
    db.refresh(user)
    return _issue_tokens(db, user)


@router.post("/refresh", response_model=TokenPair)
def refresh(body: RefreshRequest, db: Session = Depends(get_db)):
    h = hash_token(body.refresh_token)
    row = db.query(RefreshToken).filter(RefreshToken.token_hash == h).first()
    if not row or row.expires_at < datetime.now(timezone.utc):
        raise HTTPException(401, "Invalid refresh token")
    user = db.query(User).filter(User.id == row.user_id).first()
    if not user:
        raise HTTPException(401, "User missing")
    db.delete(row)
    db.commit()
    return _issue_tokens(db, user)


def _issue_tokens(db: Session, user: User) -> TokenPair:
    from app.config import get_settings

    settings = get_settings()
    access = create_access_token(str(user.id), {"role": user.role.value})
    refresh = create_refresh_token()
    exp = datetime.now(timezone.utc) + timedelta(days=settings.jwt_refresh_expire_days)
    db.add(RefreshToken(user_id=user.id, token_hash=hash_token(refresh), expires_at=exp))
    db.commit()
    return TokenPair(access_token=access, refresh_token=refresh)


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return UserOut(
        id=user.id,
        email=user.email,
        phone=user.phone,
        role=user.role.value,
        preferred_locale=user.preferred_locale,
    )
