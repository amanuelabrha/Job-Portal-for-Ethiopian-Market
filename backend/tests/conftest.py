"""Test environment: in-memory SQLite (no Postgres required for unit/API smoke tests)."""
import os

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("REDIS_URL", "redis://127.0.0.1:6379/15")
os.environ.setdefault("JWT_SECRET", "test-jwt-secret-test-jwt-secret-12")
os.environ.setdefault("JWT_REFRESH_SECRET", "test-refresh-secret-test-refresh-12")
