from marshmallow import Schema, fields


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    full_name = fields.Str()
    email = fields.Str()


class OrganizerSchema(UserSchema):
    pass


class AttendeeSchema(UserSchema):
    pass
