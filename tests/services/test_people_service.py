from datetime import datetime
import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from choreboss.repositories.people_repository import PeopleRepository
from choreboss.models import Base
from choreboss.models.chore import Chore
from choreboss.models.people import People
from choreboss.services.people_service import PeopleService


class TestPeopleService(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        self.people_repository = PeopleRepository(self.engine)
        self.people_service = PeopleService(self.people_repository)
        for person in [
            {
                'first_name': 'John',
                'last_name': 'Doe',
                'birthday': datetime.strptime('2000-01-01', '%Y-%m-%d').date(),
                'pin': '123456',
                'is_admin': True
            },
            {
                'first_name': 'Jane',
                'last_name': 'Doe',
                'birthday': datetime.strptime('2002-01-01', '%Y-%m-%d').date(),
                'pin': '654321',
                'is_admin': False
            },
            {
                'first_name': 'Mary',
                'last_name': 'Doe',
                'birthday': datetime.strptime('2004-01-01', '%Y-%m-%d').date(),
                'pin': '9876',
                'is_admin': False
            }
        ]:
            self.people_service.add_person(**person)

        self.session.commit()

    def tearDown(self):
        self.session.close()
        Base.metadata.drop_all(self.engine)

    def test_add_person(self):
        self.session = self.Session()
        self.people_service.add_person(
            first_name='Johnny',
            last_name='Doer',
            birthday=datetime.strptime('2002-01-01', '%Y-%m-%d').date(),
            pin='234567',
            is_admin=True
        )
        person_count = len(self.people_service.get_all_people())
        self.assertEqual(person_count, 4)

        new_person = self.people_repository.get_person_by_id(4)
        self.assertEqual(new_person.first_name, 'Johnny')
        self.assertEqual(new_person.last_name, 'Doer')
        self.assertEqual(
            new_person.birthday,
            datetime.strptime('2002-01-01', '%Y-%m-%d').date()
        )
        self.assertEqual(new_person.verify_pin('234567'), True)
        self.assertTrue(new_person.is_admin)
        self.assertTrue(new_person.sequence_num, 4)

    def test_add_person_with_missing_fields(self):
        with self.assertRaises(TypeError):
            self.people_service.add_person(
                # Missing first_name
                last_name="Doe",
                birthday=datetime.strptime('2000-01-01', '%Y-%m-%d').date(),
                pin="1234",
            )
        with self.assertRaises(TypeError):
            self.people_service.add_person(
                first_name="John",
                # Missing last_name
                birthday=datetime.strptime('2000-01-01', '%Y-%m-%d').date(),
                pin="1234",
            )

        with self.assertRaises(TypeError):
            self.people_service.add_person(
                first_name="John",
                last_name="Doe",
                # Missing birthday
                pin="1234",
            )

        with self.assertRaises(TypeError):
            self.people_service.add_person(
                first_name="John",
                last_name="Doe",
                birthday=datetime.strptime('2000-01-01', '%Y-%m-%d').date(),
                # Missing pin
            )

    def test_admins_exist(self):
        self.assertTrue(self.people_service.admins_exist())
        self.people_service.delete_person(1)
        self.assertFalse(self.people_service.admins_exist())

    def test_delete_person(self):
        self.people_service.delete_person(1)
        person_count = len(self.people_service.get_all_people())
        self.assertEqual(person_count, 2)

    def test_dete_person_and_adjust_sequence(self):
        self.people_service.delete_person_and_adjust_sequence(1)
        people = self.people_service.get_all_people()
        self.assertEqual(people[0].sequence_num, 1)
        self.assertEqual(people[1].sequence_num, 2)

    def test_get_all_people(self):
        people = self.people_service.get_all_people()
        self.assertEqual(len(people), 3)

    def test_get_next_person_by_person_id(self):
        next_person = self.people_service.get_next_person_by_person_id(1)
        self.assertEqual(next_person.first_name, 'Jane')

        next_person = self.people_service.get_next_person_by_person_id(2)
        self.assertEqual(next_person.first_name, 'Mary')

        next_person = self.people_service.get_next_person_by_person_id(3)
        self.assertEqual(next_person.first_name, 'John')

        next_person = self.people_service.get_next_person_by_person_id(4)
        self.assertIsNone(next_person)

    def test_get_person_by_id(self):
        person = self.people_service.get_person_by_id(1)
        self.assertIsNotNone(person)
        self.assertEqual(person.first_name, 'John')
        self.assertEqual(person.last_name, 'Doe')
        self.assertEqual(
            person.birthday,
            datetime.strptime('2000-01-01', '%Y-%m-%d').date()
        )
        self.assertEqual(person.is_admin, True)
        self.assertEqual(person.sequence_num, 1)

        person = self.people_service.get_person_by_id(3)
        self.assertIsNotNone(person)
        self.assertEqual(person.first_name, 'Mary')
        self.assertEqual(person.last_name, 'Doe')
        self.assertEqual(
            person.birthday,
            datetime.strptime('2004-01-01', '%Y-%m-%d').date()
        )
        self.assertEqual(person.is_admin, False)
        self.assertEqual(person.sequence_num, 3)

    def test_get_person_by_pin(self):
        retrieved_person = self.people_service.get_person_by_pin('123456')
        self.assertIsNotNone(retrieved_person)
        self.assertEqual(retrieved_person.first_name, 'John')
        self.assertEqual(retrieved_person.last_name, 'Doe')
        self.assertEqual(
            retrieved_person.birthday,
            datetime.strptime('2000-01-01', '%Y-%m-%d').date()
        )
        self.assertEqual(retrieved_person.is_admin, True)

    def test_get_person_by_pin_is_none(self):
        retrieved_person = self.people_service.get_person_by_pin('9999')
        self.assertIsNone(retrieved_person)

    def test_is_admin(self):
        self.assertTrue(self.people_service.is_admin('123456'))
        self.assertFalse(self.people_service.is_admin('654321'))

    def test_update_person(self):
        person = self.people_service.get_person_by_id(1)
        person.first_name = 'Johnny'
        person.last_name = 'Doer'
        person.birthday = datetime.strptime('2002-01-01', '%Y-%m-%d').date()
        person.set_pin('234567')
        person.is_admin = False
        self.people_service.update_person(person)

        updated_person = self.people_service.get_person_by_id(1)
        self.assertEqual(updated_person.first_name, 'Johnny')
        self.assertEqual(updated_person.last_name, 'Doer')
        self.assertEqual(
            updated_person.birthday,
            datetime.strptime('2002-01-01', '%Y-%m-%d').date()
        )
        self.assertEqual(updated_person.verify_pin('234567'), True)
        self.assertFalse(updated_person.is_admin)

    def test_update_sequence(self):
        for sequence in (
            {'person_id': 1, 'new_sequence': 3},
            {'person_id': 2, 'new_sequence': 1},
            {'person_id': 3, 'new_sequence': 2},
        ):
            self.people_service.update_sequence(**sequence)

        for person in self.people_service.get_all_people():
            if person.id == 1:
                self.assertEqual(person.sequence_num, 3)
            elif person.id == 2:
                self.assertEqual(person.sequence_num, 1)
            elif person.id == 3:
                self.assertEqual(person.sequence_num, 2)

    def test_get_next_sequence_num(self):
        next_sequence_num = self.people_repository.get_next_sequence_num()
        self.assertEqual(next_sequence_num, 4)

        self.people_service.add_person(
            first_name='Johnny',
            last_name='Doer',
            birthday=datetime.strptime('2002-01-01', '%Y-%m-%d').date(),
            pin='234567',
            is_admin=True
        )
        next_sequence_num = self.people_repository.get_next_sequence_num()
        self.assertEqual(next_sequence_num, 5)
