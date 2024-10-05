from datetime import datetime
from flask import (
    Blueprint, jsonify, redirect, request, render_template, url_for
)
from choreboss.repositories.chore_repository import ChoreRepository
from choreboss.services.chore_service import ChoreService
from choreboss.repositories.people_repository import PeopleRepository
from choreboss.repositories.people_repository import PeopleRepository
from choreboss.services.people_service import PeopleService
from choreboss.schemas.people_schema import PeopleSchema
from sqlalchemy import create_engine
from choreboss.config import Config

people_bp = Blueprint('people_bp', __name__)
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
chore_repository = ChoreRepository(engine)
chore_service = ChoreService(chore_repository)
people_repository = PeopleRepository(engine)
people_service = PeopleService(people_repository)
people_schema = PeopleSchema()


def fetch_people_in_sequence_order():
    return people_service.get_all_people_in_sequence_order()


@people_bp.route('/add_person', methods=['GET', 'POST'])
def add_person():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        birthday_str = request.form['birthday']
        pin = request.form['pin']
        is_admin = 'is_admin' in request.form
        birthday = datetime.strptime(birthday_str, '%Y-%m-%d').date()
        people_service.add_person(
            first_name, last_name, birthday, pin, is_admin)
        return redirect(url_for('index_bp.home'))

    # Check if there are any admins
    admins_exist = people_service.admins_exist()
    return render_template('add_person.html', admins_exist=admins_exist)


@people_bp.route('/delete_person', methods=['POST'])
def delete_person():
    person_id = request.form['person_id']
    people_service.delete_person_and_adjust_sequence(person_id)
    return redirect(url_for('people_bp.get_people'))


@people_bp.route('/people/<int:person_id>/edit', methods=['GET', 'POST'])
def edit_person(person_id):
    person = people_service.get_person_by_id(person_id)
    if not person:
        return jsonify({'error': 'Person not found'}), 404

    if request.method == 'POST':
        person.first_name = request.form['first_name']
        person.last_name = request.form['last_name']
        birthday_str = request.form['birthday']
        person.birthday = datetime.strptime(birthday_str, '%Y-%m-%d').date()
        person.is_admin = 'is_admin' in request.form
        people_service.update_person(person)
        person = people_service.get_person_by_id(person_id)

    return render_template('edit_person.html', person=person)


@people_bp.route('/people/<int:person_id>/edit_pin', methods=['GET', 'POST'])
def edit_pin(person_id):
    person = people_service.get_person_by_id(person_id)
    if not person:
        return jsonify({'error': 'Person not found'}), 404

    if request.method == 'POST':
        current_pin = request.form['current_pin']
        new_pin = request.form['new_pin']
        confirm_pin = request.form['confirm_pin']

        if new_pin != confirm_pin:
            return jsonify({'error': 'New PINs do not match'}), 400

        if not people_service.verify_pin(person_id, current_pin):
            return jsonify({'error': 'Current PIN is incorrect'}), 400

        people_service.update_pin(person_id, new_pin)
        return redirect(url_for('people_bp.edit_person', person_id=person_id))

    return render_template('edit_pin.html', person=person)


@people_bp.route('/people', methods=['GET'])
def get_people():
    people = fetch_people_in_sequence_order()
    return render_template('edit_people.html', people=people)


@people_bp.route('/change_sequence', methods=['GET'])
def change_sequence():
    people = fetch_people_in_sequence_order()
    return render_template('change_sequence.html', people=people)


@people_bp.route('/update_sequence', methods=['POST'])
def update_sequence():
    data = request.get_json()
    for item in data:
        people_service.update_sequence(item['id'], item['sequence'])
    return jsonify({'status': 'success'})


@people_bp.route('/verify_pin', methods=['POST'])
def verify_pin():
    data = request.get_json()
    print(f'data: {data}')
    context = data.get('context')
    pin = data.get('pin')

    if context == 'complete_chore':
        chore_id = data.get('chore_id')
        chore = chore_service.get_chore_by_id(chore_id)
        next_person = \
            people_service.get_next_person_by_person_id(chore.person_id)
        if people_service.verify_pin(next_person.id, pin) or \
                people_service.is_admin(pin):
            return jsonify({'status': 'success'})
    elif context == 'add_person':
        if people_service.is_admin(pin) or not people_service.admins_exist():
            return jsonify({'status': 'success'})
    elif context == 'edit_person':
        person = people_service.get_person_by_pin(pin)
        if person and (person.is_admin or person.verify_pin(pin)):
            return jsonify({'status': 'success'})
    elif context in ('delete_chore', 'delete_person', 'edit_chore'):
        person = people_service.get_person_by_pin(pin)
        if person and person.is_admin:
            return jsonify({'status': 'success'})

    return jsonify({'status': 'failure'})
