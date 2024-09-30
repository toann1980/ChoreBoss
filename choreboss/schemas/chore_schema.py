from marshmallow import Schema, fields


class ChoreSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str(required=True)
    person_id = fields.Int()
    person_id_relationship = fields.Nested(
        'PeopleSchema', only=('id', 'first_name')
    )
    last_completed_date = fields.DateTime()
    last_completed_id = fields.Int()
    last_completed_id_person = fields.Nested(
        'PeopleSchema', only=('id', 'first_name')
    )
