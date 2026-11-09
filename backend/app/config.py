"""Settings from environment variables and the project's .env file."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Repository root (backend/app/config.py -> two levels up). The Docker image keeps the same layout.
PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=PROJECT_ROOT / ".env", extra="ignore")

    sync_interval_minutes: int = Field(default=60, ge=1)  # 0 would make the worker loop busy


@lru_cache
def get_settings() -> Settings:
    return Settings()
