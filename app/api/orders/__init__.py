from flask_smorest import Blueprint

orders_blp = Blueprint("orders", __name__, description="Orders operations")

from . import routes
