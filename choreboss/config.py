"""Application configuration."""

from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings from environment variables."""

    environment: str = "development"
    debug: bool = True
    database_url: str = "postgresql+asyncpg://localhost/choreboss"
    secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 168  # 7 days
    host: str = "0.0.0.0"
    port: int = 8055

    class Config:
        """Pydantic config."""

        env_file = ".env"
        extra = "ignore"


_settings: Settings | None = None


def get_config() -> Settings:
    """Get application settings singleton.

    Returns:
        Settings: Application settings.
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


# Legacy config classes for backwards compatibility with tests
class DevelopmentConfig:
    """Legacy development config."""

    SQLALCHEMY_DATABASE_URI = "sqlite:///choreboss.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "dev-secret-key"


class TestingConfig:
    """Legacy testing config."""

    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    TESTING = True
    SECRET_KEY = "testing_secret_key"
