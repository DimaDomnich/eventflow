from flask_smorest import Blueprint

tags_blp = Blueprint("tags", __name__, description="Tag operations")

from . import routes
