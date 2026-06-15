from flask import request
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_smorest import abort
from sqlalchemy.orm import joinedload
from app.models.category import EventCategoryModel
from app.models.event import EventModel, EventStatusHistoryModel, EventTagModel
from app.models.status import EventStatusModel
from app.models.tag import TagModel
from app.models.ticket import TicketTypeModel
from app.schemas.event import (
    AddTagToEventSchema,
    CreateEventSchema,
    EventListQuerySchema,
    EventListSchema,
    EventSchema,
    UpdateEventStatusSchema,
)
from app.extensions import db
from app.schemas.ticket import TicketTypeSchema
from app.tasks.order import cancel_pending_orders_for_event
from app.utils.cache import get_cached, invalidate_pattern, make_cache_key, set_cached
from app.utils.decorators import role_required
from app.utils.files import validate_image_files
from app.utils.query_builder import QueryBuilder
from app.utils.s3 import extract_s3_key, remove_file_from_s3, upload_file_to_s3
from . import events_blp


@events_blp.route("")
class EventsList(MethodView):
    @jwt_required()
    @events_blp.arguments(EventListQuerySchema, location="query")
    @events_blp.response(200, EventListSchema)
    def get(self, validated_params):
        page, per_page = (validated_params["page"], validated_params["per_page"])
        cache_key = make_cache_key(validated_params)

        cached = get_cached(cache_key)
        if cached:
            return cached

        query = (
            QueryBuilder(
                EventModel.query.options(
                    joinedload(EventModel.category),
                    joinedload(EventModel.status),
                    joinedload(EventModel.organizer),
                    joinedload(EventModel.tags),
                    joinedload(EventModel.ticket_types),
                )
            )
            .filter_if(
                validated_params["search"],
                lambda: EventModel.title.ilike(f"%{validated_params['search']}%"),
            )
            .filter_if(
                validated_params["category_id"],
                lambda: EventModel.category_id == validated_params["category_id"],
            )
            .filter_if(
                validated_params["status_id"],
                lambda: EventModel.status_id == validated_params["status_id"],
            )
            .filter_if(
                validated_params["starts_after"],
                lambda: EventModel.starts_at >= validated_params["starts_after"],
            )
            .filter_if(
                validated_params["starts_before"],
                lambda: EventModel.starts_at <= validated_params["starts_before"],
            )
            .sort(
                EventModel, validated_params["sort_by"], validated_params["sort_order"]
            )
            .build()
        )

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        data = {
            "items": EventSchema(many=True).dump(pagination.items),
            "total": pagination.total,
            "pages": pagination.pages,
            "page": pagination.page,
            "per_page": pagination.per_page,
        }

        set_cached(cache_key, data)
        return pagination

    @jwt_required()
    @role_required("organizer")
    @events_blp.arguments(CreateEventSchema)
    @events_blp.response(201, EventSchema)
    def post(self, validated_data):
        user_id = get_jwt_identity()

        if not db.session.get(EventCategoryModel, validated_data["category_id"]):
            abort(404, message="Invalid category.")

        data = {**validated_data, "organizer_id": user_id}

        event = EventModel(**data)
        db.session.add(event)
        db.session.flush()

        history_record = EventStatusHistoryModel(
            event_id=event.id, status_id=event.status_id, changed_by_id=user_id
        )
        db.session.add(history_record)

        db.session.commit()
        invalidate_pattern("events:*")

        return event


@events_blp.route("/<int:event_id>")
class Event(MethodView):
    @jwt_required()
    @events_blp.response(200, EventSchema)
    def get(self, event_id):
        return EventModel.query.get_or_404(event_id)

    @jwt_required()
    @role_required("organizer")
    @events_blp.arguments(CreateEventSchema(partial=True))
    @events_blp.response(200, EventSchema)
    def patch(self, validated_data, event_id):
        event = EventModel.query.get_or_404(event_id)

        if str(event.organizer.id) != get_jwt_identity():
            abort(403, "Forbidden.")

        category_id = validated_data.get("category_id")
        if category_id and not db.session.get(EventCategoryModel, category_id):
            abort(404, message="Invalid category.")

        for key, value in validated_data.items():
            setattr(event, key, value)

        db.session.commit()
        invalidate_pattern("events:*")

        return event

    @jwt_required()
    @role_required("organizer")
    @events_blp.response(204, None)
    def delete(self, event_id):
        event = EventModel.query.get_or_404(event_id)

        if event.status_id != 1:
            abort(400, message="Only draft events can be deleted.")

        db.session.delete(event)
        invalidate_pattern("events:*")
        db.session.commit()


@events_blp.route("/<int:event_id>/status")
class EventStatus(MethodView):
    @jwt_required()
    @role_required("organizer")
    @events_blp.arguments(UpdateEventStatusSchema)
    @events_blp.response(200, EventSchema)
    def patch(self, validated_data, event_id):
        event = EventModel.query.get_or_404(event_id)

        if str(event.organizer.id) != get_jwt_identity():
            abort(403, "Forbidden.")

        if event.status.is_terminal:
            abort(400, message="Status can't be changed.")

        status_id = validated_data["status_id"]
        new_event_status = EventStatusModel.query.get_or_404(status_id)

        setattr(event, "status_id", status_id)

        history_record = EventStatusHistoryModel(
            event_id=event_id, status_id=status_id, changed_by_id=get_jwt_identity()
        )
        db.session.add(history_record)

        if new_event_status.name in ("cancelled", "completed"):
            cancel_pending_orders_for_event.delay(event_id)

        db.session.commit()
        invalidate_pattern("events:*")

        return event


@events_blp.route("/<int:event_id>/ticket-types")
class EventTicketTypes(MethodView):
    @jwt_required()
    @events_blp.response(200, TicketTypeSchema(many=True))
    def get(self, event_id):
        event = EventModel.query.get_or_404(event_id)

        return event.ticket_types

    @jwt_required()
    @role_required("organizer")
    @events_blp.arguments(TicketTypeSchema)
    @events_blp.response(201, TicketTypeSchema)
    def post(self, validated_data, event_id):
        event = EventModel.query.get_or_404(event_id)

        if str(event.organizer.id) != get_jwt_identity():
            abort(403, "Forbidden.")

        quantity = validated_data["quantity"]
        total_quantity = quantity + sum([t.quantity for t in event.ticket_types])

        if total_quantity > event.capacity:
            abort(400, message="Provided quantity exceeds event's capacity.")

        ticket_type = TicketTypeModel(**validated_data, event_id=event_id)

        db.session.add(ticket_type)
        db.session.commit()
        invalidate_pattern("events:*")

        return ticket_type


@events_blp.route("/<int:event_id>/tags")
class AddEventTag(MethodView):
    @jwt_required()
    @role_required("organizer")
    @events_blp.arguments(AddTagToEventSchema)
    @events_blp.response(201, EventSchema)
    def post(self, validated_data, event_id):
        event = db.session.get(EventModel, event_id)
        if not event:
            abort(404, message="Invalid event.")

        if str(event.organizer_id) != get_jwt_identity():
            abort(403, message="Forbidden.")

        tag_id = validated_data["tag_id"]

        if tag_id in [t.id for t in event.tags]:
            abort(400, message="Tag already assigned.")

        event_tag = EventTagModel(event_id=event_id, tag_id=tag_id)

        db.session.add(event_tag)
        db.session.commit()

        return event


@events_blp.route("/<int:event_id>/tags/<int:tag_id>")
class RemoveEventTag(MethodView):
    @jwt_required()
    @role_required("organizer")
    @events_blp.response(204)
    def delete(self, event_id, tag_id):
        event = db.session.get(EventModel, event_id)
        if not event:
            abort(404, message="Invalid event.")

        if not db.session.get(TagModel, tag_id):
            abort(404, message="Invalid tag.")

        if str(event.organizer_id) != get_jwt_identity():
            abort(403, message="Forbidden.")

        event_tag = EventTagModel.query.filter_by(
            event_id=event_id, tag_id=tag_id
        ).first()

        if not event_tag:
            abort(400, message="Tag wasn't assigned to event.")

        db.session.delete(event_tag)
        db.session.commit()


@events_blp.route("/<int:event_id>/banner")
class UploadEventBanner(MethodView):
    @jwt_required()
    @role_required("organizer")
    @events_blp.response(201, EventSchema)
    def post(self, event_id):
        event = EventModel.query.get_or_404(event_id)

        if str(event.organizer_id) != get_jwt_identity():
            abort(403, message="Forbidden.")

        file = request.files["banner"]

        if not file:
            abort(400, message="File was not provided.")

        if not validate_image_files(file):
            abort(400, message="Only image files are accepted.")

        banner_url = upload_file_to_s3(file, folder="banners")

        event.banner_url = banner_url

        db.session.commit()

        return event

    @jwt_required()
    @role_required("organizer")
    @events_blp.response(200, EventSchema)
    def delete(self, event_id):
        event = EventModel.query.get_or_404(event_id)

        if str(event.organizer_id) != get_jwt_identity():
            abort(403, message="Forbidden.")

        banner_url = event.banner_url

        if not banner_url:
            abort(400, message="Banner is not set.")

        remove_file_from_s3(extract_s3_key(banner_url))

        event.banner_url = None

        db.session.commit()

        return event
