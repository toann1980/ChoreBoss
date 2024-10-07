from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import unittest
from web.flask_app.main import create_app
from choreboss.models import Base
from choreboss.models.chore import Chore
from choreboss.models.people import People
from choreboss.repositories.people_repository import PeopleRepository
from choreboss.repositories.chore_repository import ChoreRepository
from choreboss.services.people_service import PeopleService
from choreboss.services.chore_service import ChoreService
from ....setup_memory_records import setup_memory_records


class TestIndexRoutes(unittest.TestCase):
    def setUp(self) -> None:

        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()

        self.engine = self.app.config['ENGINE']
        self.Session = self.app.config['SESSIONMAKER']
        self.session = self.Session()

        self.people_repository = PeopleRepository(self.engine)
        self.chore_repository = ChoreRepository(self.engine)
        self.people_service = PeopleService(self.people_repository)
        self.chore_service = ChoreService(
            self.chore_repository, self.people_repository)

        setup_memory_records(self.people_repository, self.chore_repository)

        self.client = self.app.test_client()

    def tearDown(self):
        self.session.close()
        Base.metadata.drop_all(self.engine)

    def test_home_route(self):
        """
        Test the home route of the Flask application.

        This method sends a GET request to the home route of the Flask
        application and prints the type of the response received.

        Assertions:
            - None

        Prints:
            - The type of the response object.
        """
        response = self.client.get('/')
        print(f'response type: {type(response)}')

    def test_home_route_json_response_is_none(self):
        """
        Test the home route to ensure it returns the correct content type and 
        that the JSON response is None.
        """
        response = self.client.get('/')
        self.assertEqual(response.content_type, 'text/html; charset=utf-8')
        json_data = response.get_json()
        self.assertIsNone(json_data)

    def test_home_route_post_method(self):
        """
        Test the POST method on the home route.

        This test ensures that sending a POST request to the home route ('/')
        returns a 405 Method Not Allowed status code.

        Asserts:
            response.status_code (int): The HTTP status code of the response
                should be 405.
        """
        response = self.client.post('/')
        self.assertEqual(response.status_code, 405)

    def test_home_route_put_method(self):
        """
        Test the PUT method on the home route.

        This test ensures that sending a PUT request to the home route ('/')
        returns a 405 Method Not Allowed status code.

        Asserts:
            response.status_code (int): The HTTP status code of the response
                should be 405.
        """
        response = self.client.put('/')
        self.assertEqual(response.status_code, 405)

    def test_home_route_delete_method(self):
        """
        Test the DELETE method on the home route.

        This test ensures that sending a DELETE request to the home route ('/')
        returns a 405 Method Not Allowed status code.

        Assertions:
            - The response status code should be 405.
        """
        response = self.client.delete('/')
        self.assertEqual(response.status_code, 405)
