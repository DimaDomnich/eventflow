from sqlalchemy import select

from app.celery_app import celery
from app.models.event import EventModel
from app.models.order import OrderModel
from app.models.status import OrderStatusModel, TicketStatusModel
from app.extensions import db
from app.models.ticket import TicketModel, TicketStatusHistoryModel, TicketTypeModel
from app.models.waitlist import WaitlistModel
from app.tasks.waitlist import notify_next_waitlist_person


@celery.task
def expire_pending_order(order_id):
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


@celery.task
def cancel_pending_orders_for_event(event_id):
    event = db.session.get(EventModel, event_id)
    if not event:
        return

    event_ticket_types = (
        db.session.execute(
            select(TicketTypeModel)
            .where(TicketTypeModel.event_id == event_id)
            .with_for_update()
        )
        .scalars()
        .all()
    )

    cancelled_ticket_status = TicketStatusModel.query.filter_by(
        name="cancelled"
    ).first()
    reserved_ticket_status = TicketStatusModel.query.filter_by(name="reserved").first()
    cancelled_order_status = OrderStatusModel.query.filter_by(name="cancelled").first()
    pending_order_status = OrderStatusModel.query.filter_by(name="pending").first()

    order_ids_to_cancel = set()

    for ticket_type in event_ticket_types:
        tickets_to_cancel = TicketModel.query.filter_by(
            ticket_type_id=ticket_type.id, status_id=reserved_ticket_status.id
        ).all()
        cancelled_tickets_count = 0

        for t in tickets_to_cancel:
            t.status = cancelled_ticket_status
            cancelled_tickets_count += 1

            history_record = TicketStatusHistoryModel(
                ticket_id=t.id,
                status_id=cancelled_ticket_status.id,
                changed_by_id=event.organizer_id,
            )
            db.session.add(history_record)

            order_ids_to_cancel.add(t.order_id)

        ticket_type.sold_count -= cancelled_tickets_count

    orders_stmt = select(OrderModel).filter(
        OrderModel.id.in_(order_ids_to_cancel),
        OrderModel.status_id == pending_order_status.id,
    )
    orders_to_cancel = db.session.execute(orders_stmt).scalars().all()
    for order in orders_to_cancel:
        order.status = cancelled_order_status

    WaitlistModel.query.filter_by(event_id=event_id).delete(synchronize_session=False)

    db.session.commit()
