from datetime import datetime
from choreboss.services.people_service import PeopleService
from choreboss.services.chore_service import ChoreService


def setup_memory_records(
        people_service: PeopleService,
        chore_service: ChoreService = None
) -> None:
    if chore_service:
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
            chore_service.add_chore(**chore)

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
        people_service.add_person(**person)
