from rq import Connection, Worker

from app.core.redis_client import get_redis


if __name__ == "__main__":
    with Connection(get_redis()):
        worker = Worker(["pulsewire"])
        worker.work()
