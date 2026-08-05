from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from api.dependencies.db import get_session
from api.main import create_app
from tests.setup_memory_records import setup_test_people


@pytest.mark.asyncio
async def test_session_cookie_survives_app_restart(async_session) -> None:
    """A signed browser session should remain valid across app restarts."""
    people = await setup_test_people(async_session, 1)
    await async_session.commit()
    person = people[0]

    async def override_get_session():
        yield async_session

    app1 = create_app()
    app1.dependency_overrides[get_session] = override_get_session
    client1 = TestClient(app1)
    login_response = client1.post(
        "/login",
        json={"login_name": person.login_name, "pin": "1234"},
    )
    assert login_response.status_code == 200
    assert login_response.json() == {"success": True}

    session_cookie = client1.cookies.get("session")
    assert session_cookie is not None

    app2 = create_app()
    app2.dependency_overrides[get_session] = override_get_session
    client2 = TestClient(app2)
    client2.cookies.set("session", session_cookie)

    protected_response = client2.get("/chores")
    assert protected_response.status_code == 200
    assert "My Chores" in protected_response.text or "Chores List" in protected_response.text
