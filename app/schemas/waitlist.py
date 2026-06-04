from marshmallow import Schema, fields


class WaitlistSchema(Schema):
    id = fields.Int(dump_only=True)
    joined_at = fields.DateTime(dump_only=True)
    notified_at = fields.DateTime(dump_only=True)
    expired_at = fields.DateTime(dump_only=True)

    event_id = fields.Int(dump_only=True)
