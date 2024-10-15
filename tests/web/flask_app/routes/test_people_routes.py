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

    def tearDown(self):
        self.session.close()
        Base.metadata.drop_all(self.engine)

    def test_add_person_get(self):
        """
        Test the GET request to the '/add_person' route.

        This test ensures that the '/add_person' route is accessible and returns
        a status code of 200. It also verifies that the request path is
        correctly set to '/add_person'.

        Assertions:
            - The response status code should be 200.
            - The request path should be '/add_person'.
        """
        response = self.client.get('/add_person', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.path, '/add_person')

    def test_add_person_post(self):
        """
        Test the POST request to add a new person.

        This test verifies that a new person can be added successfully via the
        '/add_person' endpoint and that the application redirects to the home
        page.

        Assertions:
            - The response status code is 200.
            - The request path after redirection is '/'.
            - The total number of people in the service is 4.
        """
        with self.app.test_client() as client:
            response = client.post(
                '/add_person',
                data={
                    'first_name': 'John',
                    'last_name': 'Smith',
                    'birthday': '2000-01-01',
                    'pin': '123456',
                    'is_admin': False
                },
                follow_redirects=True
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.path, '/')
        self.assertEqual(len(self.app.people_service.get_all_people()), 4)

    def test_delete_person(self):
        """
        Test the deletion of a person from the people service.

        This test verifies that a person can be successfully deleted and that
        the application redirects to the correct path with the expected status
        code.

        Assertions:
        - The response status code is 200.
        - The number of people in the service is 2 after deletion.
        - The deleted person's name ('John Doe') is not in the response data.
        - The request path after deletion is '/people'.
        """
        response = self.client.post(
            '/delete_person', data={'person_id': 1}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(self.app.people_service.get_all_people()), 2)
        self.assertNotIn(b'John Doe', response.data)
        self.assertEqual(response.request.path, '/people')

    def test_edit_person_get(self):
        """
        Test the GET request to edit a person's details.

        Assertions:
        - The response status code should be 200.
        - The response data should contain the first name 'John'.
        - The response data should contain the last name 'Doe'.
        - The response data should contain the birth date '2000-01-01'.
        - The request path should be '/people/1/edit'.
        """
        response = self.client.get('/people/1/edit', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'John', response.data)
        self.assertIn(b'Doe', response.data)
        self.assertIn(b'2000-01-01', response.data)
        self.assertEqual(response.request.path, '/people/1/edit')

    def test_edit_person_get_invalid_id(self):
        """
        Test the GET request to edit a person with an invalid ID.

        Assertions:
        - The response status code should be 404.
        - The response data should contain the message 'Person not found'.
        """
        response = self.client.get('/people/99/edit', follow_redirects=True)
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'Person not found', response.data)

    def test_edit_person_post(self):
        """
        Test the POST request to edit a person's details.

        This test sends a POST request to the '/people/1/edit' endpoint with
        updated person details and verifies that the changes are correctly
        applied and reflected in the response and the database.

        Assertions:
        - The response status code is 200.
        - The response data contains the updated first name, last name, and
          birthday.
        - The person's first name, last name, birthday, and admin status are
          correctly updated in the database.
        """
        response = self.client.post(
            '/people/1/edit',
            data={
                'first_name': 'John',
                'last_name': 'Smith',
                'birthday': '2012-01-01',
                'is_admin': True
            },
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/people/1/edit')
        edited_person = self.app.people_service.get_person_by_id(1)
        self.assertIn(b'John', response.data)
        self.assertIn(b'Smith', response.data)
        self.assertIn(b'2012-01-01', response.data)
        self.assertEqual(edited_person.first_name, 'John')
        self.assertEqual(edited_person.last_name, 'Smith')
        self.assertEqual(
            edited_person.birthday,
            datetime.strptime('2012-01-01', '%Y-%m-%d').date()
        )
        self.assertEqual(edited_person.is_admin, True)

    def test_edit_pin_get(self):
        """
        Test the GET request to the '/people/1/edit_pin' route.

        This test checks if the response status code is 200 and verifies that
        the response data contains the expected text fields for editing a PIN.

        Assertions:
            - Response status code should be 200.
            - Response data should contain 'Current PIN'.
            - Response data should contain 'New PIN'.
            - Response data should contain 'Confirm New PIN'.
        """
        response = self.client.get('/people/1/edit_pin')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Current PIN', response.data)
        self.assertIn(b'New PIN', response.data)
        self.assertIn(b'Confirm New PIN', response.data)

    def test_edit_pin_get_invalid_id(self):
        """
        Test the GET request to edit a person's pin with an invalid ID.

        Assertions:
            - The response status code should be 404.
            - The response data should contain 'Person not found'.
        """
        response = self.client.get(
            '/people/99/edit_pin', follow_redirects=True
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'Person not found', response.data)

    def test_edit_pin_post(self):
        """
        Test the POST request to edit a person's PIN.
        This test verifies the following scenarios:
        1. Correct current PIN and matching new PINs.
        2. Incorrect current PIN.
        3. Mismatched new PINs.

        Assertions:
        - Response status code is 200 for correct PIN and matching new PINs.
        - Response data matches the expected response for correct PIN.
        - The person's PIN is updated correctly.
        - Response status code is 400 for incorrect current PIN.
        - Response contains error message for incorrect current PIN.
        - Response status code is 400 for mismatched new PINs.
        - Response contains error message for mismatched new PINs.
        """
        # Verify correct PIN
        response = self.client.post(
            '/people/1/edit_pin',
            data={
                'current_pin': '123456',
                'new_pin': '654321',
                'confirm_pin': '654321'
            },
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        expected_response = self.client.get('/people/1/edit')
        self.assertEqual(response.data, expected_response.data)
        edited_person = self.app.people_service.get_person_by_id(1)
        self.assertEqual(edited_person.verify_pin('123456'), False)
        self.assertEqual(edited_person.verify_pin('654321'), True)

        # Verify incorrect PIN
        response = self.client.post(
            '/people/1/edit_pin',
            data={
                'current_pin': '000000',
                'new_pin': '654321',
                'confirm_pin': '654321'
            },
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Current PIN is incorrect', response.data)

        # Verify mismatched new PIN
        response = self.client.post(
            '/people/1/edit_pin',
            data={
                'current_pin': '123456',
                'new_pin': '654321',
                'confirm_pin': '123456'
            },
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'New PINs do not match', response.data)

    def test_get_people(self):
        """
        Test the GET /people endpoint.

        This test checks if the endpoint returns a 200 status code and 
        includes specific people in the response data.

        Assertions:
            - The response status code is 200.
            - The response data contains 'John Doe'.
            - The response data contains 'Jane Doe'.
            - The response data contains 'Mary Doe'.
        """
        response = self.client.get('/people')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'John Doe', response.data)
        self.assertIn(b'Jane Doe', response.data)
        self.assertIn(b'Mary Doe', response.data)

    def test_change_sequence(self):
        """
        Test the change_sequence route.

        This test ensures that the /change_sequence endpoint is accessible and 
        returns the expected content.

        Assertions:
            - The response status code should be 200.
            - The response data should contain 'John Doe'.
            - The response data should contain 'Change Sequence'.
        """
        response = self.client.get('/change_sequence')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'John Doe', response.data)
        self.assertIn(b'Change Sequence', response.data)

    def test_update_sequence_post(self):
        """
        Test the POST request to update the sequence numbers of people.

        This test verifies that the sequence numbers of two people are correctly
        updated when a POST request is made to the '/update_sequence' endpoint
        with the appropriate data.

        Assertions:
        - Initial sequence numbers of person_one and person_two are 1 and 2,
          respectively.
        - The response status code is 200.
        - The response data contains the word 'success'.
        - The updated sequence numbers of person_one and person_two are 2 and 1,
          respectively.
        """
        person_one = self.app.people_service.get_person_by_id(1)
        person_two = self.app.people_service.get_person_by_id(2)
        self.assertEqual(person_one.sequence_num, 1)
        self.assertEqual(person_two.sequence_num, 2)
        response = self.client.post(
            '/update_sequence',
            json={
                'sequence_data': json.dumps([
                    {'id': 1, 'sequence': 2},
                    {'id': 2, 'sequence': 1}
                ])
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'success', response.data)
        person_one = self.app.people_service.get_person_by_id(1)
        person_two = self.app.people_service.get_person_by_id(2)
        self.assertEqual(person_one.sequence_num, 2)
        self.assertEqual(person_two.sequence_num, 1)

    def test_verify_pin(self):
        """
        Test the /verify_pin endpoint for various contexts and PINs.
        This test verifies the behavior of the /verify_pin endpoint under
        different contexts and PINs, ensuring that the correct status and
        response data are returned.

        Assertions:
            - Status code is 200 for all requests.
            - Response data contains 'success' or 'failure' based on the context
              and PIN provided.
        """
        # complete_chore is admin context
        chore_one = self.app.chore_service.get_chore_by_id(1)
        chore_one.person_id = 2
        self.app.chore_service.update_chore(chore_one)
        response = self.client.post(
            '/verify_pin',
            json={
                'context': 'complete_chore',
                'pin': '123456',
                'chore_id': 1
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'success', response.data)

        # complete_chore is not admin context
        response = self.client.post(
            '/verify_pin',
            json={
                'context': 'complete_chore',
                'pin': '654321',
                'chore_id': 1
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b'{"status":"failure"}\n')

        # complete_chore context wrong pin
        response = self.client.post(
            '/verify_pin',
            json={
                'context': 'complete_chore',
                'pin': '000000',
                'chore_id': 1
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b'{"status":"failure"}\n')

        # add_person as admin context
        response = self.client.post(
            '/verify_pin',
            json={
                'context': 'add_person',
                'pin': '123456'
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b'{"status":"success"}\n')

        # add_person not admin context
        response = self.client.post(
            '/verify_pin',
            json={
                'context': 'add_person',
                'pin': '654321'
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b'{"status":"failure"}\n')

        # edit_person as admin context
        response = self.client.post(
            '/verify_pin',
            json={
                'context': 'edit_person',
                'pin': '123456'
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b'{"status":"success"}\n')

        # edit_person is user context
        response = self.client.post(
            '/verify_pin',
            json={
                'context': 'edit_person',
                'pin': '654321'
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b'{"status":"success"}\n')

        # edit_person not admin not user context
        response = self.client.post(
            '/verify_pin',
            json={
                'context': 'edit_person',
                'pin': '000000'
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b'{"status":"failure"}\n')

        # change_sequence as admin context
        response = self.client.post(
            '/verify_pin',
            json={
                'context': 'change_sequence',
                'pin': '123456'
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b'{"status":"success"}\n')

        # change_sequence not admin context
        response = self.client.post(
            '/verify_pin',
            json={
                'context': 'change_sequence',
                'pin': '654321'
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b'{"status":"failure"}\n')

        # delete_chore as admin context
        response = self.client.post(
            '/verify_pin',
            json={
                'context': 'delete_chore',
                'pin': '123456'
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b'{"status":"success"}\n')

        # delete_chore not admin context
        response = self.client.post(
            '/verify_pin',
            json={
                'context': 'delete_chore',
                'pin': '654321'
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b'{"status":"failure"}\n')

        # edit_chore as admin context
        response = self.client.post(
            '/verify_pin',
            json={
                'context': 'edit_chore',
                'pin': '123456'
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b'{"status":"success"}\n')

        # edit_chore not admin context
        response = self.client.post(
            '/verify_pin',
            json={
                'context': 'edit_chore',
                'pin': '654321'
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b'{"status":"failure"}\n')
