from __future__ import annotations


def test_login_page_shows_pin_pad_trigger(test_client) -> None:
    """Login page should expose a PIN pad trigger for numeric PIN entry."""
    response = test_client.get("/login")

    assert response.status_code == 200
    html = response.text
    assert 'id="pin"' in html
    assert "showPinModal('login')" in html
    assert 'inputmode="numeric"' in html
    assert 'id="login_pin"' in html
    assert 'id="pinContext"' in html


def test_login_page_does_not_show_redundant_open_pin_button(test_client) -> None:
    """Login page should rely on the PIN field itself, not a redundant extra button."""
    response = test_client.get("/login")

    assert response.status_code == 200
    html = response.text
    assert 'Open PIN Pad' not in html


def test_login_page_includes_numeric_pin_input_behavior(test_client) -> None:
    """Login page should hint that PIN entry is numeric and keep the field easy to tap."""
    response = test_client.get("/login")

    assert response.status_code == 200
    html = response.text
    assert 'inputmode="numeric"' in html or 'pattern="[0-9]*"' in html
    assert 'readonly' in html


def test_login_modal_enter_key_should_submit_login_form(test_client) -> None:
    """Login PIN pad should submit the login form when Enter is pressed."""
    response = test_client.get("/login")

    assert response.status_code == 200
    html = response.text
    assert "requestSubmit" in html or "login-form" in html
    assert "handleKeyPress" in html
    assert "Enter" in html
