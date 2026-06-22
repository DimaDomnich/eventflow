from flask import request
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_smorest import abort
from sqlalchemy import func, select
from sqlalchemy.orm import joinedload
from app.models.category import EventCategoryModel
from app.models.event import (
    EventModel,
    EventStatusHistoryModel,
    EventTagModel,
    EventsRatingModel,
)
from app.models.order import OrderModel
from app.models.status import EventStatusModel, OrderStatusModel, TicketStatusModel
from app.models.tag import TagModel
from app.models.ticket import TicketModel, TicketTypeModel
from app.schemas.event import (
    AddTagToEventSchema,
    CreateEventSchema,
    EventListQuerySchema,
    EventListSchema,
    EventRatingDistributionSchema,
    EventRatingListSchema,
    EventRatingSchema,
    EventSchema,
    TopRatedEventsSchema,
    UpdateEventSchema,
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
            .search(validated_params["search"], EventModel)
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
    @events_blp.arguments(UpdateEventSchema(partial=True))
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


@events_blp.route("/<int:event_id>/rate")
class EventRating(MethodView):
    @jwt_required()
    @events_blp.response(200, EventRatingListSchema)
    def get(self, event_id):
        event_ratings = (
            db.session.execute(
                select(EventsRatingModel)
                .join(EventModel, onclause=EventModel.id == EventsRatingModel.event_id)
                .where(EventModel.id == event_id)
            )
            .scalars()
            .all()
        )

        avg, total = db.session.execute(
            select(
                func.avg(EventsRatingModel.score), func.count(EventsRatingModel.id)
            ).where(EventsRatingModel.event_id == event_id)
        ).first()

        return {
            "items": event_ratings,
            "avg": avg,
            "total": total,
        }

    @jwt_required()
    @role_required("attendee")
    @events_blp.arguments(EventRatingSchema)
    @events_blp.response(201, EventRatingSchema)
    def post(self, validated_data, event_id):
        event = db.session.get(EventModel, event_id)

        if not event:
            abort(404, message="Event not found.")

        completed_event_status = db.session.execute(
            select(EventStatusModel).where(EventStatusModel.name == "completed")
        ).scalar()

        if event.status_id != completed_event_status.id:
            abort(400, message="Event is not completed.")

        user_id = int(get_jwt_identity())

        if db.session.execute(
            select(EventsRatingModel).where(
                EventsRatingModel.event_id == event_id,
                EventsRatingModel.user_id == user_id,
            )
        ).scalar():
            abort(400, message="User already rated this event.")

        confirmed_order_status = db.session.execute(
            select(OrderStatusModel).where(OrderStatusModel.name == "confirmed")
        ).scalar()
        valid_ticket_statuses = (
            db.session.execute(
                select(TicketStatusModel).where(
                    TicketStatusModel.name.in_(["confirmed", "used"])
                )
            )
            .scalars()
            .all()
        )

        valid_ticket_status_ids = [
            valid_ticket_status.id for valid_ticket_status in valid_ticket_statuses
        ]

        # has_ticket = False

        # for order in user.orders:
        #     if order.status_id == confirmed_order_status.id:
        #         for ticket in order.tickets:
        #             if ticket.ticket_type.event_id == event_id and ticket.status_id in [
        #                 valid_ticket_status.id
        #                 for valid_ticket_status in valid_ticket_statuses
        #             ]:
        #                 has_ticket = True

        has_ticket = db.session.execute(
            select(TicketModel)
            .join(
                TicketTypeModel,
                onclause=TicketTypeModel.id == TicketModel.ticket_type_id,
            )
            .join(OrderModel, onclause=OrderModel.id == TicketModel.order_id)
            .where(
                TicketTypeModel.event_id == event_id,
                OrderModel.user_id == user_id,
                OrderModel.status_id == confirmed_order_status.id,
                TicketModel.status_id.in_(valid_ticket_status_ids),
            )
        ).scalar()

        if not has_ticket:
            abort(400, message="User doesn't have paid ticket for this event.")

        event_rate = EventsRatingModel(
            user_id=user_id, event_id=event_id, **validated_data
        )

        db.session.add(event_rate)
        db.session.commit()

        return event_rate


@events_blp.route("/<int:event_id>/rate/distribution")
class EventRatingDistribution(MethodView):
    @jwt_required()
    @events_blp.response(200, EventRatingDistributionSchema(many=True))
    def get(self, event_id):
        distribution = db.session.execute(
            select(EventsRatingModel.score, func.count(EventsRatingModel.id))
            .where(EventsRatingModel.event_id == event_id)
            .group_by(EventsRatingModel.score)
            .order_by(EventsRatingModel.score.desc())
        ).all()

        data = [{"score": score, "count": count} for score, count in distribution]

        return data


@events_blp.route("/top-rated")
class TopRatedEvents(MethodView):
    @jwt_required()
    @events_blp.response(200, TopRatedEventsSchema(many=True))
    def get(self):
        top_rated = db.session.execute(
            select(
                EventModel.id,
                EventModel.title,
                func.avg(EventsRatingModel.score).label("avg_score"),
                func.count(EventsRatingModel.id).label("total_ratings"),
            )
            .join(
                EventsRatingModel,
                onclause=EventModel.id == EventsRatingModel.event_id,
            )
            .group_by(
                EventModel.id,
                EventModel.title,
            )
            .having(func.count(EventsRatingModel.id) >= 1)
            .order_by(func.avg(EventsRatingModel.score).desc())
            .limit(10)
        ).all()

        data = [
            {"id": id, "title": title, "avg": avg, "total_ratings": total_ratings}
            for id, title, avg, total_ratings in top_rated
        ]

        return data
