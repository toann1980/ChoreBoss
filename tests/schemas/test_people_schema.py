from datetime import datetime
import unittest
from marshmallow import ValidationError
from choreboss.schemas.people_schema import PeopleSchema


class TestPeopleSchema(unittest.TestCase):
    def setUp(self):
        self.schema = PeopleSchema()

    def test_valid_data(self):
        birthday = datetime.strptime('01-01-2000', '%m-%d-%Y').date()
        valid_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'birthday': birthday.isoformat(),
            'pin': '123456',
            'is_admin': True,
        }
        result = self.schema.load(valid_data)
        self.assertEqual(result['first_name'], valid_data['first_name'])
        self.assertEqual(result['last_name'], valid_data['last_name'])
        self.assertEqual(result['birthday'], birthday)
        self.assertEqual(result['pin'], valid_data['pin'])
        self.assertEqual(result['is_admin'], valid_data['is_admin'])

    def test_invalid_data_first_name(self):
        with self.assertRaises(ValidationError):
            self.schema.load({
                'first_name': True,
                'last_name': 'Doe',
                'birthday': datetime.strptime(
                    '01-01-2000', '%m-%d-%Y'
                ).date().isoformat(),
                'pin': '123456',
                'is_admin': True,
            })

    def test_invalid_data_last_name(self):
        with self.assertRaises(ValidationError):
            self.schema.load({
                'first_name': 'John',
                'last_name': False,
                'birthday': datetime.strptime(
                    '01-01-2000', '%m-%d-%Y'
                ).date().isoformat(),
                'pin': '123456',
                'is_admin': True,
            })

    def test_invalid_data_birthday(self):
        with self.assertRaises(ValidationError):
            self.schema.load({
                'first_name': 'John',
                'last_name': 'Doe',
                'birthday': '01-01-2000',
                'pin': '123456',
                'is_admin': True,
            })

    def test_invalid_data_pin(self):
        with self.assertRaises(ValidationError):
            self.schema.load({
                'first_name': 'John',
                'last_name': 'Doe',
                'birthday': datetime.strptime(
                    '01-01-2000', '%m-%d-%Y'
                ).date().isoformat(),
                'pin': 123456,
                'is_admin': True,
            })

    def test_invalid_data_is_admin(self):
        with self.assertRaises(ValidationError):
            self.schema.load({
                'first_name': 'John',
                'last_name': 'Doe',
                'birthday': datetime.strptime(
                    '01-01-2000', '%m-%d-%Y'
                ).date().isoformat(),
                'pin': '123456',
                'is_admin': 'apple',
            })
