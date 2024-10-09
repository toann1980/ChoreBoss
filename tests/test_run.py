import unittest
from web.flask_app.main import create_app


class TestRun(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up the test environment before any tests run."""
        cls.app = create_app()
        print(f'app.name: {cls.app.name}')
        cls.client = cls.app.test_client()
        cls.app_context = cls.app.app_context()
        cls.app_context.push()

    @classmethod
    def tearDownClass(cls):
        """Clean up the test environment after all tests."""
        cls.app_context.pop()

    def test_app_creation(self):
        """Test if the Flask app is created correctly."""
        self.assertIsNotNone(self.app)

    def test_app_config(self):
        """Test if the app runs with the correct configuration."""
        self.assertFalse(self.app.config['TESTING'])
        self.assertEqual(
            self.app.config['SQLALCHEMY_DATABASE_URI'],
            'sqlite:///choreboss.db'
        )
        self.assertFalse(self.app.debug)
