from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import select

from app.models.status import TicketStatusModel
from app.models.ticket import (
    TicketCheckinsModel,
    TicketModel,
    TicketStatusHistoryModel,
    TicketTypeModel,
)
from app.schemas.ticket import TicketCheckinSchema, TicketSchema
from app.tasks.waitlist import notify_next_waitlist_person
from app.utils.decorators import role_required
from app.extensions import db
from flask_smorest import abort


from . import tickets_blp


@tickets_blp.route("/<int:ticket_id>/cancel")
class TicketsCancel(MethodView):
    @jwt_required()
    @role_required("attendee")
    @tickets_blp.response(200, TicketSchema)
    def patch(self, ticket_id):
        ticket = TicketModel.query.get_or_404(ticket_id)

        if str(ticket.order.user_id) != get_jwt_identity():
            abort(403, message="Forbidden.")

        if ticket.status.is_terminal:
            abort(400, message="Invalid action.")

        cancelled_status = TicketStatusModel.query.filter(
            TicketStatusModel.name == "cancelled"
        ).first_or_404()

        ticket.status_id = cancelled_status.id

        stmt = (
            select(TicketTypeModel)
            .where(TicketTypeModel.id == ticket.ticket_type_id)
            .with_for_update()
        )

        ticket_type = db.session.execute(stmt).scalar()

        ticket_type.sold_count -= 1

        history_record = TicketStatusHistoryModel(
            ticket_id=ticket_id,
            status_id=cancelled_status.id,
            changed_by_id=get_jwt_identity(),
        )
        db.session.add(history_record)

        db.session.commit()

        notify_next_waitlist_person.delay(ticket_type.event_id)

        return ticket


@tickets_blp.route("/<int:ticket_id>/payment")
class TicketPayment(MethodView):
    @jwt_required()
    @role_required("attendee")
    @tickets_blp.response(200, TicketSchema)
    def patch(self, ticket_id):
        ticket = TicketModel.query.get_or_404(ticket_id)

        if str(ticket.order.user_id) != get_jwt_identity():
            abort(403, message="Forbidden.")

        reserved_status = TicketStatusModel.query.filter(
            TicketStatusModel.name == "reserved"
        ).first()

        if reserved_status.id != ticket.status_id:
            abort(400, message="Invalid ticket for this operation.")

        confirmed_status = TicketStatusModel.query.filter(
            TicketStatusModel.name == "confirmed"
        ).first()

        ticket.status = confirmed_status

        history_record = TicketStatusHistoryModel(
            ticket_id=ticket_id,
            status_id=confirmed_status.id,
            changed_by_id=get_jwt_identity(),
        )
        db.session.add(history_record)

        db.session.commit()

        return ticket


@tickets_blp.route("/<int:ticket_id>/checkin")
class TicketsCheckin(MethodView):
    @jwt_required()
    @role_required("organizer")
    @tickets_blp.response(201, TicketCheckinSchema)
    def post(self, ticket_id):
        ticket = TicketModel.query.get_or_404(ticket_id)

        if str(ticket.ticket_type.event.organizer_id) != get_jwt_identity():
            abort(403, message="Forbidden.")

        if TicketCheckinsModel.query.filter(
            TicketCheckinsModel.ticket_id == ticket_id
        ).first():
            abort(400, message="Ticket has already been checked in.")

        confirmed_status = TicketStatusModel.query.filter(
            TicketStatusModel.name == "confirmed"
        ).first()

        if ticket.status_id != confirmed_status.id:
            abort(400, message="Invalid ticket status.")

        ticket_checkin = TicketCheckinsModel(
            ticket_id=ticket_id,
            checked_in_by_id=get_jwt_identity(),
        )

        used_status = TicketStatusModel.query.filter(
            TicketStatusModel.name == "used"
        ).first()

        ticket.status = used_status

        db.session.add(ticket_checkin)

        history_record = TicketStatusHistoryModel(
            ticket_id=ticket_id,
            status_id=used_status.id,
            changed_by_id=get_jwt_identity(),
        )
        db.session.add(history_record)

        db.session.commit()

        return ticket_checkin
