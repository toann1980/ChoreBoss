from choreboss.models.people import People
from sqlalchemy.orm import sessionmaker, joinedload
from sqlalchemy import func
import bcrypt
from typing import List, Optional


class PeopleRepository:
    def __init__(self, engine) -> None:
        """Initializes the PeopleRepository with a database engine.

        Args:
            engine: The SQLAlchemy engine to bind the session.
        """
        self.Session = sessionmaker(bind=engine)

    def add_person(
        self,
        first_name: str,
        last_name: str,
        birthday: str,
        pin: str,
        is_admin: bool
    ) -> People:
        """Adds a new person to the database.

        Args:
            first_name (str): The first name of the person.
            last_name (str): The last name of the person.
            birthday (str): The birthday of the person.
            pin (str): The PIN of the person.
            is_admin (bool): Whether the person is an admin.

        Returns:
            People: The added person object.
        """
        session = self.Session()
        person = People(
            first_name=first_name,
            last_name=last_name,
            birthday=birthday,
            pin=pin,
            is_admin=is_admin,
            sequence_num=self.get_next_sequence_num()
        )
        person.set_pin(pin)
        session.add(person)
        session.commit()
        session.close()
        return person

    def admins_exist(self) -> bool:
        """Checks if any admins exist in the database.

        Returns:
            bool: True if admins exist, False otherwise.
        """
        session = self.Session()
        admin_exists = session.query(People).filter_by(
            is_admin=True).first() is not None
        session.close()
        return admin_exists

    def delete_person(self, person_id: int) -> None:
        """Deletes a person from the database by their ID.

        Args:
            person_id (int): The ID of the person to delete.
        """
        session = self.Session()
        person = session.query(People).filter_by(id=person_id).first()
        if person:
            session.delete(person)
            session.commit()
        session.close()

    def get_all_people(self) -> List[People]:
        """Gets all people from the database.

        Returns:
            List[People]: A list of all people.
        """
        session = self.Session()
        people = session.query(People).options(
            joinedload(People.chore_person_id_back_populate),
            joinedload(People.last_completed_id_back_populate)
        ).all()
        session.close()
        return people

    def get_all_people_in_sequence_order(self) -> List[People]:
        """Gets all people in sequence order.

        Returns:
            List[People]: A list of all people in sequence order.
        """
        session = self.Session()
        people = session.query(People).order_by(People.sequence_num).all()
        session.close()
        return people

    def get_next_person_by_person_id(self, current_person_id: int) -> People:
        """Gets the next person by the current person's ID.

        Args:
            current_person_id (int): The ID of the current person.

        Returns:
            People: The next People object.
        """
        session = self.Session()
        current_person = session.query(People).filter_by(
            id=current_person_id
        ).first()
        next_person = session.query(People).filter(
            People.sequence_num > current_person.sequence_num
        ).order_by(People.sequence_num).first()
        if not next_person:
            next_person = session.query(People).order_by(
                People.sequence_num
            ).first()
        session.close()
        return next_person

    def get_next_sequence_num(self) -> int:
        """Gets the next sequence number.

        Returns:
            int: The next sequence number.
        """
        session = self.Session()
        max_sequence_num = None
        try:
            max_sequence_num = session.query(
                func.max(People.sequence_num)).scalar()
        finally:
            session.close()

        return 1 if max_sequence_num is None else max_sequence_num + 1

    def get_person_by_id(self, person_id: int) -> Optional[People]:
        """Gets a person by their ID.

        Args:
            person_id (int): The ID of the person.

        Returns:
            Optional[People]: The person object or None if not found.
        """
        session = self.Session()
        person = session.query(People).options(
            joinedload(People.chore_person_id_back_populate),
            joinedload(People.last_completed_id_back_populate)
        ).filter(People.id == person_id).first()
        session.close()
        return person

    def get_person_by_pin(self, pin: str) -> Optional[People]:
        """Gets a person by their PIN.

        Args:
            pin (str): The PIN of the person.

        Returns:
            Optional[People]: The person object or None if not found.
        """
        session = self.Session()
        people = session.query(People).all()
        session.close()
        for person in people:
            if bcrypt.checkpw(pin.encode('utf-8'), person.pin.encode('utf-8')):
                return person
        return None

    def is_admin(self, pin: str) -> bool:
        """Checks if a person is an admin by their PIN.

        Args:
            pin (str): The PIN of the person.

        Returns:
            bool: True if the person is an admin, False otherwise.
        """
        session = self.Session()
        try:
            admin = session.query(People).filter_by(is_admin=True).all()
            for person in admin:
                if person.verify_pin(pin):
                    return True
        finally:
            session.close()
        return False

    def update_person(self, person: People) -> People:
        """Updates a person's data.

        Args:
            person (People): The person object to update.

        Returns:
            People: The updated person object.
        """
        session = self.Session()
        session.add(person)
        session.commit()
        session.close()
        return person

    def update_pin(self, person_id: int, new_pin: str) -> None:
        """Updates a person's PIN.

        Args:
            person_id (int): The ID of the person.
            new_pin (str): The new PIN of the person.
        """
        person = self.get_person_by_id(person_id)
        if person:
            person.set_pin(new_pin)
            self.update_person(person)

    def update_sequence(self, person_id: int, new_sequence: int) -> None:
        """Updates a person's sequence number.

        Args:
            person_id (int): The ID of the person.
            new_sequence (int): The new sequence number.
        """
        session = self.Session()
        person = session.query(People).filter_by(id=person_id).first()
        if person:
            person.sequence_num = new_sequence
            session.commit()
        session.close()

    def verify_pin(self, person_id: int, pin: str) -> bool:
        """Verifies a person's PIN.

        Args:
            person_id (int): The ID of the person.
            pin (str): The PIN to verify.

        Returns:
            bool: True if the PIN is correct, False otherwise.
        """
        session = self.Session()
        try:
            person = session.query(People).filter_by(id=person_id).first()
            if person and person.verify_pin(pin):
                return True
        finally:
            session.close()
        return False
