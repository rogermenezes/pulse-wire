import json

from app.core.redis_client import get_redis


def get_cache_json(key: str) -> dict | None:
    try:
        redis = get_redis()
        payload = redis.get(key)
        if not payload:
            return None
        return json.loads(payload)
    except Exception:
        return None


def set_cache_json(key: str, value: dict, ttl_seconds: int) -> None:
    try:
        redis = get_redis()
        redis.setex(key, ttl_seconds, json.dumps(value, default=str))
    except Exception:
        return
