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
        birthday = datetime.strptime(birthday_str, '%Y-%m-%d').date()
        people_service.add_person(first_name, last_name, birthday)
        return redirect(url_for('index_bp.home'))

    return render_template('add_person.html')


@people_bp.route('/people', methods=['GET'])
def get_all_people():
    people = people_service.get_all_people()
    return jsonify(people_schema.dump(people, many=True))
