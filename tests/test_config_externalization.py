from __future__ import annotations

from choreboss import config as config_module
from choreboss.config import get_config


def test_get_config_reads_runtime_environment(monkeypatch) -> None:
    """Environment variables should override the built-in defaults."""
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+asyncpg://user:pass@db:5432/choreboss",
    )
    monkeypatch.setenv("SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("HOST", "0.0.0.0")
    monkeypatch.setenv("PORT", "9001")
    monkeypatch.setenv("DEBUG", "false")
    monkeypatch.setenv("ENVIRONMENT", "production")

    config_module._settings = None
    settings = get_config()

    assert settings.database_url == "postgresql+asyncpg://user:pass@db:5432/choreboss"
    assert settings.secret_key == "test-secret-key"
    assert settings.host == "0.0.0.0"
    assert settings.port == 9001
    assert settings.debug is False
    assert settings.environment == "production"
