from __future__ import annotations

from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine


@pytest.mark.asyncio
async def test_alembic_upgrade_preserves_app_readability(tmp_path: Path) -> None:
    """The app should still be able to read the DB after migrations run."""
    db_path = tmp_path / "choreboss-migration.sqlite3"
    db_url = f"sqlite+aiosqlite:///{db_path}"

    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", db_url)

    command.upgrade(alembic_cfg, "head")

    engine = create_async_engine(db_url, future=True)
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        table_names = {row[0] for row in result.fetchall()}

    await engine.dispose()

    assert "people" in table_names
    assert "chores" in table_names
