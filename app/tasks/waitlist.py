from app.celery_app import celery
from app.models.waitlist import WaitlistModel
from app.extensions import db
from datetime import datetime, timedelta, timezone


@celery.task
def notify_next_waitlist_person(event_id):
    waitlist = (
        WaitlistModel.query.filter(
            WaitlistModel.event_id == event_id,
            WaitlistModel.notified_at == None,  # noqa: E711
        )
        .order_by(WaitlistModel.joined_at.asc())
        .first()
    )

    if not waitlist:
        return

    waitlist.notified_at = datetime.now(timezone.utc)

    waitlist.expired_at = waitlist.notified_at + timedelta(minutes=5)

    db.session.commit()

    print(f"Notifying user {waitlist.user_id} for event {event_id}")


@celery.task
def process_expired_waitlist():
    now = datetime.now(timezone.utc)

    expired_waitlists = WaitlistModel.query.filter(
        WaitlistModel.expired_at != None,  # noqa: E711
        WaitlistModel.expired_at < now,
    ).all()

    for expired in expired_waitlists:
        db.session.delete(expired)
        notify_next_waitlist_person.delay(expired.event_id)

    db.session.commit()
