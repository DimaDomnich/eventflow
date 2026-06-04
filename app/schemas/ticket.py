from marshmallow import Schema, fields


class TicketTypeSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()
    price = fields.Decimal(as_string=True)
    quantity = fields.Int()
    sold_count = fields.Int(dump_only=True)


class TicketSchema(Schema):
    id = fields.Int(dump_only=True)
    qr_code = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    order_id = fields.Int(dump_only=True)
    status = fields.Nested(TicketTypeSchema, dump_only=True)
    ticket_type = fields.Nested(TicketTypeSchema, dump_only=True)
