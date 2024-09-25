from flask import (
    Blueprint, jsonify, redirect, render_template, request, url_for
)
from user_agents import parse

from choreboss.schemas.chore_schema import ChoreSchema
from choreboss.schemas.people_schema import PeopleSchema
from web.flask_app.routes.chore_routes import chore_service
from web.flask_app.routes.people_routes import people_service

index_bp = Blueprint('index_bp', __name__)
chore_schema = ChoreSchema(many=True)
people_schema = PeopleSchema(many=True)

device_pattern = r'\(([^)]+)\)'


@index_bp.route('/', methods=['GET'])
def home():
    people = people_service.get_all_people()
    chores = chore_service.get_all_chores()

    people_json = people_schema.dump(people)
    chores_json = chore_schema.dump(chores)

    user_agent_string = request.headers.get('User-Agent')
    user_agent = parse(user_agent_string)

    if user_agent.is_mobile:
        return redirect(url_for('index_bp.mobile_home'))
    elif user_agent.is_tablet:
        return redirect(url_for('index_bp.tablet_home'))
    else:
        return redirect(url_for('index_bp.desktop_home'))


@index_bp.route('/mobile', methods=['GET'])
def mobile_home():
    return jsonify({'message': 'Welcome to the mobile site!'})


@index_bp.route('/tablet', methods=['GET'])
def tablet_home():
    return jsonify({'message': 'Welcome to the tablet site!'})


@index_bp.route('/desktop', methods=['GET'])
def desktop_home():
    people = people_service.get_all_people()
    chores = chore_service.get_all_chores()

    return render_template('desktop_home.html', people=people, chores=chores)
