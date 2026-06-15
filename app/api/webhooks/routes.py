import os
from flask import request
from flask_smorest import abort
from flask.views import MethodView
import stripe
from app.extensions import db
from app.models.order import OrderModel
from app.models.status import OrderStatusModel, TicketStatusModel
from app.models.ticket import TicketStatusHistoryModel
from app.tasks.order import expire_pending_order

from . import webhooks_blp


@webhooks_blp.route("/stripe")
class StripeWebhook(MethodView):
    @webhooks_blp.response(200)
    def post(self):
        payload = request.get_data()
        sig_header = request.headers.get("Stripe-Signature")

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, os.getenv("STRIPE_WEBHOOK_SECRET")
            )
            event_type = event["type"]
            p_id = event["data"]["object"]["id"]

            if event_type == "payment_intent.succeeded":
                order = OrderModel.query.filter_by(payment_intent_id=p_id).first()

                if not order:
                    return {"status": "order not found"}, 200

                pending_order_status = OrderStatusModel.query.filter_by(
                    name="pending"
                ).first()
                if order.status_id != pending_order_status.id:
                    return {"status": "already processed"}, 200

                confirmed_order_status = OrderStatusModel.query.filter_by(
                    name="confirmed"
                ).first()
                reserved_ticket_status = TicketStatusModel.query.filter_by(
                    name="reserved"
                ).first()
                confirmed_ticket_status = TicketStatusModel.query.filter_by(
                    name="confirmed"
                ).first()

                order.status = confirmed_order_status

                for ticket in order.tickets:
                    if ticket.status_id != reserved_ticket_status.id:
                        continue

                    ticket.status = confirmed_ticket_status

                    history_record = TicketStatusHistoryModel(
                        ticket_id=ticket.id,
                        status_id=confirmed_ticket_status.id,
                        changed_by_id=order.user_id,
                    )
                    db.session.add(history_record)

                db.session.commit()

                return {"status": f"successfully confirmed order {order.id}"}, 200

            elif event_type == "payment_intent.payment_failed":
                print("RAN")
                order = OrderModel.query.filter_by(payment_intent_id=p_id).first()
                if not order:
                    return {"status": "order not found"}, 200

                expire_pending_order.apply_async(args=[order.id], countdown=300)

                return {"status": "received"}, 200

            else:
                return {"status": "ignored"}, 200

        except stripe.error.SignatureVerificationError:
            abort(400, message="Invalid signature.")
