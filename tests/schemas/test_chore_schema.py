from datetime import datetime
import unittest
from marshmallow import ValidationError
from choreboss.schemas.chore_schema import ChoreSchema


class TestChoreSchema(unittest.TestCase):

    def setUp(self):
        self.schema = ChoreSchema()

    def test_valid_data(self):
        time = datetime.now()
        valid_data = {
            'name': 'Wash the dishes',
            'description': 'Clean all the dishes after dinner',
            'person_id': 2,
            'last_completed_date': time.isoformat(),
            'last_completed_id': 3
        }
        result = self.schema.load(valid_data)
        print(f'result: {result}')
        self.assertEqual(result['name'], valid_data['name'])
        self.assertEqual(result['description'], valid_data['description'])
        self.assertEqual(result['last_completed_date'], time)
        self.assertEqual(
            result['last_completed_id'],
            valid_data['last_completed_id']
        )

    def test_invalid_data(self):
        with self.assertRaises(ValidationError):
            self.schema.load({
                'id': 1,
            })

        with self.assertRaises(ValidationError):
            self.schema.load({
                'name': '',
            })

        with self.assertRaises(ValidationError):
            self.schema.load({
                'description': 'Clean all the dishes after dinner',
            })

        with self.assertRaises(ValidationError):
            self.schema.load({
                'id': 1,
                'name': 'Wash the dishes',
                'description': 'Clean all the dishes after dinner',
            })

        with self.assertRaises(ValidationError):
            self.schema.load({
                'id': 1,
                'description': 'Clean all the dishes after dinner',
                'person_id': '2',
            })

        with self.assertRaises(ValidationError):
            self.schema.load({
                'id': 1,
                'name': 'Wash the dishes',
                'description': 'Clean all the dishes after dinner',
                'person_id': 2,
                'last_completed_date': 'invalid-date',
            })

        with self.assertRaises(ValidationError):
            self.schema.load({
                'id': 1,
                'name': 'Wash the dishes',
                'description': 'Clean all the dishes after dinner',
                'person_id': 2,
                'last_completed_date': datetime.now().date(),
                'last_completed_id': '3'
            })
