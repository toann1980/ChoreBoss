from choreboss.repositories.sequence_repository import SequenceRepository


class SequenceService:
    def __init__(self, sequence_repository: SequenceRepository):
        self.sequence_repository = sequence_repository

    def add_sequence(self, person_id, sequence):
        return self.sequence_repository.add_sequence(person_id, sequence)

    def get_all_sequences(self):
        return self.sequence_repository.get_all_sequences()

    def get_sequence_by_person_id(self, person_id):
        return self.sequence_repository.get_sequence_by_person_id(person_id)

    def update_sequence(self, person_id, new_sequence):
        return self.sequence_repository.update_sequence(person_id, new_sequence)
