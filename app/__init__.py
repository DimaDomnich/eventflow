from flask import Flask
from .config import config_map
from .extensions import db, migrate, jwt, bcrypt, configure_jwt
from . import models
import os


def create_app():
    app = Flask(__name__)

    env = os.getenv("FLASK_ENV", "development")
    app.config.from_object(config_map[env])

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    configure_jwt(app, jwt)
    bcrypt.init_app(app)

    from .api import api_bp

    app.register_blueprint(api_bp, url_prefix="/api")

    return app
