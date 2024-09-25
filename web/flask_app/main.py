from flask import Flask
import os
from sqlalchemy import create_engine

from choreboss.config import Config
from choreboss.models import Base
from choreboss.models.person import Person
from choreboss.models.chore import Chore
from web.flask_app.routes.person_routes import person_bp
from web.flask_app.routes.chore_routes import chore_bp
from web.flask_app.routes.index_routes import index_bp


def create_app():
    app = Flask(
        __name__,
        static_folder=os.path.join(os.path.dirname(__file__), '..', 'static'),
        template_folder=os.path.join(
            os.path.dirname(__file__), '..', 'templates'
        )
    )
    app.secret_key = Config.SECRET_KEY
    app.config.from_object(Config)

    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    Base.metadata.create_all(engine)

    for bp in (person_bp, chore_bp, index_bp):
        app.register_blueprint(bp)

    return app
