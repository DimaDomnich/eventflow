from marshmallow import Schema, fields, validate

from app.schemas.shared.pagination import PaginationQuerySchema, PaginationSchema

from .tag import TagSchema
from .ticket import TicketTypeSchema
from .user import OrganizerSchema
from .status import EventStatusSchema
from .category import CategorySchema


class CreateEventSchema(Schema):
    title = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    description = fields.Str(required=True)
    location = fields.Str(required=True)
    starts_at = fields.DateTime(required=True)
    ends_at = fields.DateTime(required=True)
    capacity = fields.Int(required=True, validate=validate.Range(min=1))
    category_id = fields.Int(required=True)


class EventSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    description = fields.Str()
    location = fields.Str()
    starts_at = fields.DateTime()
    ends_at = fields.DateTime()
    capacity = fields.Int()
    banner_url = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    category = fields.Nested(CategorySchema, dump_only=True)
    status = fields.Nested(EventStatusSchema, dump_only=True)
    organizer = fields.Nested(OrganizerSchema, dump_only=True)
    tags = fields.List(fields.Nested(TagSchema), dump_only=True)
    ticket_types = fields.List(fields.Nested(TicketTypeSchema), dump_only=True)


class EventListSchema(PaginationSchema):
    items = fields.List(fields.Nested(EventSchema))


class EventListQuerySchema(PaginationQuerySchema):
    search = fields.Str(load_default=None)
    category_id = fields.Int(load_default=None)
    status_id = fields.Int(load_default=None)
    starts_after = fields.DateTime(load_default=None)
    starts_before = fields.DateTime(load_default=None)
    sort_by = fields.Str(
        load_default="created_at",
        validate=validate.OneOf(["created_at", "starts_at", "title"]),
    )
    sort_order = fields.Str(
        load_default="desc", validate=validate.OneOf(["asc", "desc"])
    )


class UpdateEventStatusSchema(Schema):
    status_id = fields.Int(required=True)


class AddTagToEventSchema(Schema):
    tag_id = fields.Int(required=True)
