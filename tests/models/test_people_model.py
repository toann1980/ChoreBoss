from datetime import datetime
import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from choreboss.models.people import People
from choreboss.models import Base


class TestPeopleSchema(unittest.TestCase):
    def setUp(self):
        self.model = People()
        self.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def test_valid_data(self):
        birthday = datetime.strptime('01-01-2000', '%m-%d-%Y').date()
        valid_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'login_name': 'john',
            'birthday': birthday,
            'pin': '123456',
            'is_admin': True,
            'sequence_num': 1
        }
        person = People(**valid_data)
        self.session.add(person)
        self.session.commit()
        result = self.session.query(People).filter_by(id=person.id).first()
        self.assertEqual(result.id, person.id)
        self.assertEqual(result.first_name, valid_data['first_name'])
        self.assertEqual(result.last_name, valid_data['last_name'])
        self.assertEqual(result.birthday, birthday)
        self.assertEqual(result.login_name, valid_data['login_name'])
        self.assertEqual(result.pin, valid_data['pin'])
        self.assertEqual(result.is_admin, valid_data['is_admin'])

    def tearDown(self):
        self.session.close()
        Base.metadata.drop_all(self.engine)

    def test_invalid_data_first_name(self):
        # Not a string
        with self.assertRaises(AttributeError):
            People(**{
                'first_name': True,
                'last_name': 'Doe',
                'birthday': datetime.strptime(
                    '01-01-2000', '%m-%d-%Y'
                ).date(),
                'pin': '123456',
                'is_admin': True,
            })
        # Too short
        with self.assertRaises(AttributeError):
            People(**{
                'first_name': 'A',
                'last_name': 'Doe',
                'birthday': datetime.strptime(
                    '01-01-2000', '%m-%d-%Y'
                ).date(),
                'pin': '123456',
                'is_admin': True,
            })
        # Too long
        with self.assertRaises(AttributeError):
            People(**{
                'first_name': 'A' * 51,
                'last_name': 'Doe',
                'birthday': datetime.strptime(
                    '01-01-2000', '%m-%d-%Y'
                ).date(),
                'pin': '123456',
                'is_admin': True,
            })

    def test_invalid_data_last_name(self):
        # Not a string
        with self.assertRaises(AttributeError):
            People(**{
                'first_name': 'John',
                'last_name': False,
                'birthday': datetime.strptime(
                    '01-01-2000', '%m-%d-%Y'
                ).date(),
                'pin': '123456',
                'is_admin': True,
            })
        # Too short
        with self.assertRaises(AttributeError):
            People(**{
                'first_name': 'John',
                'last_name': 'Z',
                'birthday': datetime.strptime(
                    '01-01-2000', '%m-%d-%Y'
                ).date(),
                'pin': '123456',
                'is_admin': True,
            })
        # Too long
        with self.assertRaises(AttributeError):
            People(**{
                'first_name': 'John',
                'last_name': 'Z' * 51,
                'birthday': datetime.strptime(
                    '01-01-2000', '%m-%d-%Y'
                ).date(),
                'pin': '123456',
                'is_admin': True,
            })

    def test_invalid_data_login_name(self):
        with self.assertRaises(AttributeError):
            People(**{
                'first_name': 'John',
                'last_name': 'Doe',
                'login_name': 'ab',
                'birthday': datetime.strptime(
                    '01-01-2000', '%m-%d-%Y'
                ).date(),
                'pin': '123456',
                'is_admin': True,
            })
        with self.assertRaises(AttributeError):
            People(**{
                'first_name': 'John',
                'last_name': 'Doe',
                'login_name': 'bad name',
                'birthday': datetime.strptime(
                    '01-01-2000', '%m-%d-%Y'
                ).date(),
                'pin': '123456',
                'is_admin': True,
            })

    def test_invalid_data_birthday(self):
        with self.assertRaises(AttributeError):
            People(**{
                'first_name': 'John',
                'last_name': 'Doe',
                'birthday': '01-01-2000',
                'pin': '123456',
                'is_admin': True,
            })

    def test_invalid_data_pin(self):
        with self.assertRaises(AttributeError):
            People(**{
                'first_name': 'John',
                'last_name': 'Doe',
                'birthday': datetime.strptime(
                    '01-01-2000', '%m-%d-%Y'
                ).date(),
                'pin': 123456,
                'is_admin': True,
            })
        with self.assertRaises(AttributeError):
            People(**{
                'first_name': 'John',
                'last_name': 'Doe',
                'birthday': datetime.strptime(
                    '01-01-2000', '%m-%d-%Y'
                ).date(),
                'pin': '456',
                'is_admin': True,
            })

    def test_invalid_sequence_num(self):
        with self.assertRaises(AttributeError):
            People(**{
                'first_name': 'John',
                'last_name': 'Doe',
                'birthday': datetime.strptime(
                    '01-01-2000', '%m-%d-%Y'
                ).date(),
                'pin': '123456',
                'is_admin': True,
                'sequence_num': 'apple'
            })

    def test_invalid_data_is_admin(self):
        with self.assertRaises(AttributeError):
            People(**{
                'first_name': 'John',
                'last_name': 'Doe',
                'birthday': datetime.strptime(
                    '01-01-2000', '%m-%d-%Y'
                ).date(),
                'pin': '123456',
                'is_admin': 'apple',
            })
