from flask import Flask
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from choreboss import setup_services
from choreboss.config import Config, TestingConfig
from choreboss.models import Base
from web.flask_app.routes.people_routes import people_bp
from web.flask_app.routes.chore_routes import chore_bp
from web.flask_app.routes.index_routes import index_bp


def create_app(config_name: str = None) -> Flask:
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

    if config_name == 'testing':
        app.config.from_object(TestingConfig)
    else:
        app.config.from_object(Config)

    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    Base.metadata.create_all(engine)
    app.people_service, app.chore_service = setup_services(engine)

    # Store the engine and sessionmaker in the app config for use in tests
    app.config['ENGINE'] = engine
    app.config['SESSIONMAKER'] = sessionmaker(bind=engine)

    for bp in (people_bp, chore_bp, index_bp):
        app.register_blueprint(bp)

    return app
