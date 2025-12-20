"""
Application configuration and settings.
"""

from pathlib import Path
from urllib.parse import quote_plus

from pydantic import Field
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    """Application configuration settings."""

    # PostgreSQL configuration
    db_user: str = Field(default=..., alias="DB_USER")  # Required field
    db_password: str = Field(default=..., alias="DB_PASSWORD")  # Required field
    db_host: str = Field(default=..., alias="DB_HOST")  # Required field
    db_port: str = Field(default=..., alias="DB_PORT")  # Required field
    db_name: str = Field(default=..., alias="DB_NAME")  # Required field

    # JWT Configuration
    secret_key: str = Field(default=..., alias="SECRET_KEY")  # Required field
    algorithm: str = Field(default="HS256", alias="ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=30, alias="ACCESS_TOKEN_EXPIRE_MINUTES"
    )

    # Refresh token configuration
    refresh_token_expire_days: int = Field(default=7, alias="REFRESH_TOKEN_EXPIRE_DAYS")

    default_pagination_limit: int = Field(default=10, alias="DEFAULT_PAGINATION_LIMIT")

    # Static files paths
    permissions_path: str = Field(
        default=str(
            Path(__file__).parent.parent.parent / "statics" / "permissions.json"
        ),
        alias="PERMISSIONS_PATH",
    )
    policies_path: str = Field(
        default=str(Path(__file__).parent.parent.parent / "statics" / "policies.json"),
        alias="POLICIES_PATH",
    )

    # Construct the database URL
    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.db_user}:{quote_plus(self.db_password)}@{self.db_host}:{self.db_port}/{self.db_name}"

    model_config = {
        "populate_by_name": True,
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


# Global instance of the configuration
config = Config()
