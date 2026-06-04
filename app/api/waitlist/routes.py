from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models.event import EventModel
from app.models.waitlist import WaitlistModel
from app.schemas.waitlist import WaitlistSchema
from app.utils.decorators import role_required
from app.extensions import db
from flask_smorest import abort
from . import waitlist_blp


@waitlist_blp.route("/events/<int:event_id>")
class Waitlist(MethodView):
    @jwt_required()
    @role_required("attendee")
    @waitlist_blp.response(201, WaitlistSchema)
    def post(self, event_id):
        event = db.session.get(EventModel, event_id)

        if not event:
            abort(404, message="Invalid event.")

        if len(
            [
                ticket_type
                for ticket_type in event.ticket_types
                if ticket_type.sold_count == ticket_type.quantity
            ]
        ) < len(event.ticket_types):
            abort(400, message="Waitlist can't be joined for this event.")

        existing = WaitlistModel.query.filter_by(
            event_id=event_id, user_id=get_jwt_identity()
        ).first()
        if existing:
            abort(400, message="Already on the waitlist.")

        waitlist = WaitlistModel(user_id=get_jwt_identity(), event_id=event_id)

        db.session.add(waitlist)
        db.session.commit()

        return waitlist

    @jwt_required()
    @role_required("attendee")
    @waitlist_blp.response(204)
    def delete(self, event_id):
        event = db.session.get(EventModel, event_id)

        if not event:
            abort(404, message="Invalid event.")

        WaitlistModel.query.filter_by(
            event_id=event_id, user_id=get_jwt_identity()
        ).delete(synchronize_session=False)
        db.session.commit()
