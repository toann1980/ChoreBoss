from datetime import datetime
from flask import (
    Blueprint, jsonify, redirect, request, render_template, url_for
)
from choreboss.repositories.people_repository import PeopleRepository
from choreboss.services.people_service import PeopleService
from choreboss.schemas.people_schema import PeopleSchema
from sqlalchemy import create_engine
from choreboss.config import Config

people_bp = Blueprint('people_bp', __name__)
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
people_repository = PeopleRepository(engine)
people_service = PeopleService(people_repository)
people_schema = PeopleSchema()


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
        return redirect(url_for('people_bp.get_person', person_id=person.id))

    return render_template('edit_person.html', person=person)


@people_bp.route('/people', methods=['GET'])
def get_people():
    people = people_service.get_all_people()
    return render_template('edit_people.html', people=people)


@people_bp.route('/people/<int:person_id>', methods=['GET'])
def get_person(person_id):
    person = people_service.get_person_by_id(person_id)
    if person:
        return render_template('person_detail.html', person=person)
    else:
        return jsonify({'error': 'Person not found'}), 404


@people_bp.route('/verify_pin', methods=['POST'])
def verify_pin():
    data = request.get_json()
    pin = data.get('pin')
    person = people_service.get_person_by_pin(pin)
    if person and person.is_admin:
        return jsonify({'is_admin': True})
    return jsonify({'is_admin': False})
