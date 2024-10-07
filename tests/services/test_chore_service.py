from datetime import datetime
import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from choreboss.repositories.people_repository import PeopleRepository
from choreboss.repositories.chore_repository import ChoreRepository
from choreboss.models import Base
from choreboss.models.chore import Chore
from choreboss.models.people import People
from choreboss.services.people_service import PeopleService
from choreboss.services.chore_service import ChoreService


class TestChoreService(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        self.people_repository = PeopleRepository(self.engine)
        self.people_service = PeopleService(self.people_repository)
        self.chore_repository = ChoreRepository(self.engine)

        self.chore_service = ChoreService(
            self.chore_repository, self.people_repository)
        for chore in [
            {
                'name': 'Wash the dishes',
                'description': 'Wash the dishes',
            },
            {
                'name': 'Take out the trash',
                'description': 'Take out the trash',
            },
            {
                'name': 'Vacuum the floor',
                'description': 'Vacuum the floor',
            }
        ]:
            self.chore_service.add_chore(**chore)

        self.session.commit()

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

    def tearDown(self):
        self.session.close()
        Base.metadata.drop_all(self.engine)

    def test_add_chore(self):
        self.session = self.Session()
        self.chore_service.add_chore(
            name='Clean the bathroom',
            description='Clean the bathroom',
        )
        chore_count = len(self.chore_service.get_all_chores())
        self.assertEqual(chore_count, 4)

    def test_complete_chore(self):
        chore = self.chore_service.get_chore_by_id(1)
        chore.person_id = 1
        self.chore_service.update_chore(chore)
        self.chore_service.complete_chore(chore)
        completed_chore = self.chore_service.get_chore_by_id(1)
        self.assertEqual(completed_chore.last_completed_id, 1)
        self.assertEqual(completed_chore.person_id, 2)
        self.assertEqual(
            completed_chore.last_completed_date.date(),
            datetime.now().date()
        )

    def test_delete_chore(self):
        self.chore_service.delete_chore(1)
        self.session.commit()
        self.assertEqual(len(self.chore_service.get_all_chores()), 2)

    def test_get_all_chores(self):
        self.assertEqual(len(self.chore_service.get_all_chores()), 3)

        self.chore_service.add_chore(
            name='Clean the bathroom',
            description='Clean the bathroom',
        )
        self.session.commit()

        self.assertEqual(len(self.chore_service.get_all_chores()), 4)

    def test_get_chore_by_id(self):
        chore = self.chore_service.get_chore_by_id(1)
        self.assertEqual(chore.name, 'Wash the dishes')
        self.assertEqual(chore.description, 'Wash the dishes')

    def test_update_chore(self):
        chore = self.chore_service.get_chore_by_id(1)
        chore.name = 'Wash the dishes and the sink'
        chore.description = 'Wash the dishes and the sink'
        self.chore_service.update_chore(chore)
        updated_chore = self.chore_service.get_chore_by_id(1)
        self.assertEqual(updated_chore.name, 'Wash the dishes and the sink')
        self.assertEqual(
            updated_chore.description, 'Wash the dishes and the sink'
        )
