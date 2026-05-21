from flask import (Blueprint, current_app, render_template, Response)
from typing import Union


index_bp = Blueprint('index_bp', __name__)


@index_bp.route('/', methods=['GET'])
def home() -> Union[Response, str]:
    """
    Render the home page with a list of people and chores.

    Returns:
        Any: The rendered template for the home page.
    """
    people = current_app.people_service.get_all_people()
    chores = current_app.chore_service.get_all_chores()

    return render_template('index.html', people=people, chores=chores)
