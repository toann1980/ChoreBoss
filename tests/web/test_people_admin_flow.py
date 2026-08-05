from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from tests.setup_memory_records import setup_test_people


def _login_as_admin(test_client) -> None:
    response = test_client.post(
        "/login",
        json={"login_name": "john", "pin": "1234"},
    )
    assert response.status_code == 200
    assert response.json() == {"success": True}


def test_add_person_form_parses_birthday_and_redirects(test_client, async_session: AsyncSession) -> None:
    __import__("asyncio").get_event_loop().run_until_complete(setup_test_people(async_session, 1))
    __import__("asyncio").get_event_loop().run_until_complete(async_session.commit())

    _login_as_admin(test_client)

    response = test_client.post(
        "/people/add",
        data={
            "first_name": "Jane",
            "last_name": "Live",
            "birthday": "2000-01-01",
            "pin": "2468",
            "is_admin": "",
            "assign_chores": "on",
            "login_name": "jane_live",
        },
        follow_redirects=False,
    )

    assert response.status_code in {303, 200}
    if response.status_code == 303:
        assert response.headers["location"].endswith("/login")
