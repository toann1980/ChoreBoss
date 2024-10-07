from flask import Flask
import os
from sqlalchemy import create_engine

from choreboss.config import Config
from choreboss.models import Base
from choreboss.models.people import People
from choreboss.models.chore import Chore
from web.flask_app.routes.people_routes import people_bp
from web.flask_app.routes.chore_routes import chore_bp
from web.flask_app.routes.index_routes import index_bp


def create_app() -> Flask:
    """
    Create and configure the Flask application.
    This function sets up the Flask application with the necessary
    configurations, including static and template folders, secret key, and
    SQLAlchemy database URI. It also registers the blueprints for different
    parts of the application.
    Returns:
        Flask: The configured Flask application instance.
    """
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

    for bp in (people_bp, chore_bp, index_bp):
        app.register_blueprint(bp)

    return app
