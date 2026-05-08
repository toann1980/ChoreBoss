from __future__ import annotations


def test_register_page_renders_add_person_form(test_client) -> None:
    response = test_client.get("/people/add")

    assert response.status_code == 200
    body = response.text
    assert "Add New Person" in body
    assert "login_name" in body
    assert "assign_chores" in body
