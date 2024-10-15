import unittest
import pytest
from flask import Flask
from sqlalchemy.orm import sessionmaker
from web.flask_app.main import create_app


class _BaseFlaskAppMain(unittest.TestCase):
    CONFIG_CLASS = None

    @classmethod
    def setUpClass(cls):
        """Set up the test environment before any tests run."""
        print(f'CONFIG_CLASS: {cls.CONFIG_CLASS}')
        cls.app = create_app(cls.CONFIG_CLASS)
        cls.client = cls.app.test_client()
        cls.app_context = cls.app.app_context()
        cls.app_context.push()

    @classmethod
    def tearDownClass(cls):
        """Clean up the test environment after all tests."""
        cls.app_context.pop()

    def test_app_creation(self):
        """Test if the Flask app is created correctly."""
        self.assertIsInstance(self.app, Flask)
        if self.CONFIG_CLASS == 'testing':
            self.assertTrue(self.app.config['TESTING'])
            self.assertEqual(
                self.app.config['SQLALCHEMY_DATABASE_URI'],
                'sqlite:///:memory:'
            )
        else:
            self.assertFalse(self.app.config['TESTING'])

    def test_blueprints_registration(self):
        """Test if the blueprints are registered correctly."""
        self.assertIn('people_bp', self.app.blueprints)
        self.assertIn('chore_bp', self.app.blueprints)
        self.assertIn('index_bp', self.app.blueprints)

    def test_services_setup(self):
        """Test if the services are set up correctly."""
        self.assertIsNotNone(self.app.people_service)
        self.assertIsNotNone(self.app.chore_service)

    def test_engine_and_sessionmaker(self):
        """Test if the engine and sessionmaker are stored in the app config."""
        self.assertIn('ENGINE', self.app.config)
        self.assertIn('SESSIONMAKER', self.app.config)
        self.assertIsInstance(self.app.config['SESSIONMAKER'], sessionmaker)


class TestFlaskAppMainTestingConfig(_BaseFlaskAppMain):
    CONFIG_CLASS = 'testing'
