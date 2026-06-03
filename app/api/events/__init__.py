from flask_smorest import Blueprint

events_blp = Blueprint("events", __name__, description="Events operations")

from . import routes
