from __future__ import annotations


def test_login_page_has_register_link(test_client) -> None:
    response = test_client.get("/login")

    assert response.status_code == 200
    body = response.text
    assert "Register" in body
    assert "/people/add" in body
    assert "showPinModal('login')" in body
    assert 'inputmode="numeric"' in body
