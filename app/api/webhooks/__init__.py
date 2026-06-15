from flask_smorest import Blueprint

webhooks_blp = Blueprint("webhooks", __name__, description="Webhook handlers")

from . import routes
