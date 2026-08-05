from datetime import datetime
import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from choreboss.models.chore import Chore
from choreboss.models import Base


class TestChoreModel(unittest.TestCase):
    def setUp(self):
        self.model = Chore()
        self.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def test_valid_data(self):
        time = datetime.now()
        valid_data = {
            'name': 'Wash the dishes',
            'description': 'Clean all the dishes after dinner',
            'person_id': 2,
            'last_completed_date': time,
            'last_completed_id': 3
        }
        chore = Chore(**valid_data)
        self.session.add(chore)
        self.session.commit()
        result = self.session.query(Chore).filter_by(id=chore.id).first()
        self.assertEqual(result.name, valid_data['name'])
        self.assertEqual(result.description, valid_data['description'])
        self.assertEqual(result.last_completed_date, time)
        self.assertEqual(
            result.last_completed_id, valid_data['last_completed_id'])

    def test_invalid_data_id(self):
        with self.assertRaises(AttributeError):
            Chore(**{
                'id': '1',
                'name': 'Wash the dishes',
                'description': 'Clean all the dishes after dinner',
                'person_id': 2,
                'last_completed_date': datetime.now().date(),
                'last_completed_id': 3
            })

    def test_invalid_data_name(self):
        with self.assertRaises(AttributeError):
            Chore(**{
                'id': 1,
                'name': '1',
                'description': 'Clean all the dishes after dinner',
                'person_id': 2,
                'last_completed_date': datetime.now().date(),
                'last_completed_id': 3
            })

        with self.assertRaises(AttributeError):
            Chore(**{
                'id': 1,
                'name': 1,
                'description': 'Clean all the dishes after dinner',
                'person_id': 2,
                'last_completed_date': datetime.now().date(),
                'last_completed_id': 3
            })

    def test_invalid_data_description(self):
        with self.assertRaises(AttributeError):
            Chore(**{
                'id': 1,
                'name': 'Wash the dishes',
                'description': '',
                'person_id': 2,
                'last_completed_date': datetime.now().date(),
                'last_completed_id': 3
            })

        with self.assertRaises(AttributeError):
            Chore(**{
                'id': 1,
                'name': 'Wash the dishes',
                'description': 1,
                'person_id': 2,
                'last_completed_date': datetime.now().date(),
                'last_completed_id': 3
            })

    def test_invalid_data_person_id(self):
        with self.assertRaises(AttributeError):
            Chore(**{
                'id': 1,
                'name': 'Wash the dishes',
                'description': 'Clean all the dishes after dinner',
                'person_id': '2',
                'last_completed_date': datetime.now().date(),
                'last_completed_id': 3
            })

    def test_invalid_data_last_completed_date(self):
        with self.assertRaises(AttributeError):
            Chore(**{
                'id': 1,
                'name': 'Wash the dishes',
                'description': 'Clean all the dishes after dinner',
                'person_id': 2,
                'last_completed_date': '2000-01-01',
                'last_completed_id': 3
            })

    def test_invalid_data_last_completed_id(self):
        with self.assertRaises(AttributeError):
            Chore(**{
                'id': 1,
                'name': 'Wash the dishes',
                'description': 'Clean all the dishes after dinner',
                'person_id': 2,
                'last_completed_date': datetime.now(),
                'last_completed_id': '3'
            })
