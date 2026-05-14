from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, EmailStr, Field


class UserRoleSchema(str, Enum):
    job_seeker = "job_seeker"
    employer = "employer"


class RegisterRequest(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=32)
    password: str = Field(min_length=8, max_length=128)
    role: UserRoleSchema


class LoginRequest(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class GoogleAuthRequest(BaseModel):
    id_token: str


class UserOut(BaseModel):
    id: int
    email: Optional[str]
    phone: Optional[str]
    role: str
    preferred_locale: str

    class Config:
        from_attributes = True


class EducationIn(BaseModel):
    institution: str
    degree: str
    field: str = ""
    year_end: Optional[int] = None


class ExperienceIn(BaseModel):
    company: str
    title: str
    description: Optional[str] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None


class SeekerProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    headline: Optional[str] = None
    bio: Optional[str] = None
    portfolio_urls: Optional[list[str]] = None
    preferred_locale: Optional[str] = None
    education: Optional[list[EducationIn]] = None
    experience: Optional[list[ExperienceIn]] = None
    skills: Optional[list[str]] = None


class SeekerProfileOut(BaseModel):
    full_name: str
    headline: str
    bio: Optional[str]
    portfolio_urls: list[str]
    resume_path: Optional[str]
    parsed_cv: Optional[dict[str, Any]]
    skills: list[str]
    preferred_locale: str

    class Config:
        from_attributes = True


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None


class CompanyOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    website: Optional[str]
    verified: bool

    class Config:
        from_attributes = True


class JobCreate(BaseModel):
    title_en: str
    title_am: Optional[str] = None
    description_en: str
    description_am: Optional[str] = None
    requirements_en: str = ""
    requirements_am: Optional[str] = None
    category: str
    city: str
    salary_min_etb: Optional[int] = None
    salary_max_etb: Optional[int] = None
    job_type: str
    deadline: Optional[datetime] = None
    is_published: bool = True


class JobUpdate(BaseModel):
    title_en: Optional[str] = None
    title_am: Optional[str] = None
    description_en: Optional[str] = None
    description_am: Optional[str] = None
    requirements_en: Optional[str] = None
    requirements_am: Optional[str] = None
    category: Optional[str] = None
    city: Optional[str] = None
    salary_min_etb: Optional[int] = None
    salary_max_etb: Optional[int] = None
    job_type: Optional[str] = None
    deadline: Optional[datetime] = None
    is_published: Optional[bool] = None


class JobOut(BaseModel):
    id: int
    company_id: int
    company_name: str
    title_en: str
    title_am: Optional[str]
    description_en: str
    description_am: Optional[str]
    requirements_en: str
    requirements_am: Optional[str]
    category: str
    city: str
    salary_min_etb: Optional[int]
    salary_max_etb: Optional[int]
    job_type: str
    deadline: Optional[datetime]
    is_premium: bool
    view_count: int
    application_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class JobListFilters(BaseModel):
    city: Optional[str] = None
    category: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    job_type: Optional[str] = None
    q: Optional[str] = None


class ApplicationCreate(BaseModel):
    cover_letter: Optional[str] = None
    use_profile_resume: bool = True


class ApplicationOut(BaseModel):
    id: int
    job_id: int
    status: str
    match_score: Optional[float]
    created_at: datetime
    job_title: Optional[str] = None

    class Config:
        from_attributes = True


class ApplicantOut(BaseModel):
    application_id: int
    seeker_user_id: int
    full_name: str
    email: Optional[str]
    match_score: Optional[float]
    status: str
    created_at: datetime


class ApplicationStatusUpdate(BaseModel):
    status: str


class JobAlertCreate(BaseModel):
    name: str = "Alert"
    criteria: dict[str, Any]
    notify_email: bool = True
    notify_sms: bool = False


class MessageCreate(BaseModel):
    to_user_id: int
    body: str
    application_id: Optional[int] = None


class UserActiveBody(BaseModel):
    active: bool


class PaymentInitRequest(BaseModel):
    job_id: int
    amount_etb: int = Field(ge=100, le=500_000)
    provider: str = "chapa"


class AnalyticsSummary(BaseModel):
    total_views: int
    total_applications: int
    conversion_rate: float  # applications / views
