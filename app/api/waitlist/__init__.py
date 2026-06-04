from flask_smorest import Blueprint

waitlist_blp = Blueprint("waitlist", __name__, description="Waitlist operations")

from . import routes
