import unittest
from web.flask_app.main import create_app
from flask import current_app
from choreboss.models import Base
from ....setup_memory_records import setup_memory_records


class TestIndexRoutes(unittest.TestCase):
    def setUp(self) -> None:

        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()

        self.engine = self.app.config['ENGINE']
        self.Session = self.app.config['SESSIONMAKER']
        self.Session.expire_on_commit = False
        self.session = self.Session()

        setup_memory_records(self.app.people_service, self.app.chore_service)

        self.client = self.app.test_client()

    def tearDown(self):
        self.session.close()
        Base.metadata.drop_all(self.engine)

    def test_app(self):
        self.assertIsNotNone(self.app)
        self.assertEqual(current_app, self.app)

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
        self.assertEqual(response.request.path, '/')

    def test_home_route_json_response_is_none(self):
        """
        Test the home route to ensure it returns the correct content type and
        that the JSON response is None.
        """
        response = self.client.get('/')
        self.assertEqual(response.content_type, 'text/html; charset=utf-8')
        self.assertIsNone(response.get_json())

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
