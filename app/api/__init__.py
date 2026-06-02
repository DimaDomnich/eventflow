from flask import Blueprint

api_bp = Blueprint("api", __name__)

from .auth import auth_blp

api_bp.register_blueprint(auth_blp, url_prefix="/auth")
