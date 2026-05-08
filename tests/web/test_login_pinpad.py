from __future__ import annotations

from fastapi.testclient import TestClient


def test_login_page_shows_pin_pad_trigger(test_client: TestClient) -> None:
    """Login page should expose a PIN pad trigger for numeric PIN entry."""
    response = test_client.get("/login")

    assert response.status_code == 200
    html = response.text
    assert 'id="pin"' in html
    assert 'showPinModal(\'login\')' in html
    assert 'Pin Pad' in html or 'PIN Pad' in html or 'numpadModal' in html


def test_login_page_includes_numeric_pin_input_behavior(test_client: TestClient) -> None:
    """Login page should hint that PIN entry is numeric and keep the field easy to tap."""
    response = test_client.get("/login")

    assert response.status_code == 200
    html = response.text
    assert 'inputmode="numeric"' in html or 'pattern="[0-9]*"' in html
    assert 'readonly' in html
