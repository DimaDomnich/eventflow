from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
import redis
import os

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


def get_redis_client():
    return redis.from_url(os.getenv("REDIS_URL") or "")
