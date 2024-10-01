from marshmallow import Schema, fields


class SequenceSchema(Schema):
    id = fields.Int(dump_only=True)
    person_id = fields.Int(required=True)
    sequence = fields.Int(required=True)
    person_id_foreign_key = \
        fields.Nested('PeopleSchema', only=('id', 'first_name', 'last_name'))
