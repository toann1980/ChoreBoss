from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from tests.setup_memory_records import setup_test_people


def test_login_form_accepts_correct_credentials_and_redirects(
    test_client,
    async_session: AsyncSession,
) -> None:
    """Rendered login flow should accept valid credentials and set a session cookie."""
    # Seed the default admin user used by the smoke path.
    import asyncio

    asyncio.get_event_loop().run_until_complete(setup_test_people(async_session, 1))
    asyncio.get_event_loop().run_until_complete(async_session.commit())

    response = test_client.post(
        "/login",
        json={"login_name": "john", "pin": "1234"},
    )

    assert response.status_code == 200
    assert response.json() == {"success": True}
    assert "session=" in response.headers.get("set-cookie", "")
