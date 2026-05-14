import enum
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class UserRole(str, enum.Enum):
    job_seeker = "job_seeker"
    employer = "employer"
    admin = "admin"


class JobType(str, enum.Enum):
    full_time = "full_time"
    part_time = "part_time"
    remote = "remote"
    contract = "contract"


class ApplicationStatus(str, enum.Enum):
    submitted = "submitted"
    shortlisted = "shortlisted"
    rejected = "rejected"
    hired = "hired"


class PaymentStatus(str, enum.Enum):
    pending = "pending"
    paid = "paid"
    failed = "failed"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True, index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(32), unique=True, nullable=True, index=True)
    hashed_password: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    google_sub: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, native_enum=False), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    preferred_locale: Mapped[str] = mapped_column(String(8), default="en")  # en | am | om ...
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    seeker_profile: Mapped[Optional["JobSeekerProfile"]] = relationship(back_populates="user", uselist=False)
    company: Mapped[Optional["Company"]] = relationship(back_populates="owner", uselist=False)


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    __table_args__ = (UniqueConstraint("token_hash", name="uq_refresh_hash"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    token_hash: Mapped[str] = mapped_column(String(128), index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    user: Mapped["User"] = relationship(back_populates="refresh_tokens")


class JobSeekerProfile(Base):
    __tablename__ = "job_seeker_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    full_name: Mapped[str] = mapped_column(String(255), default="")
    headline: Mapped[str] = mapped_column(String(512), default="")
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    portfolio_urls: Mapped[list] = mapped_column(JSON, default=list)  # list[str]
    resume_path: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    resume_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    parsed_cv: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # structured extraction
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    user: Mapped["User"] = relationship(back_populates="seeker_profile")
    education: Mapped[list["Education"]] = relationship(back_populates="profile", cascade="all, delete-orphan")
    experience: Mapped[list["Experience"]] = relationship(back_populates="profile", cascade="all, delete-orphan")
    skills: Mapped[list["Skill"]] = relationship(back_populates="profile", cascade="all, delete-orphan")


class Education(Base):
    __tablename__ = "education"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("job_seeker_profiles.id", ondelete="CASCADE"))
    institution: Mapped[str] = mapped_column(String(512))
    degree: Mapped[str] = mapped_column(String(255))
    field: Mapped[str] = mapped_column(String(255), default="")
    year_end: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    profile: Mapped["JobSeekerProfile"] = relationship(back_populates="education")


class Experience(Base):
    __tablename__ = "experience"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("job_seeker_profiles.id", ondelete="CASCADE"))
    company: Mapped[str] = mapped_column(String(512))
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    start_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    end_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    profile: Mapped["JobSeekerProfile"] = relationship(back_populates="experience")


class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("job_seeker_profiles.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(128), index=True)

    profile: Mapped["JobSeekerProfile"] = relationship(back_populates="skills")


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    name: Mapped[str] = mapped_column(String(512))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    owner: Mapped["User"] = relationship(back_populates="company")
    jobs: Mapped[list["Job"]] = relationship(back_populates="company", cascade="all, delete-orphan")


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), index=True)
    title_en: Mapped[str] = mapped_column(String(512))
    title_am: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    description_en: Mapped[str] = mapped_column(Text)
    description_am: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    requirements_en: Mapped[str] = mapped_column(Text, default="")
    requirements_am: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(128), index=True)
    city: Mapped[str] = mapped_column(String(128), index=True)
    salary_min_etb: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    salary_max_etb: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    job_type: Mapped[JobType] = mapped_column(Enum(JobType, native_enum=False), default=JobType.full_time)
    deadline: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True)
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    application_count_cached: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    company: Mapped["Company"] = relationship(back_populates="jobs")
    applications: Mapped[list["Application"]] = relationship(back_populates="job", cascade="all, delete-orphan")
    views: Mapped[list["JobView"]] = relationship(back_populates="job", cascade="all, delete-orphan")


class JobView(Base):
    __tablename__ = "job_views"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), index=True)
    viewer_key: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)  # hashed IP or user id
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    job: Mapped["Job"] = relationship(back_populates="views")


class Application(Base):
    __tablename__ = "applications"
    __table_args__ = (UniqueConstraint("job_id", "seeker_user_id", name="uq_job_seeker"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), index=True)
    seeker_user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    status: Mapped[ApplicationStatus] = mapped_column(
        Enum(ApplicationStatus, native_enum=False), default=ApplicationStatus.submitted
    )
    cover_letter: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    resume_path_snapshot: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    match_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # 0..1 TF-IDF cosine
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    job: Mapped["Job"] = relationship(back_populates="applications")


class JobAlert(Base):
    __tablename__ = "job_alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    seeker_user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(255), default="My alert")
    criteria: Mapped[dict[str, Any]] = mapped_column(JSON)  # city, category, salary_min, job_type, keywords
    notify_email: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_sms: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    from_user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    to_user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    application_id: Mapped[Optional[int]] = mapped_column(ForeignKey("applications.id", ondelete="SET NULL"), nullable=True)
    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    employer_user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    job_id: Mapped[Optional[int]] = mapped_column(ForeignKey("jobs.id", ondelete="SET NULL"), nullable=True)
    provider: Mapped[str] = mapped_column(String(32))  # chapa | telebirr
    external_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    amount_etb: Mapped[int] = mapped_column(Integer)
    status: Mapped[PaymentStatus] = mapped_column(Enum(PaymentStatus, native_enum=False), default=PaymentStatus.pending)
    raw_payload: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
