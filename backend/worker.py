from rq import SimpleWorker

from app.core.redis_client import get_redis


if __name__ == "__main__":
    redis = get_redis(decode_responses=False)
    worker = SimpleWorker(["pulsewire"], connection=redis)
    worker.work()
