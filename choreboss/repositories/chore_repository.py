from datetime import datetime
from sqlalchemy.orm import sessionmaker, joinedload
from sqlalchemy.engine import Engine
from choreboss.models.chore import Chore
from choreboss.models import Base


class ChoreRepository:
    def __init__(self, engine: Engine) -> None:
        """
        Initialize the ChoreRepository with a database engine.

        :param engine: SQLAlchemy engine instance.
        """
        self.Session = sessionmaker(bind=engine)

    def add_chore(self, name: str, description: str) -> None:
        """
        Add a new chore to the database.

        Args:
            name (str): Name of the chore.
            description (str): Description of the chore.
        """
        with self.Session() as session:
            chore = Chore(name=name, description=description)
            session.add(chore)
            session.commit()

    def complete_chore(self, chore: Chore) -> None:
        """
        Mark a chore as completed.

        Args:
            chore (Chore): The Chore object to mark as completed.
        """
        with self.Session() as session:
            existing_chore = session.query(
                Chore).filter_by(id=chore.id).first()
            if existing_chore:
                existing_chore.last_completed_id = chore.person_id
                existing_chore.last_completed_date = datetime.now()
                session.commit()

    def delete_chore(self, chore_id: int) -> None:
        """
        Delete a chore from the database.

        Args:
            chore_id (int): ID of the chore to delete.
        """
        with self.Session() as session:
            chore = session.query(Chore).filter_by(id=chore_id).first()
            if chore:
                session.delete(chore)
                session.commit()

    def get_all_chores(self) -> list[Chore]:
        """
        Retrieve all chores from the database.

        Returns:
            list[Chore]: A list of all Chore objects.
        """
        with self.Session() as session:
            chores = session.query(Chore).options(
                joinedload(Chore.person_id_foreign_key),
                joinedload(Chore.last_completed_id_foreign_key)
            ).all()
            return chores

    def get_chore_by_id(self, chore_id: int) -> Chore:
        """
        Retrieve a chore by its ID.

        Args:
            chore_id (int): ID of the chore to retrieve.

        Returns:
            Chore: The Chore object with the given ID.
        """
        with self.Session() as session:
            chore = session.query(Chore).options(
                joinedload(Chore.person_id_foreign_key),
                joinedload(Chore.last_completed_id_foreign_key)
            ).filter_by(id=chore_id).first()
            return chore

    def update_chore(self, chore: Chore) -> None:
        """
        Update an existing chore in the database.

        Args:
            chore (Chore): The Chore object with updated information.
        """
        with self.Session() as session:
            existing_chore = session.query(
                Chore).filter_by(id=chore.id).first()
            if existing_chore:
                existing_chore.name = chore.name
                existing_chore.description = chore.description
                existing_chore.person_id = chore.person_id
                session.commit()
