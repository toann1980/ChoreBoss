from __future__ import annotations

from flask_bridge import app


def test_register_page_accepts_form_post_and_redirects(monkeypatch) -> None:
    client = app.test_client()

    def fake_api_call(method, endpoint, data=None, params=None):
        assert method == "POST"
        assert endpoint == "/people/"
        assert data["login_name"] == "alex"
        assert data["first_name"] == "Alex"
        return 200, {"id": 42}

    monkeypatch.setattr("flask_bridge.api_call", fake_api_call)

    response = client.post(
        "/people/add",
        data={
            "first_name": "Alex",
            "last_name": "Nguyen",
            "login_name": "alex",
            "birthday": "2015-05-15",
            "pin": "1234",
            "is_admin": "on",
        },
        follow_redirects=False,
    )

    assert response.status_code in (302, 303)
    assert response.headers["Location"].endswith("/login")
