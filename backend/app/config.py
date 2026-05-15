"""Application configuration — all secrets from environment."""
from functools import lru_cache
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://jobportal:jobportal_dev@localhost:5432/jobportal_et"
    redis_url: str = "redis://localhost:6379/0"

    jwt_secret: str = "dev-change-me"
    jwt_refresh_secret: str = "dev-refresh-change-me"
    jwt_access_expire_minutes: int = 30
    jwt_refresh_expire_days: int = 14

    frontend_url: str = "http://localhost:3000"
    backend_url: str = "http://localhost:8000"

    google_client_id: str = ""
    google_client_secret: str = ""

    email_from: str = "noreply@localhost"
    sendgrid_api_key: str = ""
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""

    africastalking_username: str = ""
    africastalking_api_key: str = ""
    africastalking_sender_id: str = "JobET"

    storage_backend: str = "local"  # local | s3
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_s3_bucket: str = ""
    aws_region: str = "af-south-1"

    chapa_secret_key: str = ""
    chapa_webhook_secret: str = ""

    cv_parser_mode: str = "basic"  # basic | spacy
    affinda_api_key: str = ""

    cors_origins: str = "http://localhost:3000"
    rate_limit_per_minute: int = 120
    max_upload_mb: int = 5
    clamav_socket: str = ""

    @property
    def cors_origin_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
