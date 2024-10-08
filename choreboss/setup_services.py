from sqlalchemy.engine import Engine
from choreboss.repositories.people_repository import PeopleRepository
from choreboss.services.people_service import PeopleService
from choreboss.repositories.chore_repository import ChoreRepository
from choreboss.services.chore_service import ChoreService


def setup_services(engine: Engine) -> tuple[PeopleService, ChoreService]:
    people_repository = PeopleRepository(engine)
    people_service = PeopleService(people_repository)
    chore_repository = ChoreRepository(engine)
    chore_service = ChoreService(chore_repository, people_repository)
    return people_service, chore_service
