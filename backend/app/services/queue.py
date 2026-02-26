from rq import Queue

from app.core.redis_client import get_redis


def get_queue(name: str = "pulsewire") -> Queue:
    return Queue(name=name, connection=get_redis())
