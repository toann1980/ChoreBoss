from flask import Blueprint, request, jsonify
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


@people_bp.route('/people', methods=['POST'])
def add_person():
    data = request.get_json()
    people = people_service.add_person(
        data['first_name'], data['last_name'], data['age'])
    return people_schema.jsonify(people)


@people_bp.route('/people', methods=['GET'])
def get_all_people():
    people = people_service.get_all_people()
    return jsonify(people_schema.dump(people, many=True))
