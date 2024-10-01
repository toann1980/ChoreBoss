from flask import Flask
import os
from sqlalchemy import create_engine

from choreboss.config import Config
from choreboss.models import Base
from choreboss.models.people import People
from choreboss.models.chore import Chore
from choreboss.models.sequence import Sequence
from web.flask_app.routes.people_routes import people_bp
from web.flask_app.routes.chore_routes import chore_bp
from web.flask_app.routes.index_routes import index_bp
from web.flask_app.routes.sequence_routes import sequence_bp


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

    for bp in (people_bp, chore_bp, index_bp, sequence_bp):
        app.register_blueprint(bp)

    return app
