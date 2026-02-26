from redis import Redis

from app.core.config import settings


def get_redis(*, decode_responses: bool = True) -> Redis:
    return Redis.from_url(settings.redis_url, decode_responses=decode_responses)
