from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import select

from app.models.status import TicketStatusModel
from app.models.ticket import TicketModel, TicketTypeModel
from app.schemas.ticket import TicketSchema
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

        status = TicketStatusModel.query.filter(
            TicketStatusModel.name == "cancelled"
        ).first_or_404()

        ticket.status_id = status.id

        stmt = (
            select(TicketTypeModel)
            .where(TicketTypeModel.id == ticket.ticket_type_id)
            .with_for_update()
        )

        ticket_type = db.session.execute(stmt).scalar()

        ticket_type.sold_count -= 1

        db.session.commit()

        return ticket
