from __future__ import annotations

from flask_bridge import app


def test_person_detail_renders_iso_birthday(monkeypatch) -> None:
    client = app.test_client()

    def fake_api_call(method, endpoint, data=None, params=None):
        assert method == "GET"
        assert endpoint == "/people/1"
        return 200, {
            "id": 1,
            "first_name": "Admin",
            "last_name": "Test",
            "login_name": "admin",
            "birthday": "1990-01-01",
            "is_admin": True,
        }

    monkeypatch.setattr("flask_bridge.api_call", fake_api_call)
    monkeypatch.setattr("flask_bridge.render_template", lambda *args, **kwargs: "ok")

    with client.session_transaction() as sess:
        sess["token"] = "fake-token"

    response = client.get("/people/1")

    assert response.status_code == 200
    assert response.get_data(as_text=True) == "ok"


def test_add_chore_accepts_form_post(monkeypatch) -> None:
    client = app.test_client()

    calls = []

    def fake_api_call(method, endpoint, data=None, params=None):
        calls.append((method, endpoint, data))
        if endpoint == "/people/":
            return 200, [{"id": 1, "first_name": "Admin"}]
        assert method == "POST"
        assert endpoint == "/chores/"
        assert data["name"] == "Sweep floors"
        return 200, {"id": 99}

    monkeypatch.setattr("flask_bridge.api_call", fake_api_call)
    monkeypatch.setattr("flask_bridge.render_template", lambda *args, **kwargs: "ok")

    with client.session_transaction() as sess:
        sess["token"] = "fake-token"

    response = client.post(
        "/chores/add",
        data={"name": "Sweep floors", "description": "Sweep the kitchen", "person_id": ""},
        follow_redirects=False,
    )

    assert response.status_code in (302, 303)
    assert any(endpoint == "/chores/" for _, endpoint, _ in calls)


def test_change_sequence_placeholder_returns_501(monkeypatch) -> None:
    client = app.test_client()

    def fake_api_call(method, endpoint, data=None, params=None):
        assert method == "GET"
        assert endpoint == "/people/"
        return 200, [{"id": 1, "first_name": "Admin"}]

    monkeypatch.setattr("flask_bridge.api_call", fake_api_call)
    monkeypatch.setattr("flask_bridge.render_template", lambda *args, **kwargs: "ok")

    with client.session_transaction() as sess:
        sess["token"] = "fake-token"

    response = client.post("/change_sequence", json={"sequence_data": "[]"})

    assert response.status_code == 501
