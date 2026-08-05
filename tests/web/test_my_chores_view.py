from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from tests.setup_memory_records import setup_test_chores, setup_test_people


def _login(test_client, login_name: str, pin: str) -> None:
    response = test_client.post(
        "/login",
        json={"login_name": login_name, "pin": pin},
    )
    assert response.status_code == 200
    assert response.json() == {"success": True}


def test_non_admin_sees_only_assigned_chores_and_due_status(
    test_client,
    async_session: AsyncSession,
) -> None:
    people = __import__("asyncio").get_event_loop().run_until_complete(setup_test_people(async_session, 2))
    chores = __import__("asyncio").get_event_loop().run_until_complete(setup_test_chores(async_session, 2))
    chores[0].person_id = people[1].id
    chores[1].person_id = None
    __import__("asyncio").get_event_loop().run_until_complete(async_session.commit())

    _login(test_client, "jane", "5678")

    response = test_client.get("/chores")

    assert response.status_code == 200
    html = response.text
    assert "My Chores" in html
    assert chores[0].name in html
    assert chores[1].name not in html
    assert "Due now" in html
    assert "Assigned to" not in html


def test_admin_sees_all_chores_with_assignment_and_due_status(
    test_client,
    async_session: AsyncSession,
) -> None:
    people = __import__("asyncio").get_event_loop().run_until_complete(setup_test_people(async_session, 2))
    chores = __import__("asyncio").get_event_loop().run_until_complete(setup_test_chores(async_session, 2))
    chores[0].person_id = people[1].id
    chores[1].person_id = None
    __import__("asyncio").get_event_loop().run_until_complete(async_session.commit())

    _login(test_client, "john", "1234")

    response = test_client.get("/chores")

    assert response.status_code == 200
    html = response.text
    assert "Chores List" in html
    assert chores[0].name in html
    assert chores[1].name in html
    assert "Assigned to" in html
    assert "Unassigned" in html
    assert "Due now" in html
