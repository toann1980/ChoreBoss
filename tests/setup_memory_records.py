"""Test setup utilities for in-memory test database."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def setup_test_people(
    session: AsyncSession,
    count: int = 1,
) -> list:
    """Create test people in database.

    Args:
        session: Async database session.
        count: Number of people to create (1-3).

    Returns:
        list: Created people objects.
    """
    from choreboss.models.people import People

    people = []
    test_data = [
        {
            "first_name": "John",
            "last_name": "Doe",
            "birthday": date(2000, 1, 1),
            "pin": "1234",
            "is_admin": True,
            "sequence_num": 1,
        },
        {
            "first_name": "Jane",
            "last_name": "Doe",
            "birthday": date(2002, 1, 1),
            "pin": "5678",
            "is_admin": False,
            "sequence_num": 2,
        },
        {
            "first_name": "Mary",
            "last_name": "Doe",
            "birthday": date(2004, 1, 1),
            "pin": "9012",
            "is_admin": False,
            "sequence_num": 3,
        },
    ]

    for i in range(min(count, 3)):
        person = People(**test_data[i])
        person.set_pin(test_data[i]["pin"])
        session.add(person)
        people.append(person)

    await session.flush()
    return people


async def setup_test_chores(
    session: AsyncSession,
    count: int = 1,
) -> list:
    """Create test chores in database.

    Args:
        session: Async database session.
        count: Number of chores to create (1+).

    Returns:
        list: Created chore objects.
    """
    from choreboss.models.chore import Chore

    chores = []
    test_data = [
        {
            "name": "Wash the dishes",
            "description": "Wash the dishes in the sink",
            "person_id": None,
        },
        {
            "name": "Take out trash",
            "description": "Take out the trash to the curb",
            "person_id": None,
        },
        {
            "name": "Vacuum the floor",
            "description": "Vacuum all carpeted areas",
            "person_id": None,
        },
        {
            "name": "Clean the bathroom",
            "description": "Clean toilet, sink, and shower",
            "person_id": None,
        },
        {
            "name": "Do the laundry",
            "description": "Wash and fold all household laundry",
            "person_id": None,
        },
    ]

    for i in range(min(count, len(test_data))):
        chore = Chore(**test_data[i])
        session.add(chore)
        chores.append(chore)

    await session.flush()
    return chores
