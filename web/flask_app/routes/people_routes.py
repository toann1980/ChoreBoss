from datetime import datetime
from flask import (
    Blueprint, current_app, jsonify, redirect, request, render_template,
    Response, url_for
)
import json


people_bp = Blueprint('people_bp', __name__)


@people_bp.route('/add_person', methods=['GET', 'POST'])
def add_person() -> Response:
    """Add a new person.

    Returns:
        Response: The rendered template for adding a person or a redirect to the
            home page.
    """
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        birthday_str = request.form['birthday']
        pin = request.form['pin']
        is_admin = 'is_admin' in request.form
        birthday = datetime.strptime(birthday_str, '%Y-%m-%d').date()
        current_app.people_service.add_person(
            first_name, last_name, birthday, pin, is_admin)
        return redirect(url_for('index_bp.home'))

    # Check if there are any admins
    admins_exist = current_app.people_service.admins_exist()
    return render_template('add_person.html', admins_exist=admins_exist)


@people_bp.route('/delete_person', methods=['POST'])
def delete_person() -> Response:
    """Delete a person and adjust the sequence.

    Returns:
        Response: A redirect to the list of people.
    """
    person_id = request.form['person_id']
    current_app.people_service.delete_person_and_adjust_sequence(person_id)
    return redirect(url_for('people_bp.get_people'))


@people_bp.route('/people/<int:person_id>/edit', methods=['GET', 'POST'])
def edit_person(person_id: int) -> Response:
    """Edit a person's details.

    Args:
        person_id (int): The ID of the person to edit.

    Returns:
        Response: The rendered template for editing a person or a redirect to
            the person's edit page.
    """
    person = current_app.people_service.get_person_by_id(person_id)
    if not person:
        return jsonify({'error': 'Person not found'}), 404

    if request.method == 'POST':
        person.first_name = request.form['first_name']
        person.last_name = request.form['last_name']
        birthday_str = request.form['birthday']
        person.birthday = datetime.strptime(birthday_str, '%Y-%m-%d').date()
        person.is_admin = 'is_admin' in request.form
        current_app.people_service.update_person(person)
        person = current_app.people_service.get_person_by_id(person_id)

    return render_template('edit_person.html', person=person)


@people_bp.route('/people/<int:person_id>/edit_pin', methods=['GET', 'POST'])
def edit_pin(person_id: int) -> Response:
    """Edit a person's PIN.

    Args:
        person_id (int): The ID of the person to edit the PIN for.

    Returns:
        Response: The rendered template for editing a person's PIN or a redirect
            to the person's edit page.
    """
    person = current_app.people_service.get_person_by_id(person_id)
    if not person:
        return jsonify({'error': 'Person not found'}), 404

    if request.method == 'POST':
        current_pin = request.form['current_pin']
        new_pin = request.form['new_pin']
        confirm_pin = request.form['confirm_pin']

        if new_pin != confirm_pin:
            return jsonify({'error': 'New PINs do not match'}), 400

        if not person.verify_pin(current_pin):
            return jsonify({'error': 'Current PIN is incorrect'}), 400

        person.set_pin(new_pin)
        current_app.people_service.update_person(person)
        return redirect(url_for('people_bp.edit_person', person_id=person_id))

    return render_template('edit_pin.html', person=person)


@people_bp.route('/people', methods=['GET'])
def get_people() -> Response:
    """Get the list of all people.

    Returns:
        Response: The rendered template with the list of people.
    """
    people = current_app.people_service.get_all_people()
    return render_template('edit_people.html', people=people)


@people_bp.route('/change_sequence', methods=['GET'])
def change_sequence() -> Response:
    """Render the change sequence page.

    Returns:
        Response: The rendered template for changing the sequence of people.
    """
    people = current_app.people_service.get_all_people()
    return render_template('change_sequence.html', people=people)


@people_bp.route('/update_sequence', methods=['POST'])
def update_sequence() -> Response:
    """Update the sequence of people.

    Returns:
        Response: A JSON response indicating the status of the update.
    """
    data = request.get_json()
    print(f'data: {data}')
    data = json.loads(data.get('sequence_data'))
    for item in data:
        current_app.people_service.update_sequence(
            item['id'], item['sequence'])
    return jsonify({'status': 'success'})


@people_bp.route('/verify_pin', methods=['POST'])
def verify_pin() -> Response:
    """Verify a person's PIN.

    Returns:
        Response: A JSON response indicating the status of the verification.
    """
    data = request.get_json()
    print(f'data: {data}')
    context = data.get('context')
    pin = data.get('pin')

    if context == 'complete_chore':
        chore_id = data.get('chore_id')
        chore = current_app.chore_service.get_chore_by_id(chore_id)
        next_person = \
            current_app.people_service.get_next_person_by_person_id(
                chore.person_id)
        if next_person.verify_pin(pin) or \
                current_app.people_service.is_admin(pin):
            return jsonify({'status': 'success'})
    elif context == 'add_person':
        if current_app.people_service.is_admin(pin) or \
                not current_app.people_service.admins_exist():
            return jsonify({'status': 'success'})
    elif context == 'edit_person':
        person = current_app.people_service.get_person_by_pin(pin)
        if person and (person.is_admin or person.verify_pin(pin)):
            return jsonify({'status': 'success'})
    elif context in (
        'change_sequence', 'delete_chore', 'delete_person', 'edit_chore'
    ):
        person = current_app.people_service.get_person_by_pin(pin)
        if person and person.is_admin:
            return jsonify({'status': 'success'})

    return jsonify({'status': 'failure'})
