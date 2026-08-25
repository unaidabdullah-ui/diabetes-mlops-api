"""Application configuration.

All settings are sourced from environment variables (with sane defaults)
so the same image can be promoted across dev/staging/prod without code
changes. Override any of these via `docker run -e VAR=value ...` or a
`.env` file.
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Diabetes Prediction API"
    app_version: str = "1.0.0"
    environment: str = "development"  # development | staging | production

    model_path: str = "models/diabetes_model.pkl"
    metadata_path: str = "models/metadata.json"

    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_prefix="DIABETES_API_", env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    """Cached settings accessor. Use `get_settings.cache_clear()` in tests
    to force re-reading environment variables."""
    return Settings()
