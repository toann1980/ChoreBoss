from flask import (
    Blueprint, jsonify, redirect, render_template, request, url_for
)
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


@chore_bp.route('/chores', methods=['GET', 'POST'])
def add_chore():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        chore_service.add_chore(name, description)
        return redirect(url_for('index_bp.home'))

    return render_template('add_chore.html')


@chore_bp.route('/chores', methods=['GET'])
def get_all_chores():
    chores = chore_service.get_all_chores()
    return render_template('chores_list.html', chores=chores)


@chore_bp.route('/chores/<int:chore_id>', methods=['GET'])
def get_chore(chore_id):
    chore = chore_service.get_chore_by_id(chore_id)
    if chore:
        return render_template('chore_detail.html', chore=chore)
    else:
        return jsonify({'error': 'Chore not found'}), 404
