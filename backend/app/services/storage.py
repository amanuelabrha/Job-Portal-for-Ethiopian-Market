"""File storage: local disk (dev) or S3 (production)."""
from __future__ import annotations

import os
import uuid
from pathlib import Path

from app.config import get_settings


def ensure_upload_dir() -> Path:
    base = Path(__file__).resolve().parent.parent.parent / "uploads"
    base.mkdir(parents=True, exist_ok=True)
    return base


def save_resume_file(filename: str, data: bytes) -> str:
    settings = get_settings()
    ext = Path(filename).suffix.lower()
    if ext not in (".pdf", ".docx"):
        raise ValueError("Invalid extension")
    key = f"{uuid.uuid4().hex}{ext}"
    if settings.storage_backend == "s3":
        return _save_s3(key, data)
    path = ensure_upload_dir() / key
    path.write_bytes(data)
    return str(path).replace("\\", "/")


def _save_s3(key: str, data: bytes) -> str:
    import boto3
    from botocore.exceptions import BotoCoreError, ClientError

    s = get_settings()
    client = boto3.client(
        "s3",
        aws_access_key_id=s.aws_access_key_id or None,
        aws_secret_access_key=s.aws_secret_access_key or None,
        region_name=s.aws_region,
    )
    try:
        client.put_object(Bucket=s.aws_s3_bucket, Key=f"resumes/{key}", Body=data)
        return f"s3://{s.aws_s3_bucket}/resumes/{key}"
    except (BotoCoreError, ClientError) as e:
        raise RuntimeError(str(e)) from e
