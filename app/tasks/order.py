from sqlalchemy import select

from app.celery_app import celery
from app.models.order import OrderModel
from app.models.status import OrderStatusModel, TicketStatusModel
from app.extensions import db
from app.models.ticket import TicketStatusHistoryModel, TicketTypeModel
from app.tasks.waitlist import notify_next_waitlist_person


@celery.task
def expire_pending_order(order_id):
    print(order_id, "order_Id")
    order = db.session.get(OrderModel, order_id)
    if not order:
        return

    confirmed_order_status = OrderStatusModel.query.filter_by(name="confirmed").first()

    if order.status_id == confirmed_order_status.id:
        return

    cancelled_order_status = OrderStatusModel.query.filter_by(name="cancelled").first()

    order.status = cancelled_order_status

    cancelled_ticket_status = TicketStatusModel.query.filter_by(
        name="cancelled"
    ).first()
    ticket_type_cancels = dict()
    print("RAN 2")
    for ticket in order.tickets:
        if ticket.status.is_terminal:
            continue

        if ticket.ticket_type.id not in ticket_type_cancels:
            ticket_type_cancels[ticket.ticket_type.id] = 0

        ticket_type_cancels[ticket.ticket_type.id] += 1

        ticket.status = cancelled_ticket_status
        history_record = TicketStatusHistoryModel(
            ticket_id=ticket.id,
            status_id=cancelled_ticket_status.id,
            changed_by_id=order.user_id,  # technically, system updates it and not the user
        )
        db.session.add(history_record)

    for ticket_type_id, count in ticket_type_cancels.items():
        stmt = (
            select(TicketTypeModel)
            .where(TicketTypeModel.id == ticket_type_id)
            .with_for_update()
        )

        ticket_type = db.session.execute(stmt).scalar()
        ticket_type.sold_count -= count

    db.session.commit()

    event_id = order.tickets[0].ticket_type.event_id

    notify_next_waitlist_person.delay(event_id)
