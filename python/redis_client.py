import os
import redis

from errors import RedisUnavailableError


def get_client(host=None, port=None, timeout=1):
    """
    Creates Redis client and validates connection immediately.

    Fails fast if Redis is not available.
    """
    host = host or os.getenv("REDIS_HOST", "localhost")
    port = int(port or os.getenv("REDIS_PORT", 6379))

    try:
        redis_client = redis.Redis(
            host=host,
            port=port,
            socket_connect_timeout=timeout,
            socket_timeout=timeout,
            decode_responses=True,
        )

        # Force connection on startup for test
        redis_client.ping()

    except (
        redis.ConnectionError,
        redis.TimeoutError,
        redis.AuthenticationError,
    ) as exc:
        raise RedisUnavailableError(
            f"Redis is not available at {host}:{port}"
        )

    return redis_client
