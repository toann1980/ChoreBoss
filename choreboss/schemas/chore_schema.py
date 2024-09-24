from marshmallow import Schema, fields


class ChoreSchema(Schema):
    id = fields.Int(dump_only=True)
    description = fields.Str(required=True)
    person_id = fields.Int()
    person = fields.Nested('PersonSchema', only=('id', 'name'))
