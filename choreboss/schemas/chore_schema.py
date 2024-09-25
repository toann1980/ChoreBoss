from marshmallow import Schema, fields


class ChoreSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str(required=True)
    person_id = fields.Int()
    person_id_relationship = fields.Nested('PeopleSchema', only=('id', 'name'))
    last_completed = fields.DateTime()  # New field
    last_completed_id = fields.Int()  # New field
    last_completed_id_person = \
        fields.Nested('PeopleSchema', only=('id', 'name'))
