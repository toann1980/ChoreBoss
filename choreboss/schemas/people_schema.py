from marshmallow import Schema, fields


class PeopleSchema(Schema):
    id = fields.Int(dump_only=True)
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    birthday = fields.Date(required=True)
    pin = fields.Str(required=True)
    is_admin = fields.Bool(required=True)
    chore_person_id_back_populate = fields.List(
        fields.Nested('ChoreSchema', exclude=('person',)))
