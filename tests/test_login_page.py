from __future__ import annotations

from flask_bridge import app


def test_login_page_has_register_link() -> None:
    client = app.test_client()

    response = client.get("/login")

    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "Register" in body
    assert "/people/add" in body
