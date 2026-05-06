from __future__ import annotations

from flask_bridge import app


def test_verify_pin_allows_admin_delete_context(monkeypatch) -> None:
    client = app.test_client()

    def fake_api_call(method, endpoint, data=None, params=None):
        if method == 'POST' and endpoint == '/auth/login':
            assert data == {'login_name': 'admin', 'pin': '1111'}
            return 200, {
                'access_token': 'token',
                'token_type': 'bearer',
                'person_id': 1,
                'is_admin': True,
            }
        raise AssertionError(f'unexpected call: {method} {endpoint}')

    monkeypatch.setattr('flask_bridge.api_call', fake_api_call)

    with client.session_transaction() as sess:
        sess['token'] = 'token'
        sess['login_name'] = 'admin'

    response = client.post('/verify_pin', json={'context': 'delete_chore', 'pin': '1111'})

    assert response.status_code == 200
    assert response.get_json() == {'status': 'success'}


def test_verify_pin_rejects_bad_pin(monkeypatch) -> None:
    client = app.test_client()

    def fake_api_call(method, endpoint, data=None, params=None):
        if method == 'POST' and endpoint == '/auth/login':
            return 401, {'detail': 'Invalid PIN'}
        raise AssertionError(f'unexpected call: {method} {endpoint}')

    monkeypatch.setattr('flask_bridge.api_call', fake_api_call)

    with client.session_transaction() as sess:
        sess['token'] = 'token'
        sess['login_name'] = 'admin'

    response = client.post('/verify_pin', json={'context': 'delete_chore', 'pin': '9999'})

    assert response.status_code == 200
    assert response.get_json() == {'status': 'failure'}


def test_delete_chore_redirects_after_success(monkeypatch) -> None:
    client = app.test_client()

    def fake_api_call(method, endpoint, data=None, params=None):
        if method == 'DELETE' and endpoint == '/chores/7':
            return 204, {}
        raise AssertionError(f'unexpected call: {method} {endpoint}')

    monkeypatch.setattr('flask_bridge.api_call', fake_api_call)

    with client.session_transaction() as sess:
        sess['token'] = 'token'

    response = client.post('/chores/7/delete', follow_redirects=False)

    assert response.status_code in (302, 303)
    assert response.headers['Location'].endswith('/chores')
