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

        This test simulates a client sending a POST request to the '/add_person'
        endpoint with the necessary data to add a new person. It verifies that
        the response status code is 200 (OK) and that the request path is
        redirected to the root path ('/').

        Test data:
        - first_name: 'John'
        - last_name: 'Smith'
        - birthday: '2000-01-01'
        - pin: '123456'
        - is_admin: False

        Assertions:
        - The response status code should be 200.
        - The request path should be '/'.
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
        Test the deletion of a person from the system.

        This test simulates a POST request to the '/delete_person' endpoint with
        a person_id of 1. It verifies that the response status code is 200, the
        number of people in the system is reduced to 2, the deleted person's
        name ('John Doe') is not present in the response data, and the request
        is redirected to the '/people' path.
        """
        response = self.client.post(
            '/delete_person', data={'person_id': 1}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(self.app.people_service.get_all_people()), 2)
        self.assertNotIn(b'John Doe', response.data)
        self.assertEqual(response.request.path, '/people')

    def test_edit_person_get(self):
        """
        Test the GET request to the '/people/1/edit' route.

        This test ensures that the GET request to the '/people/1/edit' route
        returns a status code of 200 and that the response data contains the
        expected information about the person with ID 1. Specifically, it checks
        for the presence of the first name 'John', the last name 'Doe', and
        birth date '2000-01-01' in the response data. Additionally, it verifies
        that the request path is '/people/1/edit'.

        Assertions:
            - The response status code is 200.
            - The response data contains the byte string 'John'.
            - The response data contains the byte string 'Doe'.
            - The response data contains the byte string '2000-01-01'.
            - The request path is '/people/1/edit'.
        """
        response = self.client.get('/people/1/edit', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'John', response.data)
        self.assertIn(b'Doe', response.data)
        self.assertIn(b'2000-01-01', response.data)
        self.assertEqual(response.request.path, '/people/1/edit')

    def test_edit_person_post(self):
        """
        Test the POST request to edit a person's details.

        This test simulates a POST request to the '/people/1/edit' endpoint with
        updated person details and verifies that the response status code is
        200. It then performs a GET request to the same endpoint to ensure that
        the changes have been successfully applied and the updated details are
        present in the response data.

        Assertions:
            - The response status code of the POST request is 200.
            - The updated person's name ('John Smith') is present in the
              response data of the subsequent GET request.
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

        This test checks if the response status code is 200 (OK) and verifies
        that the response data contains the expected content, specifically
        the name 'John Doe'.
        """
        response = self.client.get('/people/1/edit_pin')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Current PIN', response.data)
        self.assertIn(b'New PIN', response.data)
        self.assertIn(b'Confirm New PIN', response.data)

    def test_edit_pin_post(self):
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

    def test_get_people(self):
        """
        Test the GET /people route.

        This test verifies that the /people endpoint returns a 200 status code
        and that the response data contains the expected people names: 
        'John Doe', 'Jane Doe', and 'Mary Doe'.
        """
        response = self.client.get('/people')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'John Doe', response.data)
        self.assertIn(b'Jane Doe', response.data)
        self.assertIn(b'Mary Doe', response.data)

    def test_change_sequence(self):
        response = self.client.get('/change_sequence')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'John Doe', response.data)
        self.assertIn(b'Change Sequence', response.data)

    def test_update_sequence_post(self):
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


if __name__ == '__main__':
    unittest.main()
