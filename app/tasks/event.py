from datetime import datetime, timezone

from sqlalchemy import select

from app.celery_app import celery
from app.extensions import db
from app.models.event import EventModel, EventStatusHistoryModel
from app.models.status import EventStatusModel
from app.tasks.order import cancel_pending_orders_for_event


@celery.task
def process_finished_events():
    event_published_status = EventStatusModel.query.filter_by(name="published").first()
    finished_events = (
        db.session.execute(
            select(EventModel).where(
                datetime.now(timezone.utc) > EventModel.ends_at,
                EventModel.status_id == event_published_status.id,
            )
        )
        .scalars()
        .all()
    )

    event_completed_status = EventStatusModel.query.filter_by(name="completed").first()
    for e in finished_events:
        e.status_id = event_completed_status.id

        history_entry = EventStatusHistoryModel(
            event_id=e.id,
            status_id=event_completed_status.id,
            changed_by_id=e.organizer_id,
        )
        db.session.add(history_entry)

        cancel_pending_orders_for_event.delay(e.id)

    db.session.commit()
