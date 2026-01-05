import os
import redis


def get_client(host=None, port=None):
    if host is None:
        host = os.getenv("REDIS_HOST", "localhost")
    if port is None:
        port = os.getenv("REDIS_PORT", 6379)
    redis_client = redis.Redis(host=host, port=port, decode_responses=True)
    return redis_client
