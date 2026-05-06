from __future__ import annotations

from flask_bridge import app


def test_dashboard_renders_with_list_payloads(monkeypatch) -> None:
    client = app.test_client()

    def fake_api_call(method, endpoint, data=None, params=None):
        if endpoint == "/chores/":
            return 200, [{"id": 1, "name": "Wash dishes", "description": "Wash all dishes and put them away"}]
        if endpoint == "/people/":
            return 200, [{"id": 1, "first_name": "Admin", "last_name": "Test"}]
        raise AssertionError(f"Unexpected endpoint: {endpoint}")

    monkeypatch.setattr("flask_bridge.api_call", fake_api_call)

    with client.session_transaction() as sess:
        sess["token"] = "fake-token"

    response = client.get("/")

    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "Wash dishes" in body
    assert "ChoreBoss" in body
