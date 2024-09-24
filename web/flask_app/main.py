from flask import Flask
from choreboss.config import Config
from choreboss.models import Base
from sqlalchemy import create_engine

from choreboss.models.person import Person
from choreboss.models.chore import Chore


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    Base.metadata.create_all(engine)

    from web.flask_app.routes.person_routes import person_bp
    from web.flask_app.routes.chore_routes import chore_bp

    app.register_blueprint(person_bp)
    app.register_blueprint(chore_bp)

    return app
