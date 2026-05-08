from __future__ import annotations

import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from tests.setup_memory_records import setup_test_people


def test_authenticated_pages_use_fresh_back_navigation(
    test_client,
    async_session: AsyncSession,
) -> None:
    """Authenticated pages should use a fresh back navigation helper instead of browser history."""
    asyncio.get_event_loop().run_until_complete(setup_test_people(async_session, 1))
    asyncio.get_event_loop().run_until_complete(async_session.commit())

    login_response = test_client.post(
        "/login",
        json={"login_name": "john", "pin": "1234"},
    )
    assert login_response.status_code == 200

    response = test_client.get("/people")

    assert response.status_code == 200
    html = response.text
    assert 'onclick="goBackFresh()"' in html
    assert "window.history.back()" not in html
    assert "window.location.href = refUrl.href;" in html
    assert "fallbackUrl" in html
