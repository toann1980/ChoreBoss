from datetime import datetime
import json
import unittest
from web.flask_app.main import create_app
from choreboss.models import Base
from ....setup_memory_records import setup_memory_records


class TestPeopleRoutes(unittest.TestCase):
    def setUp(self) -> None:
        """
        Set up the test environment for the Flask application.
        This method initializes the Flask application in testing mode, sets up
        the application context, and configures the database engine and session.
        It also populates the in-memory records for the people and chore
        services and creates a test client for making HTTP requests.

        Attributes:
            app (Flask): The Flask application instance configured for testing.
            app_context (AppContext): The application context for the Flask app.
            engine (Engine): The SQLAlchemy engine used for database operations.
            Session (sessionmaker): The SQLAlchemy session factory.
            session (Session): The SQLAlchemy session instance.
            client (FlaskClient): The test client for making HTTP requests.
        """
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()

        self.engine = self.app.config['ENGINE']
        self.Session = self.app.config['SESSIONMAKER']
        self.Session.expire_on_commit = False
        self.session = self.Session()
        setup_memory_records(self.app.people_service, self.app.chore_service)

        self.client = self.app.test_client()

    def tearDown(self) -> None:
        self.session.close()
        Base.metadata.drop_all(self.engine)

    def test_add_chore_get(self):
        """
        Test the GET request to the '/chores' endpoint.

        This test ensures that the '/chores' page is accessible and contains the
        expected content.

        Assertions:
            - The response status code should be 200.
            - The request path should be '/chores'.
            - The response data should contain 'Chore Name'.
            - The response data should contain 'Description'.
            - The response data should contain 'Add Chore'.
        """
        response = self.client.get(
            '/chores',
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.path, '/chores')
        self.assertIn(b'Chore Name', response.data)
        self.assertIn(b'Description', response.data)
        self.assertIn(b'Add Chore', response.data)

    def test_add_chore_post(self) -> None:
        """
        Test the POST request to add a new chore.

        This test verifies that a new chore can be successfully added via a POST
        request and that the chore's details are correctly stored.

        Assertions:
        - The request path after the POST request should be '/'.
        - The name of the newly added chore should be 'Test Chore'.
        - The description of the newly added chore should be 'Test Description'.
        """
        response = self.client.post(
            '/chores',
            data={'name': 'Test Chore', 'description': 'Test Description'},
            follow_redirects=True
        )
        self.assertEqual(response.request.path, '/')
        new_chore = self.app.chore_service.get_all_chores()[-1]
        self.assertEqual(new_chore.name, 'Test Chore')
        self.assertEqual(new_chore.description, 'Test Description')

    def test_complete_chore(self) -> None:
        """
        Test the completion of a chore.
        This test verifies that a chore can be marked as complete and that the 
        appropriate confirmation message is displayed.

        Assertions:
            - The response path should match the expected chore detail path.
            - The response should contain the chore description.
            - The response should contain the confirmation message for marking
              the chore as complete.
        """
        chore = self.app.chore_service.get_all_chores()[1]
        chore.person_id = 1
        self.app.chore_service.update_chore(chore)

        response = self.client.post(
            f'/chore/{chore.id}/complete',
            follow_redirects=True
        )
        self.assertEqual(response.request.path, f'/chores/{chore.id}')
        self.assertIn(b'Take out the trash', response.data)
        self.assertIn(
            b'Are you sure you want to mark this chore as complete?',
            response.data
        )

    def test_complete_chore_invalid_id(self) -> None:
        """
        Test completing a chore with an invalid ID.

        This test sends a POST request to complete a chore with an ID that does
        not exist and verifies that the response status code is 404 and the
        response data contains the message 'Chore not found'.

        Assertions:
            - The response status code should be 404.
            - The response data should contain the message 'Chore not found'.
        """
        response = self.client.post(
            '/chore/1000/complete',
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'Chore not found', response.data)

    def test_delete_chore(self) -> None:
        """
        Test the deletion of a chore.

        This test sends a POST request to delete a chore with a specific ID and 
        checks if the response redirects to the home page and the chore is no 
        longer present in the response data.

        Assertions:
            - The response path should be '/'.
            - The chore 'Wash the dishes' should not be present in the response
              data.
        """
        response = self.client.post(
            f'/delete_chore/{1}',
            follow_redirects=True
        )
        self.assertEqual(response.request.path, '/')
        self.assertNotIn(b'Wash the dishes', response.data)

    def test_delete_chore_invalid_id(self) -> None:
        """
        Test the deletion of a chore with an invalid ID.

        This test ensures that attempting to delete a chore with a non-existent
        ID returns a 404 status code and an appropriate error message.

        Assertions:
            - The response status code should be 404.
            - The response data should contain the message 'Chore not found'.
        """
        response = self.client.post(
            f'/delete_chore/{1000}',
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'Chore not found', response.data)

    def test_edit_chore_get(self) -> None:
        """
        Test the GET request to edit a chore.
        This test checks if the edit chore page is correctly rendered with the
        expected data.

        Assertions:
        - The request path matches the expected edit URL.
        - The response contains the expected chore name.
        - The response contains the placeholder for selecting a person.
        """
        chore = self.app.chore_service.get_chore_by_id(1)
        response = self.client.get(
            f'/chores/{chore.id}/edit',
            data={'name': 'Test Chore', 'description': 'Test Description'},
        )

        self.assertEqual(response.request.path, f'/chores/{chore.id}/edit')
        self.assertIn(b'value="Wash the dishes"', response.data)
        self.assertIn(b'-- Select a person --', response.data)

    def test_edit_chore_get_invalid_id(self) -> None:
        """
        Test the GET request to edit a chore with an invalid ID.

        Assertions:
            - The response status code should be 404.
            - The response data should contain the message 'Chore not found'.
        """
        response = self.client.get(
            '/chores/1000/edit',
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'Chore not found', response.data)

    def test_edit_chore_post(self) -> None:
        """
        Test the POST request to edit a chore.
        This test verifies that the chore is correctly updated and the response
        contains the updated chore details.

        Assertions:
            - The response path should match the expected chore detail path.
            - The response data should contain the updated chore name.
            - The response data should contain the updated chore description.
        """
        chore = self.app.chore_service.get_chore_by_id(1)
        response = self.client.post(
            f'/chores/{chore.id}/edit',
            data={
                'name': 'Test Chore',
                'description': 'Test Description',
                'assigned_to': None
            },
            follow_redirects=True
        )

        self.assertEqual(response.request.path, f'/chores/{chore.id}')
        self.assertIn(b'Test Chore', response.data)
        self.assertIn(b'Test Description', response.data)

    def test_get_chore(self) -> None:
        """
        Test case for retrieving a specific chore by its ID.

        This test verifies that the GET request to the endpoint for a specific
        chore returns the correct status code and expected content in the
        response.

        Assertions:
            - The response status code is 200.
            - The response data contains the string 'Wash the dishes'.
            - The response data contains the string 'Assigned to:'.
        """
        chore = self.app.chore_service.get_chore_by_id(1)
        response = self.client.get(f'/chores/{chore.id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Wash the dishes', response.data)
        self.assertIn(b'Assigned to:', response.data)

    def test_get_chore_invalid_id(self) -> None:
        """
        Test the GET /chores/<id> endpoint with an invalid chore ID.

        This test ensures that requesting a chore with a non-existent ID returns
        a 404 status code and an appropriate error message.

        Assertions:
            - The response status code should be 404.
            - The response data should contain the message 'Chore not found'.
        """
        response = self.client.get('/chores/1000')
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'Chore not found', response.data)
