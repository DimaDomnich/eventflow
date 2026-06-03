from marshmallow import Schema, fields


class TicketTypeSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()
    price = fields.Decimal(as_string=True)
    quantity = fields.Int()
    sold_count = fields.Int(dump_only=True)
