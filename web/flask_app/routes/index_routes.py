from flask import (Blueprint, render_template)

from choreboss.schemas.chore_schema import ChoreSchema
from choreboss.schemas.people_schema import PeopleSchema
from web.flask_app.routes.chore_routes import chore_service
from web.flask_app.routes.people_routes import people_service


index_bp = Blueprint('index_bp', __name__)
chore_schema = ChoreSchema(many=True)
people_schema = PeopleSchema(many=True)


@index_bp.route('/', methods=['GET'])
def home():
    people = people_service.get_all_people()
    chores = chore_service.get_all_chores()

    return render_template('index.html', people=people, chores=chores)
