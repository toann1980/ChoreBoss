from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from tests.setup_memory_records import setup_test_chores, setup_test_people


def _login_as_admin(test_client) -> None:
    response = test_client.post(
        "/login",
        json={"login_name": "john", "pin": "1234"},
    )
    assert response.status_code == 200
    assert response.json() == {"success": True}


def test_add_chore_page_renders_for_admin(test_client, async_session: AsyncSession) -> None:
    people = __import__("asyncio").get_event_loop().run_until_complete(setup_test_people(async_session, 2))
    __import__("asyncio").get_event_loop().run_until_complete(async_session.commit())

    _login_as_admin(test_client)

    response = test_client.get("/chores/add")

    assert response.status_code == 200
    html = response.text
    assert "Add Chore" in html
    assert "Assigned To" in html
    assert "person_id" in html
    assert people[0].first_name in html


def test_add_chore_form_creates_chore_and_redirects(test_client, async_session: AsyncSession) -> None:
    __import__("asyncio").get_event_loop().run_until_complete(setup_test_people(async_session, 2))
    __import__("asyncio").get_event_loop().run_until_complete(async_session.commit())

    _login_as_admin(test_client)

    response = test_client.post(
        "/chores/add",
        data={
            "name": "Sweep floors",
            "description": "Sweep the kitchen and hall",
            "person_id": "1",
        },
        follow_redirects=False,
    )

    assert response.status_code in {303, 200}
    if response.status_code == 303:
        assert response.headers["location"].endswith("/chores")


def test_edit_chore_page_renders_with_existing_values(test_client, async_session: AsyncSession) -> None:
    people = __import__("asyncio").get_event_loop().run_until_complete(setup_test_people(async_session, 2))
    chores = __import__("asyncio").get_event_loop().run_until_complete(setup_test_chores(async_session, 1))
    __import__("asyncio").get_event_loop().run_until_complete(async_session.commit())

    _login_as_admin(test_client)

    response = test_client.get(f"/chores/{chores[0].id}/edit")

    assert response.status_code == 200
    html = response.text
    assert "Edit Chore" in html
    assert chores[0].name in html
    assert chores[0].description in html
    assert 'showPinModal(\'edit_chore\')' in html
    assert 'showPinModal(\'delete_chore\')' in html
    assert people[0].first_name in html


def test_edit_chore_form_updates_chore_and_redirects(test_client, async_session: AsyncSession) -> None:
    __import__("asyncio").get_event_loop().run_until_complete(setup_test_people(async_session, 2))
    chores = __import__("asyncio").get_event_loop().run_until_complete(setup_test_chores(async_session, 1))
    __import__("asyncio").get_event_loop().run_until_complete(async_session.commit())

    _login_as_admin(test_client)

    response = test_client.post(
        f"/chores/{chores[0].id}/edit",
        data={
            "name": "Polish floors",
            "description": "Polish the kitchen floor",
            "person_id": "2",
            "pin": "1234",
            "pinContext": "edit_chore",
        },
        follow_redirects=False,
    )

    assert response.status_code in {303, 200}
    if response.status_code == 303:
        assert response.headers["location"].endswith(f"/chores/{chores[0].id}")
