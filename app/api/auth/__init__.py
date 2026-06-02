from flask import Blueprint

auth_blp = Blueprint("auth", __name__)

from . import routes
