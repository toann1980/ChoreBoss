from flask import Blueprint, request, jsonify
from choreboss.repositories.person_repository import PersonRepository
from choreboss.services.person_service import PersonService
from choreboss.schemas.person_schema import PersonSchema
from sqlalchemy import create_engine
from choreboss.config import Config

person_bp = Blueprint('person_bp', __name__)
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
person_repository = PersonRepository(engine)
person_service = PersonService(person_repository)
person_schema = PersonSchema()


@person_bp.route('/people', methods=['POST'])
def add_person():
    data = request.get_json()
    person = person_service.add_person(data['name'])
    return person_schema.jsonify(person)


@person_bp.route('/people', methods=['GET'])
def get_all_people():
    people = person_service.get_all_people()
    return person_schema.jsonify(people, many=True)
