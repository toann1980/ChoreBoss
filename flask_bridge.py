"""
Flask frontend bridge to FastAPI backend.

This module creates a Flask app that:
1. Serves the HTML/CSS/JS templates from web/templates/
2. Makes HTTP calls to the FastAPI backend at http://localhost:8000/api/
3. Tests the full async backend end-to-end

Run alongside FastAPI backend:
  Terminal 1: python api_run.py              (FastAPI backend)
  Terminal 2: python flask_bridge.py         (Flask frontend)

Then visit http://localhost:8055 in your browser.
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import logging
import os
from datetime import date, datetime

import requests
import json

# Configuration
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000/api')
FLASK_PORT = int(os.getenv('FLASK_PORT', 8055))
FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-prod')

app = Flask(
    __name__,
    static_folder=os.path.join(os.path.dirname(__file__), 'web', 'static'),
    template_folder=os.path.join(os.path.dirname(__file__), 'web', 'templates')
)
app.secret_key = FLASK_SECRET_KEY
logging.basicConfig(level=logging.DEBUG)
app.logger.setLevel(logging.DEBUG)

# =============================================================================
# Helper functions to call FastAPI backend
# =============================================================================

def get_auth_headers():
    """Get Authorization header if user is logged in."""
    token = session.get('token')
    if token:
        return {'Authorization': f'Bearer {token}'}
    return {}


def _normalize_dates(value):
    """Convert common ISO date/datetime fields from strings to Python objects."""
    if isinstance(value, list):
        return [_normalize_dates(item) for item in value]
    if isinstance(value, dict):
        normalized = dict(value)
        for key, raw in list(normalized.items()):
            if isinstance(raw, str):
                if key == 'birthday':
                    try:
                        normalized[key] = date.fromisoformat(raw)
                        continue
                    except ValueError:
                        pass
                if key in {'created_at', 'updated_at', 'last_completed_date'}:
                    try:
                        normalized[key] = datetime.fromisoformat(raw)
                        continue
                    except ValueError:
                        pass
        return normalized
    return value


def api_call(method, endpoint, data=None, params=None):
    """
    Make HTTP call to FastAPI backend.
    
    Args:
        method: 'GET', 'POST', 'PUT', 'DELETE'
        endpoint: e.g., '/chores/' or '/people/1'
        data: Dict to send as JSON
        params: Query parameters
    
    Returns:
        (status_code, response_json)
    """
    url = f"{API_BASE_URL}{endpoint}"
    headers = get_auth_headers()
    headers['Content-Type'] = 'application/json'
    app.logger.debug('API %s %s params=%s payload=%s', method, endpoint, params, data)
    
    try:
        if method == 'GET':
            resp = requests.get(url, headers=headers, params=params, timeout=5)
        elif method == 'POST':
            resp = requests.post(url, headers=headers, json=data, timeout=5)
        elif method == 'PUT':
            resp = requests.put(url, headers=headers, json=data, timeout=5)
        elif method == 'DELETE':
            resp = requests.delete(url, headers=headers, timeout=5)
        else:
            return 400, {'error': f'Unknown method: {method}'}
        
        try:
            parsed = resp.json() if resp.text else {}
        except ValueError:
            parsed = {'error': 'Backend returned non-JSON response', 'raw': resp.text[:500]}

        if isinstance(parsed, dict) and 'detail' in parsed and 'error' not in parsed:
            parsed['error'] = parsed['detail']

        parsed = _normalize_dates(parsed)

        if isinstance(parsed, dict):
            app.logger.debug('API %s %s -> %s dict_keys=%s', method, endpoint, resp.status_code, list(parsed.keys()))
        elif isinstance(parsed, list):
            app.logger.debug('API %s %s -> %s list_len=%s', method, endpoint, resp.status_code, len(parsed))
        else:
            app.logger.debug('API %s %s -> %s type=%s', method, endpoint, resp.status_code, type(parsed).__name__)
        return resp.status_code, parsed
    except requests.exceptions.ConnectionError:
        app.logger.exception('API connection error for %s %s', method, endpoint)
        return 503, {
            'error': 'Cannot connect to FastAPI backend',
            'hint': 'Make sure FastAPI is running: python api_run.py'
        }
    except Exception:
        app.logger.exception('API call failed for %s %s', method, endpoint)
        return 500, {'error': 'Unexpected bridge error'}


# =============================================================================
# Routes
# =============================================================================

def _collection_items(payload, collection_name: str) -> list:
    """Extract a list from either a raw list response or a keyed mapping."""
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        items = payload.get(collection_name)
        if isinstance(items, list):
            return items
    app.logger.warning(
        'Unexpected %s payload shape: %s',
        collection_name,
        type(payload).__name__,
    )
    return []


@app.route('/')
def index():
    """Home page."""
    if 'token' not in session:
        return redirect(url_for('login'))
    
    # Get chores and people for dashboard
    status, chores_data = api_call('GET', '/chores/')
    if status != 200:
        return f"Error fetching chores: {chores_data}", 500
    
    status, people_data = api_call('GET', '/people/')
    if status != 200:
        return f"Error fetching people: {people_data}", 500
    
    chores = _collection_items(chores_data, 'chores')
    people = _collection_items(people_data, 'people')
    
    return render_template('index.html', chores=chores, people=people)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page - PIN pad to authenticate."""
    if request.method == 'POST':
        data = request.get_json()
        login_name = data.get('login_name')
        pin = data.get('pin')
        
        if not login_name or not pin:
            return jsonify({'error': 'Missing login_name or pin'}), 400
        
        status, result = api_call('POST', '/auth/login', {
            'login_name': login_name,
            'pin': pin
        })
        
        if status == 200:
            if not isinstance(result, dict):
                app.logger.error('Unexpected login payload shape: %s', type(result).__name__)
                return jsonify({'error': 'Unexpected login response from backend'}), 502
            session['token'] = result.get('access_token')
            session['person_id'] = result.get('person_id')
            # Normalize and store login_name as lowercase so the bridge is case-insensitive
            session['login_name'] = login_name.strip().lower()
            app.logger.info('Login succeeded for %s', session['login_name'])
            return jsonify({'success': True})
        else:
            app.logger.warning('Login failed for %s with status %s payload=%s', login_name, status, result)
            if isinstance(result, dict):
                return jsonify({'error': result.get('error', 'Login failed')}), status
            return jsonify({'error': 'Login failed'}), status
    
    # GET: Show login page
    return render_template('login.html')


@app.route('/logout')
def logout():
    """Logout - clear session."""
    session.clear()
    return redirect(url_for('login'))


@app.route('/chores')
def chores_list():
    """List all chores."""
    if 'token' not in session:
        return redirect(url_for('login'))
    
    status, data = api_call('GET', '/chores/')
    if status != 200:
        return f"Error: {data}", 500
    
    chores = _collection_items(data, 'chores')
    return render_template('chores_list.html', chores=chores)


@app.route('/chores/<int:chore_id>')
def chore_detail(chore_id):
    """View chore details."""
    if 'token' not in session:
        return redirect(url_for('login'))
    
    status, chore = api_call('GET', f'/chores/{chore_id}')
    if status != 200:
        return f"Chore not found: {chore}", 404

    if isinstance(chore, dict):
        chore = dict(chore)
        person_id = chore.get('person_id')
        if person_id:
            person_status, person = api_call('GET', f'/people/{person_id}')
            if person_status == 200 and isinstance(person, dict):
                chore['person_id_foreign_key'] = person
        last_completed_id = chore.get('last_completed_id')
        if last_completed_id:
            person_status, person = api_call('GET', f'/people/{last_completed_id}')
            if person_status == 200 and isinstance(person, dict):
                chore['last_completed_id_foreign_key'] = person
    
    return render_template('chore_detail.html', chore=chore)


@app.route('/chores/add', methods=['GET', 'POST'])
def add_chore():
    """Add new chore (admin only)."""
    if 'token' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        data = request.get_json(silent=True) or request.form
        status, result = api_call('POST', '/chores/', {
            'name': data.get('name'),
            'description': data.get('description'),
            'person_id': data.get('person_id') or data.get('assigned_to') or None
        })
        
        if status in (200, 201):
            if request.is_json:
                chore_id = result.get('id') if isinstance(result, dict) else None
                return jsonify({'success': True, 'chore_id': chore_id})
            return redirect(url_for('chores_list'))
        else:
            message = result.get('error', 'Failed to add chore') if isinstance(result, dict) else 'Failed to add chore'
            if request.is_json:
                return jsonify({'error': message}), status
            return render_template('add_chore.html', people=_collection_items(api_call('GET', '/people/')[1], 'people'), error=message), status
    
    # GET: Show form
    status, people_data = api_call('GET', '/people/')
    people = _collection_items(people_data, 'people') if status == 200 else []
    return render_template('add_chore.html', people=people)


@app.route('/chores/<int:chore_id>/edit', methods=['GET', 'POST'])
def edit_chore(chore_id):
    """Edit chore (admin only)."""
    if 'token' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        data = request.get_json(silent=True) or request.form
        status, result = api_call('PUT', f'/chores/{chore_id}', {
            'name': data.get('name'),
            'description': data.get('description'),
            'person_id': data.get('person_id') or data.get('assigned_to') or None
        })
        
        if status == 200:
            if request.is_json:
                return jsonify({'success': True})
            return redirect(url_for('chore_detail', chore_id=chore_id))
        else:
            message = result.get('error', 'Failed to update') if isinstance(result, dict) else 'Failed to update'
            if request.is_json:
                return jsonify({'error': message}), status
            status2, chore = api_call('GET', f'/chores/{chore_id}')
            status3, people_data = api_call('GET', '/people/')
            people = _collection_items(people_data, 'people') if status3 == 200 else []
            return render_template('edit_chore.html', chore=chore, people=people, error=message), status
    
    # GET: Show form
    status, chore = api_call('GET', f'/chores/{chore_id}')
    if status != 200:
        return f"Chore not found: {chore}", 404
    
    status, people_data = api_call('GET', '/people/')
    people = _collection_items(people_data, 'people') if status == 200 else []
    
    return render_template('edit_chore.html', chore=chore, people=people)


@app.route('/chores/<int:chore_id>/complete', methods=['POST'])
def complete_chore(chore_id):
    """Mark chore as complete."""
    if 'token' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    status, result = api_call('POST', f'/chores/{chore_id}/complete', {})

    # If the caller expects JSON (AJAX), return JSON. Otherwise redirect to the chore detail
    wants_json = request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 'application/json' in request.headers.get('Accept', '')

    if status == 200:
        if wants_json:
            return jsonify({'success': True, 'chore': result})
        # Redirect back to the chore detail page for normal form submissions
        return redirect(url_for('chore_detail', chore_id=chore_id))
    else:
        message = result.get('error', 'Failed to complete') if isinstance(result, dict) else 'Failed to complete'
        if wants_json:
            return jsonify({'error': message}), status
        # For non-AJAX, render the chore detail page with an error message
        status2, chore = api_call('GET', f'/chores/{chore_id}')
        return render_template('chore_detail.html', chore=chore, error=message), status


@app.route('/chores/<int:chore_id>/delete', methods=['POST'])
def delete_chore(chore_id):
    """Delete chore (admin only)."""
    if 'token' not in session:
        return redirect(url_for('login'))
    
    status, result = api_call('DELETE', f'/chores/{chore_id}')
    
    if status in (200, 204):
        if request.is_json:
            return jsonify({'success': True})
        return redirect(url_for('chores_list'))
    else:
        message = result.get('error', 'Failed to delete') if isinstance(result, dict) else 'Failed to delete'
        if request.is_json:
            return jsonify({'error': message}), status
        status2, data = api_call('GET', '/chores/')
        chores = _collection_items(data, 'chores') if status2 == 200 else []
        return render_template('chores_list.html', chores=chores, error=message), status


@app.route('/verify_pin', methods=['POST'])
def verify_pin():
    """Validate PIN entry for modal-driven actions.

    The browser bridge keeps the current login_name in session, so we can
    reuse the auth endpoint to verify the entered PIN against the logged-in
    person before allowing the form submit to proceed.
    """
    if 'token' not in session or 'login_name' not in session:
        return jsonify({'status': 'failure'}), 401

    data = request.get_json(silent=True) or {}
    context = data.get('context')
    pin = data.get('pin')

    if not pin or not context:
        return jsonify({'status': 'failure'})

    status, auth_result = api_call('POST', '/auth/login', {
        'login_name': session['login_name'],
        'pin': pin,
    })
    if status != 200 or not isinstance(auth_result, dict):
        # Cannot verify PIN (invalid credentials)
        return jsonify({'status': 'failure', 'reason': 'invalid'})

    # Refresh the bridge session with the latest backend token/role so a
    # just-promoted admin can immediately perform admin actions.
    session['token'] = auth_result.get('access_token')
    session['person_id'] = auth_result.get('person_id')
    session['is_admin'] = bool(auth_result.get('is_admin'))
    # Keep login_name normalized in session (lowercase)
    _ln = session.get('login_name') or data.get('login_name')
    if _ln:
        session['login_name'] = _ln.strip().lower()

    is_admin = bool(auth_result.get('is_admin'))
    if context == 'add_person':
        status2, people_data = api_call('GET', '/people/')
        people = _collection_items(people_data, 'people') if status2 == 200 else []
        if is_admin or not people:
            return jsonify({'status': 'success'})
        return jsonify({'status': 'failure', 'reason': 'not_admin'})

    if context == 'complete_chore':
        return jsonify({'status': 'success'})

    if context in {'change_sequence', 'delete_chore', 'delete_person', 'edit_chore', 'edit_person'}:
        return jsonify({'status': 'success' if is_admin else 'failure', 'reason': (None if is_admin else 'not_admin')})

    return jsonify({'status': 'failure', 'reason': 'invalid'})


@app.route('/people')
def people_list():
    """List all people."""
    if 'token' not in session:
        return redirect(url_for('login'))
    
    status, data = api_call('GET', '/people/')
    if status != 200:
        return f"Error: {data}", 500
    
    people = _collection_items(data, 'people')
    return render_template('edit_people.html', people=people)


@app.route('/people/<int:person_id>', methods=['GET', 'POST'])
def person_detail(person_id):
    """View or update a person."""
    if 'token' not in session:
        return redirect(url_for('login'))
    
    status, person = api_call('GET', f'/people/{person_id}')
    if status != 200:
        return f"Person not found: {person}", 404
    
    if request.method == 'POST':
        data = request.get_json(silent=True) or request.form
        payload = {
            'first_name': data.get('first_name'),
            'last_name': data.get('last_name'),
            'birthday': data.get('birthday'),
            'is_admin': data.get('is_admin') in ('on', 'true', '1', True),
            'assign_chores': data.get('assign_chores') in ('on', 'true', '1', True),
        }
        status, result = api_call('PUT', f'/people/{person_id}', payload)
        if status == 200:
            if request.is_json:
                return jsonify({'success': True})
            return redirect(url_for('person_detail', person_id=person_id))
        message = result.get('error', 'Failed to update person') if isinstance(result, dict) else 'Failed to update person'
        if request.is_json:
            return jsonify({'error': message}), status
        return render_template('edit_person.html', person=person, error=message), status
    
    return render_template('edit_person.html', person=person)


@app.route('/people/add', methods=['GET', 'POST'])
def add_person():
    """Add new person."""
    if request.method == 'POST':
        data = request.get_json(silent=True) or request.form
        payload = {
            'first_name': data.get('first_name'),
            'last_name': data.get('last_name'),
            'login_name': data.get('login_name'),
            'birthday': data.get('birthday'),
            'pin': data.get('pin'),
            'is_admin': data.get('is_admin', False),
            'assign_chores': data.get('assign_chores', False),
        }
        if hasattr(payload['is_admin'], 'lower'):
            payload['is_admin'] = str(payload['is_admin']).lower() in ('1', 'true', 'on', 'yes')
        if hasattr(payload['assign_chores'], 'lower'):
            payload['assign_chores'] = str(payload['assign_chores']).lower() in ('1', 'true', 'on', 'yes')
        status, result = api_call('POST', '/people/', payload)
        
        if status == 201 or status == 200:
            if request.is_json:
                person_id = result.get('id') if isinstance(result, dict) else None
                return jsonify({'success': True, 'person_id': person_id})
            return redirect(url_for('login'))
        else:
            message = result.get('error', 'Failed to add person') if isinstance(result, dict) else 'Failed to add person'
            if status in (401, 403) and not request.is_json:
                message = (
                    'Please log in as an admin to add a person, or use the '
                    'bootstrap registration path when no admins exist.'
                )
            app.logger.warning('Add person failed status=%s payload=%s', status, result)
            if request.is_json:
                return jsonify({'error': message}), status
            return render_template('add_person.html', form_action=url_for('add_person'), error=message), status
    
    # GET: Show form
    return render_template('add_person.html', form_action=url_for('add_person'))


@app.route('/people/<int:person_id>/delete', methods=['POST'])
def delete_person(person_id):
    """Delete a person."""
    if 'token' not in session:
        return redirect(url_for('login'))

    status, result = api_call('DELETE', f'/people/{person_id}')
    if status == 204:
        if request.is_json:
            return jsonify({'success': True})
        return redirect(url_for('people_list'))

    message = result.get('error', 'Failed to delete person') if isinstance(result, dict) else 'Failed to delete person'
    if request.is_json:
        return jsonify({'error': message}), status
    return render_template('edit_person.html', person=api_call('GET', f'/people/{person_id}')[1], error=message), status


@app.route('/people/<int:person_id>/edit_pin', methods=['GET', 'POST'])
def edit_pin(person_id):
    """PIN change placeholder until the FastAPI backend exposes a PIN update endpoint."""
    if 'token' not in session:
        return redirect(url_for('login'))
    status, person = api_call('GET', f'/people/{person_id}')
    if status != 200:
        return f"Person not found: {person}", 404
    if request.method == 'POST':
        message = 'PIN change is not yet implemented in the FastAPI backend.'
        if request.is_json:
            return jsonify({'error': message}), 501
        return render_template('edit_pin.html', person=person, error=message), 501
    return render_template('edit_pin.html', person=person)


@app.route('/change_sequence', methods=['GET', 'POST'])
def change_sequence():
    """Render the change-sequence page and return a clear placeholder on POST."""
    if 'token' not in session:
        return redirect(url_for('login'))

    status, data = api_call('GET', '/people/')
    people = _collection_items(data, 'people') if status == 200 else []
    if request.method == 'POST':
        message = 'Sequence updates are not yet implemented in the FastAPI backend.'
        if request.is_json:
            return jsonify({'error': message}), 501
        return render_template('change_sequence.html', people=people, error=message), 501

    return render_template('change_sequence.html', people=people)


@app.route('/update_sequence', methods=['POST'])
def update_sequence():
    """Proxy a sequence update to the FastAPI backend.

    Expects JSON: { sequence_data: JSON-stringified list [{id, sequence}, ...] }
    Returns JSON on AJAX requests, otherwise redirects to people list.
    """
    if 'token' not in session:
        return redirect(url_for('login'))

    data = request.get_json(silent=True) or request.form
    seq_raw = data.get('sequence_data')
    try:
        if isinstance(seq_raw, str):
            seq = json.loads(seq_raw)
        else:
            seq = seq_raw
        # normalize types
        seq = [{'id': int(x['id']), 'sequence': int(x['sequence'])} for x in seq]
    except Exception as e:
        app.logger.exception('Bad sequence_data payload: %s', e)
        if request.is_json:
            return jsonify({'error': 'Bad sequence data'}), 400
        return render_template('change_sequence.html', people=_collection_items(api_call('GET', '/people/')[1], 'people'), error='Invalid sequence payload'), 400

    status, result = api_call('POST', '/people/sequence', seq)
    if status == 200:
        if request.is_json:
            # Return both old and new shapes for compatibility: boolean 'success' and 'status' string
            return jsonify({'success': True, 'status': 'success'})
        return redirect(url_for('people_list'))
    else:
        message = result.get('error', 'Failed to update sequence') if isinstance(result, dict) else 'Failed to update sequence'
        if request.is_json:
            return jsonify({'error': message, 'status': 'failure'}), status
        people = _collection_items(api_call('GET', '/people/')[1], 'people')
        return render_template('change_sequence.html', people=people, error=message), status


@app.route('/api/health')
def health_check():
    """Health check - test backend connectivity."""
    status, result = api_call('GET', '/health')
    
    if status == 200:
        return jsonify({
            'status': 'ok',
            'frontend': 'Flask (Jinja2)',
            'backend': 'FastAPI',
            'backend_response': result
        })
    else:
        return jsonify({
            'status': 'error',
            'message': 'Cannot reach FastAPI backend',
            'hint': 'Make sure FastAPI is running: python api_run.py',
            'error': result
        }), status


# =============================================================================
# Error handlers
# =============================================================================

@app.errorhandler(404)
def not_found(e):
    """404 handler."""
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    """500 handler."""
    return render_template('500.html', error=str(e)), 500


if __name__ == '__main__':
    print(f"""
╔════════════════════════════════════════════════════════════════╗
║     Flask Frontend Bridge to FastAPI Backend                  ║
╚════════════════════════════════════════════════════════════════╝

🔗 API Backend:  {API_BASE_URL}
🌐 Frontend:     http://localhost:{FLASK_PORT}

📝 To test:
   1. Start FastAPI backend (in another terminal):
      python api_run.py

   2. Then visit:
      http://localhost:{FLASK_PORT}

   3. Health check:
      http://localhost:{FLASK_PORT}/api/health

""")
    app.run(debug=False, use_reloader=False, host='0.0.0.0', port=FLASK_PORT)
