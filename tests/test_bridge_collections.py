from __future__ import annotations

from flask_bridge import app


def test_index_accepts_raw_list_payloads(monkeypatch) -> None:
    client = app.test_client()

    def fake_api_call(method, endpoint, data=None, params=None):
        if endpoint == "/chores/":
            return 200, [{"id": 1, "name": "Wash dishes"}]
        if endpoint == "/people/":
            return 200, [{"id": 1, "first_name": "Toan"}]
        raise AssertionError(f"Unexpected endpoint: {endpoint}")

    monkeypatch.setattr("flask_bridge.api_call", fake_api_call)
    monkeypatch.setattr("flask_bridge.render_template", lambda *args, **kwargs: "ok")

    with client.session_transaction() as sess:
        sess["token"] = "fake-token"

    response = client.get("/")

    assert response.status_code == 200
    assert response.get_data(as_text=True) == "ok"
