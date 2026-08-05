from __future__ import annotations


def test_version_endpoint_returns_build_identity(test_client) -> None:
    response = test_client.get("/api/version")

    assert response.status_code == 200
    data = response.json()
    assert data["version"] == "2.0.0"
    assert data["title"] == "ChoreBoss API"


def test_version_endpoint_uses_runtime_build_metadata(monkeypatch) -> None:
    monkeypatch.setenv("BUILD_VERSION", "2.0.1")
    monkeypatch.setenv("BUILD_SHA", "abc123")
    monkeypatch.setenv("BUILD_DATE", "2026-05-20T21:52:00-07:00")

    from api.main import create_app
    from fastapi.testclient import TestClient

    app = create_app()
    client = TestClient(app)

    response = client.get("/api/version")

    assert response.status_code == 200
    assert response.json() == {
        "version": "2.0.1",
        "title": "ChoreBoss API",
        "build_sha": "abc123",
        "build_date": "2026-05-20T21:52:00-07:00",
    }
