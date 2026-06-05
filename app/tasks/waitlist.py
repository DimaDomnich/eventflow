import os

from app.celery_app import celery
from app.models.user import UserModel
from app.models.waitlist import WaitlistModel
from app.extensions import db, get_ses_client
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

    ses = get_ses_client()

    user = UserModel.query.get(waitlist.user_id)

    ses.send_email(
        Source=os.getenv("SES_SENDER"),
        Destination={"ToAddresses": [user.email]},
        Message={
            "Subject": {"Data": "A spot opened up for your waitlisted event"},
            "Body": {
                "Text": {
                    "Data": f"Hi {user.full_name}, a ticket is now available. You have 5 minutes to purchase before the next person is notified."
                }
            },
        },
    )

    waitlist.notified_at = datetime.now(timezone.utc)

    waitlist.expired_at = waitlist.notified_at + timedelta(minutes=5)

    db.session.commit()


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
