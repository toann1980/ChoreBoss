from choreboss.models.sequence import Sequence
from sqlalchemy.orm import sessionmaker


class SequenceRepository:
    def __init__(self, engine):
        self.Session = sessionmaker(bind=engine)

    def add_sequence(self, person_id, sequence):
        session = self.Session()
        sequence = Sequence(person_id=person_id, sequence=sequence)
        session.add(sequence)
        session.commit()
        session.close()
        return sequence

    def get_all_sequences(self):
        session = self.Session()
        sequences = session.query(Sequence).all()
        session.close()
        return sequences

    def get_sequence_by_person_id(self, person_id):
        session = self.Session()
        sequence = session.query(Sequence).filter_by(
            person_id=person_id).first()
        session.close()
        return sequence

    def update_sequence(self, person_id, new_sequence):
        session = self.Session()
        sequence = session.query(Sequence).filter_by(
            person_id=person_id).first()
        if sequence:
            sequence.sequence = new_sequence
        else:
            sequence = Sequence(person_id=person_id, sequence=new_sequence)
            session.add(sequence)
        session.commit()
        session.close()
        return sequence
