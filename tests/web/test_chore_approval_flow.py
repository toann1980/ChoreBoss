from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tests.setup_memory_records import setup_test_chores, setup_test_people


def _login(test_client, login_name: str, pin: str) -> None:
    response = test_client.post(
        "/login",
        json={"login_name": login_name, "pin": pin},
    )
    assert response.status_code == 200
    assert response.json() == {"success": True}


@pytest.mark.asyncio
async def test_assigned_user_can_request_completion_and_admin_can_approve(
    test_client,
    async_session: AsyncSession,
) -> None:
    people = await setup_test_people(async_session, 2)
    chores = await setup_test_chores(async_session, 1)
    chores[0].person_id = people[1].id
    await async_session.commit()

    _login(test_client, people[1].login_name, "5678")

    detail_response = test_client.get(f"/chores/{chores[0].id}")
    assert detail_response.status_code == 200
    detail_html = detail_response.text
    assert "Request Approval" in detail_html

    request_response = test_client.post(
        f"/chores/{chores[0].id}/request_completion",
        data={"pin": "5678", "pinContext": "request_complete"},
        follow_redirects=False,
    )
    assert request_response.status_code in {200, 303}

    refreshed = await async_session.get(type(chores[0]), chores[0].id)
    assert refreshed.completion_requested_by_id == people[1].id
    assert refreshed.completion_requested_at is not None

    _login(test_client, people[0].login_name, "1234")

    approve_response = test_client.post(
        f"/chores/{chores[0].id}/approve_completion",
        data={"pin": "1234", "pinContext": "approve_complete"},
        follow_redirects=False,
    )
    assert approve_response.status_code in {200, 303}

    updated = await async_session.get(type(chores[0]), chores[0].id)
    assert updated.last_completed_id == people[1].id
    assert updated.last_completed_date is not None
    assert updated.completion_requested_by_id is None
    assert updated.completion_requested_at is None
    assert updated.completion_approved_by_id == people[0].id
    assert updated.completion_approved_at is not None
