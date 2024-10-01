from flask import Blueprint, jsonify, render_template, request

from choreboss.repositories.people_repository import PeopleRepository
from choreboss.repositories.sequence_repository import SequenceRepository
from choreboss.services.people_service import PeopleService
from choreboss.services.sequence_service import SequenceService
from choreboss.schemas.sequence_schema import SequenceSchema
from sqlalchemy import create_engine
from choreboss.config import Config

sequence_bp = Blueprint('sequence_bp', __name__)
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
people_repository = PeopleRepository(engine)
people_service = PeopleService(people_repository)
sequence_repository = SequenceRepository(engine)
sequence_service = SequenceService(sequence_repository)
sequence_schema = SequenceSchema()


@sequence_bp.route('/change_sequence', methods=['GET'])
def change_sequence():
    people = people_service.get_all_people_in_sequence_order()
    return render_template('change_sequence.html', people=people)


@sequence_bp.route('/update_sequence', methods=['POST'])
def update_sequence():
    sequence_data = request.get_json()
    print("Received sequence data:", sequence_data)
    for item in sequence_data:
        person_id = item['id']
        sequence = item['sequence']
        sequence_service.update_sequence(person_id, sequence)
    return jsonify({'status': 'success'})
