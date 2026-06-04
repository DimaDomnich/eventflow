from flask_smorest import Blueprint

tickets_blp = Blueprint("tickets", __name__, description="Tickets operation")

from . import routes
