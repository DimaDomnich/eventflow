from marshmallow import Schema, fields


class EventStatusSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()
