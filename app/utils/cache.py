from functools import wraps
import json
import time
import uuid
from flask import Response
from flask_jwt_extended import get_jwt_identity
from app.extensions import get_redis_client
from flask_smorest import abort

RATE_LIMIT = 3
RATE_WINDOW_SECONDS = 60


def make_cache_key(params):
    serializable = {
        k: v.isoformat() if hasattr(v, "isoformat") else v for k, v in params.items()
    }
    return f"events:{json.dumps(serializable, sort_keys=True)}"


def get_cached(key):
    redis = get_redis_client()
    cached = redis.get(key)
    if cached:
        return Response(cached, mimetype="application/json")
    return None


def set_cached(key, data, ex=60):
    redis = get_redis_client()
    redis.set(key, json.dumps(data), ex=ex)


def invalidate_pattern(pattern):
    redis = get_redis_client()
    keys = redis.keys(pattern)
    if keys:
        redis.delete(*keys)


def rate_limit(key: str, rate_limit=RATE_LIMIT, window_seconds=RATE_WINDOW_SECONDS):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user_id = get_jwt_identity()
            r = get_redis_client()
            cache_key = f"rate_limit:{key}:{user_id}"
            now = time.time()

            r.zremrangebyscore(cache_key, "-inf", now - window_seconds)

            if r.zcard(cache_key) >= rate_limit:
                abort(429, message="Too many requests.")

            r.zadd(cache_key, {str(uuid.uuid4()): now})
            r.expire(cache_key, window_seconds)

            return fn(*args, **kwargs)

        return wrapper

    return decorator
