from marshmallow import Schema, fields


class PeopleSchema(Schema):
    id = fields.Int(dump_only=True)
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    age = fields.Int(required=True)
    chores = fields.List(fields.Nested('ChoreSchema', exclude=('person',)))
