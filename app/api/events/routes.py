from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_smorest import abort
from sqlalchemy.orm import joinedload
from app.models.category import EventCategoryModel
from app.models.event import EventModel
from app.models.status import EventStatusModel
from app.models.ticket import TicketTypeModel
from app.schemas.event import CreateEventSchema, EventSchema, UpdateEventStatusSchema
from app.extensions import db
from app.schemas.ticket import TicketTypeSchema
from app.utils.decorators import role_required
from . import events_blp


@events_blp.route("")
class EventsList(MethodView):
    @jwt_required()
    @events_blp.response(200, EventSchema(many=True))
    def get(self):
        return EventModel.query.options(
            joinedload(EventModel.category),
            joinedload(EventModel.status),
            joinedload(EventModel.organizer),
            joinedload(EventModel.tags),
            joinedload(EventModel.ticket_types),
        ).all()

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
        db.session.commit()

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

        return event

    @jwt_required()
    @role_required("organizer")
    @events_blp.response(204, None)
    def delete(self, event_id):
        event = EventModel.query.get_or_404(event_id)

        if event.status_id != 1:
            abort(400, message="Only draft events can be deleted.")

        db.session.delete(event)
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
        if not db.session.get(EventStatusModel, status_id):
            abort(404, message="Invalid status.")

        setattr(event, "status_id", status_id)

        db.session.commit()

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

        return ticket_type
