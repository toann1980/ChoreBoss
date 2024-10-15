import os
from dotenv import load_dotenv

load_dotenv()


class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL', 'sqlite:///choreboss.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY')


class TestingConfig:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    TESTING = True
    SECRET_KEY = 'testing_secret_key'
