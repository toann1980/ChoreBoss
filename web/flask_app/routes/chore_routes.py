from flask import Blueprint, request, jsonify
from choreboss.repositories.chore_repository import ChoreRepository
from choreboss.services.chore_service import ChoreService
from choreboss.schemas.chore_schema import ChoreSchema
from sqlalchemy import create_engine
from choreboss.config import Config

chore_bp = Blueprint('chore_bp', __name__)
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
chore_repository = ChoreRepository(engine)
chore_service = ChoreService(chore_repository)
chore_schema = ChoreSchema()


@chore_bp.route('/chores', methods=['POST'])
def add_chore():
    data = request.get_json()
    chore = chore_service.add_chore(data['description'])
    return jsonify(chore_schema.dump(chore))


@chore_bp.route('/chores', methods=['GET'])
def get_all_chores():
    chores = chore_service.get_all_chores()
    return jsonify(chore_schema.dump(chores, many=True))
