from flask import (
    Blueprint, jsonify, redirect, render_template, request, url_for
)
from choreboss.repositories.chore_repository import ChoreRepository
from choreboss.repositories.people_repository import PeopleRepository
from choreboss.services.chore_service import ChoreService
from choreboss.services.people_service import PeopleService
from choreboss.schemas.chore_schema import ChoreSchema
from sqlalchemy import create_engine
from choreboss.config import Config

chore_bp = Blueprint('chore_bp', __name__)
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
people_repository = PeopleRepository(engine)
people_service = PeopleService(people_repository)
chore_repository = ChoreRepository(engine)
chore_service = ChoreService(chore_repository, people_repository)
chore_schema = ChoreSchema()


@chore_bp.route('/chores', methods=['GET', 'POST'])
def add_chore():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        chore_service.add_chore(name, description)
        return redirect(url_for('index_bp.home'))

    return render_template('add_chore.html')


@chore_bp.route('/chore/<int:chore_id>/complete', methods=['POST'])
def complete_chore(chore_id):
    chore = chore_service.get_chore_by_id(chore_id)
    if not chore:
        return jsonify({'error': 'Chore not found'}), 404

    chore_service.complete_chore(chore)
    return redirect(url_for('chore_bp.get_chore', chore_id=chore.id))


@chore_bp.route('/delete_chore/<int:chore_id>', methods=['POST'])
def delete_chore(chore_id):
    chore = chore_service.get_chore_by_id(chore_id)
    if not chore:
        return jsonify({'error': 'Chore not found'}), 404

    chore_service.delete_chore(chore_id)
    return redirect(url_for('index_bp.home'))


@chore_bp.route('/chores/<int:chore_id>/edit', methods=['GET', 'POST'])
def edit_chore(chore_id):
    chore = chore_service.get_chore_by_id(chore_id)
    if not chore:
        return jsonify({'error': 'Chore not found'}), 404

    if request.method == 'POST':
        chore.name = request.form['name']
        chore.description = request.form['description']
        assigned_to = request.form['assigned_to']
        chore.person_id = int(assigned_to) if assigned_to else None
        chore_service.update_chore(chore)
        return redirect(url_for('chore_bp.get_chore', chore_id=chore.id))

    people = people_service.get_all_people()
    return render_template('edit_chore.html', chore=chore, people=people)


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
