from marshmallow import Schema, fields


class OrganizerSchema(Schema):
    id = fields.Int(dump_only=True)
    full_name = fields.Str()
    email = fields.Str()
