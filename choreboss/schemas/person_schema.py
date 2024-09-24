from marshmallow import Schema, fields


class PersonSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    chores = fields.List(fields.Nested('ChoreSchema', exclude=('person',)))
