from decimal import Decimal

from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.order import OrderModel
from app.models.ticket import TicketModel, TicketTypeModel
from app.schemas.order import CreateOrderSchema, OrderSchema
from app.utils.decorators import role_required
from sqlalchemy.orm import joinedload
from app.extensions import db
from sqlalchemy import select
from flask_smorest import abort


from . import orders_blp


@orders_blp.route("")
class Orders(MethodView):
    @jwt_required()
    # @role_required("attendee")
    @orders_blp.response(200, OrderSchema(many=True))
    def get(self):
        return OrderModel.query.options(
            joinedload(OrderModel.user),
            joinedload(OrderModel.status),
            joinedload(OrderModel.tickets),
        ).all()

    @jwt_required()
    @role_required("attendee")
    @orders_blp.arguments(CreateOrderSchema)
    @orders_blp.response(201, OrderSchema)
    def post(self, validated_data):
        req_ticket_types = validated_data["tickets"]

        stmt = (
            select(TicketTypeModel)
            .where(
                TicketTypeModel.id.in_([t["ticket_type_id"] for t in req_ticket_types])
            )
            .with_for_update()
        )

        ticket_types = db.session.execute(stmt).scalars().all()

        if len(ticket_types) != len(
            req_ticket_types
        ):  # all or some of the ticket types are invalid
            abort(404, message="Ticket type(/s) are invalid.")

        req_map = {t["ticket_type_id"]: t for t in req_ticket_types}

        for t in ticket_types:
            req_ticket_type = req_map[t.id]
            if req_ticket_type["count"] + t.sold_count > t.quantity:
                abort(
                    400,
                    message=f"Not enough tickets available for '{t.name}'.",
                )

        order = OrderModel(user_id=get_jwt_identity())
        db.session.add(order)
        db.session.flush()

        order_total = 0

        for t in ticket_types:
            req_ticket_type = req_map[t.id]

            for _ in range(req_ticket_type["count"]):
                ticket = TicketModel(qr_code="", order_id=order.id, ticket_type_id=t.id)
                order_total += t.price
                db.session.add(ticket)

            t.sold_count = t.sold_count + req_ticket_type["count"]

        order.total_amount = order_total

        db.session.commit()

        return order
