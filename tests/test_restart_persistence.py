from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from choreboss.models import Base
from choreboss.repositories.chore_repository import ChoreRepository
from choreboss.repositories.people_repository import PeopleRepository


@pytest.mark.asyncio
async def test_records_survive_engine_restart(tmp_path: Path) -> None:
    """Persist people and chores across a file-backed engine restart."""
    db_path = tmp_path / "choreboss.sqlite3"
    database_url = f"sqlite+aiosqlite:///{db_path}"

    engine = create_async_engine(database_url, future=True)
    session_factory = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with session_factory() as session:
        people_repo = PeopleRepository(session)
        chore_repo = ChoreRepository(session)

        person = await people_repo.add_person(
            first_name="Alice",
            last_name="Smith",
            birthday=date(2012, 1, 1),
            pin="1234",
            is_admin=True,
            login_name="alice",
        )
        chore = await chore_repo.add_chore(
            name="Wash dishes",
            description="Wash all dishes and put them away",
            person_id=person.id,
        )
        await session.commit()
        person_id = person.id
        chore_id = chore.id

    await engine.dispose()

    restarted_engine = create_async_engine(database_url, future=True)
    restarted_session_factory = sessionmaker(
        restarted_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with restarted_session_factory() as session:
        people_repo = PeopleRepository(session)
        chore_repo = ChoreRepository(session)

        restored_person = await people_repo.get_person_by_id(person_id)
        restored_chore = await chore_repo.get_chore_by_id(chore_id)

    await restarted_engine.dispose()

    assert restored_person is not None
    assert restored_person.login_name == "alice"
    assert restored_person.first_name == "Alice"
    assert restored_chore is not None
    assert restored_chore.name == "Wash dishes"
    assert restored_chore.person_id == person_id
