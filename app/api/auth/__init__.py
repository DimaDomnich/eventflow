from flask_smorest import Blueprint

auth_blp = Blueprint("auth", __name__, description="Auth operations")

from . import routes
