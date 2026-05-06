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
import requests
import os
from datetime import datetime
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

# =============================================================================
# Helper functions to call FastAPI backend
# =============================================================================

def get_auth_headers():
    """Get Authorization header if user is logged in."""
    token = session.get('token')
    if token:
        return {'Authorization': f'Bearer {token}'}
    return {}


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
        
        data = resp.json() if resp.text else {}
        if isinstance(data, dict) and 'detail' in data and 'error' not in data:
            data['error'] = data['detail']
        return resp.status_code, data
    except requests.exceptions.ConnectionError:
        return 503, {
            'error': 'Cannot connect to FastAPI backend',
            'hint': 'Make sure FastAPI is running: python api_run.py'
        }
    except Exception as e:
        return 500, {'error': str(e)}


# =============================================================================
# Routes
# =============================================================================

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
    
    chores = chores_data.get('chores', [])
    people = people_data.get('people', [])
    
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
            session['token'] = result.get('access_token')
            session['person_id'] = result.get('person_id')
            session['login_name'] = login_name
            return jsonify({'success': True})
        else:
            return jsonify({'error': result.get('error', 'Login failed')}), status
    
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
    
    chores = data.get('chores', [])
    return render_template('chores_list.html', chores=chores)


@app.route('/chores/<int:chore_id>')
def chore_detail(chore_id):
    """View chore details."""
    if 'token' not in session:
        return redirect(url_for('login'))
    
    status, chore = api_call('GET', f'/chores/{chore_id}')
    if status != 200:
        return f"Chore not found: {chore}", 404
    
    return render_template('chore_detail.html', chore=chore)


@app.route('/chores/add', methods=['GET', 'POST'])
def add_chore():
    """Add new chore (admin only)."""
    if 'token' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        data = request.get_json()
        status, result = api_call('POST', '/chores/', {
            'name': data.get('name'),
            'description': data.get('description'),
            'person_id': data.get('person_id')
        })
        
        if status == 201:
            return jsonify({'success': True, 'chore_id': result.get('id')})
        else:
            return jsonify({'error': result.get('error', 'Failed to add chore')}), status
    
    # GET: Show form
    status, people_data = api_call('GET', '/people/')
    people = people_data.get('people', []) if status == 200 else []
    return render_template('add_chore.html', people=people)


@app.route('/chores/<int:chore_id>/edit', methods=['GET', 'POST'])
def edit_chore(chore_id):
    """Edit chore (admin only)."""
    if 'token' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        data = request.get_json()
        status, result = api_call('PUT', f'/chores/{chore_id}', {
            'name': data.get('name'),
            'description': data.get('description'),
            'person_id': data.get('person_id')
        })
        
        if status == 200:
            return jsonify({'success': True})
        else:
            return jsonify({'error': result.get('error', 'Failed to update')}), status
    
    # GET: Show form
    status, chore = api_call('GET', f'/chores/{chore_id}')
    if status != 200:
        return f"Chore not found: {chore}", 404
    
    status, people_data = api_call('GET', '/people/')
    people = people_data.get('people', []) if status == 200 else []
    
    return render_template('edit_chore.html', chore=chore, people=people)


@app.route('/chores/<int:chore_id>/complete', methods=['POST'])
def complete_chore(chore_id):
    """Mark chore as complete."""
    if 'token' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    status, result = api_call('POST', f'/chores/{chore_id}/complete', {})
    
    if status == 200:
        return jsonify({'success': True, 'chore': result})
    else:
        return jsonify({'error': result.get('error', 'Failed to complete')}), status


@app.route('/chores/<int:chore_id>/delete', methods=['POST'])
def delete_chore(chore_id):
    """Delete chore (admin only)."""
    if 'token' not in session:
        return redirect(url_for('login'))
    
    status, result = api_call('DELETE', f'/chores/{chore_id}')
    
    if status == 200:
        return jsonify({'success': True})
    else:
        return jsonify({'error': result.get('error', 'Failed to delete')}), status


@app.route('/people')
def people_list():
    """List all people."""
    if 'token' not in session:
        return redirect(url_for('login'))
    
    status, data = api_call('GET', '/people/')
    if status != 200:
        return f"Error: {data}", 500
    
    people = data.get('people', [])
    return render_template('edit_people.html', people=people)


@app.route('/people/<int:person_id>')
def person_detail(person_id):
    """View person details."""
    if 'token' not in session:
        return redirect(url_for('login'))
    
    status, person = api_call('GET', f'/people/{person_id}')
    if status != 200:
        return f"Person not found: {person}", 404
    
    return render_template('edit_person.html', person=person)


@app.route('/people/add', methods=['GET', 'POST'])
def add_person():
    """Add new person (admin only)."""
    if 'token' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        data = request.get_json()
        status, result = api_call('POST', '/people/', {
            'first_name': data.get('first_name'),
            'last_name': data.get('last_name'),
            'birthday': data.get('birthday'),
            'pin': data.get('pin'),
            'is_admin': data.get('is_admin', False)
        })
        
        if status == 201:
            return jsonify({'success': True, 'person_id': result.get('id')})
        else:
            return jsonify({'error': result.get('error', 'Failed to add person')}), status
    
    # GET: Show form
    return render_template('add_person.html')


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
    app.run(debug=True, host='0.0.0.0', port=FLASK_PORT)
