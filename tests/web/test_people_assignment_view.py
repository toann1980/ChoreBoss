from __future__ import annotations

import asyncio

from tests.setup_memory_records import setup_test_chores, setup_test_people


def _login(test_client, login_name: str = "john", pin: str = "1234") -> None:
    response = test_client.post("/login", json={"login_name": login_name, "pin": pin})
    assert response.status_code == 200


def test_home_links_to_people_assignment_view(test_client, async_session) -> None:
    people = asyncio.get_event_loop().run_until_complete(setup_test_people(async_session, 2))
    chores = asyncio.get_event_loop().run_until_complete(setup_test_chores(async_session, 1))
    chores[0].person_id = people[1].id
    asyncio.get_event_loop().run_until_complete(async_session.commit())
    _login(test_client)

    response = test_client.get("/")

    assert response.status_code == 200
    assert "/people" in response.text
    assert "Manage People" in response.text
    assert "Add Person" not in response.text
    assert "Edit People" not in response.text
    assert "chore-section-header" in response.text
    assert "chore-row" in response.text
    assert "chore-assignee" in response.text
    assert "Jane Doe" in response.text


def test_people_page_links_to_each_person_assigned_chores(test_client, async_session) -> None:
    people = asyncio.get_event_loop().run_until_complete(setup_test_people(async_session, 2))
    chores = asyncio.get_event_loop().run_until_complete(setup_test_chores(async_session, 2))
    chores[0].person_id = people[1].id
    awaitable = async_session.commit()
    asyncio.get_event_loop().run_until_complete(awaitable)
    _login(test_client)

    response = test_client.get("/people")

    assert response.status_code == 200
    assert f"/people/{people[1].id}/chores" in response.text
    assert "Jane Doe" in response.text


def test_person_assignment_view_shows_only_selected_person_chores(test_client, async_session) -> None:
    people = asyncio.get_event_loop().run_until_complete(setup_test_people(async_session, 2))
    chores = asyncio.get_event_loop().run_until_complete(setup_test_chores(async_session, 2))
    chores[0].person_id = people[1].id
    chores[1].person_id = people[0].id
    asyncio.get_event_loop().run_until_complete(async_session.commit())
    _login(test_client)

    response = test_client.get(f"/people/{people[1].id}/chores")

    assert response.status_code == 200
    assert "Jane Doe" in response.text
    assert "Chores" in response.text
    assert chores[0].name in response.text
    assert chores[1].name not in response.text
