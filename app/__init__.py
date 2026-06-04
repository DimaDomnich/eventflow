from flask import Flask
from .config import config_map
from .extensions import db, migrate, jwt, bcrypt, configure_jwt
from flask_smorest import Api
from . import models
import os
from .celery_app import celery


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
    from .api.orders import orders_blp
    from .api.waitlist import waitlist_blp
    from .api.tickets import tickets_blp
    from .api.tags import tags_blp

    api.register_blueprint(auth_blp, url_prefix="/api/auth")
    api.register_blueprint(events_blp, url_prefix="/api/events")
    api.register_blueprint(orders_blp, url_prefix="/api/orders")
    api.register_blueprint(waitlist_blp, url_prefix="/api/waitlist")
    api.register_blueprint(tickets_blp, url_prefix="/api/tickets")
    api.register_blueprint(tags_blp, url_prefix="/api/tags")

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask

    return app
