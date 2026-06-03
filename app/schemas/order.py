from marshmallow import Schema, fields, validate

from app.schemas.status import OrderStatusSchema
from app.schemas.ticket import TicketSchema
from app.schemas.user import AttendeeSchema


class OrderSchema(Schema):
    id = fields.Int(dump_only=True)
    payment_intent_id = fields.Str(dump_only=True)
    total_amount = fields.Decimal(as_string=True)
    user = fields.Nested(AttendeeSchema, dump_only=True)
    status = fields.Nested(OrderStatusSchema, dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    tickets = fields.List(fields.Nested(TicketSchema), dump_only=True)


class CreateOrderTicketTypeSchema(Schema):
    ticket_type_id = fields.Int(required=True)
    count = fields.Int(required=True, validate=validate.Range(min=1))


class CreateOrderSchema(Schema):
    tickets = fields.List(
        fields.Nested(CreateOrderTicketTypeSchema),
        required=True,
        validate=validate.Length(min=1),
    )
