from flask import Flask
from .config import config_map
from .extensions import db, migrate, jwt, bcrypt, configure_jwt
from flask_smorest import Api
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

    api = Api(app)

    from .api.auth import auth_blp
    from .api.events import events_blp

    api.register_blueprint(auth_blp, url_prefix="/api/auth")
    api.register_blueprint(events_blp, url_prefix="/api/events")

    return app
