"""Application configuration"""

from typing import List

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    PROJECT_NAME: str = "FastAPI Enterprise"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    SECRET_KEY: str = "change-me-in-dev"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    ALGORITHM: str = "HS256"
    CORS_ORIGINS: List[str] = ["*"]
    DATABASE_URL: str = "sqlite+aiosqlite:///./app.db"

    # Redis configuration (optional)
    REDIS_URL: str | None = None
    REDIS_TTL: int = 300

    model_config = ConfigDict(env_file=".env", case_sensitive=True)


settings = Settings()
