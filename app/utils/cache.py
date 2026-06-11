import json
from flask import Response
from app.extensions import get_redis_client


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
