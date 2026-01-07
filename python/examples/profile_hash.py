import time 
from typing import Dict, Any

from errors import RedisUnavailableError


def data_get_profile(user_id: int, slow_operation: bool = True) -> Dict[str, Any]:
    """
    Simulates fetching a user profile from a slow data source
    (e.g. database, external API).

    Args:
        user_id: User identifier
        slow_operation: If True, simulates latency

    Returns:
        User profile dictionary
    """
    if slow_operation:
        time.sleep(1)  # simulate slow I/O operation

    profile = {
        "id": user_id,
        "name": "Alice",
        "balance": 100,
    }
    return profile


def redis_get_user_key(user_id: int) -> str:
    """
    Builds a Redis key for storing user profile.

    Using a consistent key naming strategy is critical
    for cache invalidation and debugging.

    Example:
        user:42:profile
    """
    return f"user:{user_id}:profile"


def redis_set_key_profile(key: str, profile: Dict[str, Any], redis_client) -> None:
    """
    Stores a user profile as a Redis hash.
    Raises RedisUnavailableError on failure.
    """
    try:
        redis_client.hset(key, mapping=profile)
        redis_client.expire(key, 30)  # TTL 30 seconds for entire hash
    except Exception as exc:
        raise RedisUnavailableError(f"Failed to write hash to Redis key={key}") from exc


def redis_get_key_profile(key: str, redis_client) -> str | None:
    """
    Retrieves a Redis hash as a dictionary.
    Returns None if cache miss.
    Raises RedisUnavailableError if Redis is unreachable.
    """
    try:
        data = redis_client.hgetall(key)
        return data if data else None
    except Exception as exc:
        raise RedisUnavailableError(f"Failed to read hash from Redis key={key}") from exc


def redis_clear_cache_profile(user_id: int, redis_client) -> None:
    """
    Deletes the entire Redis hash.
    """
    try:
        key = redis_get_user_key(user_id)
        redis_client.delete(key)
    except Exception as exc:
        raise RedisUnavailableError(f"Failed to delete hash from Redis key={key}") from exc


def app_get_profile(user_id: int, redis_client) -> Dict[str, Any]:
    """
    Application-level function implementing
    cache-aside (lazy loading) pattern.

    Flow:
        1. Try Redis
        2. On cache miss -> fetch from source
        3. Save result to Redis
        4. Return profile
    """
    key = f"user:{user_id}:profile"

    try:
        profile = redis_get_key_profile(key, redis_client)
    except RedisUnavailableError:
        # degraded mode: treat as cache miss
        profile = None

    if profile:
        return profile

    # Cache miss or invalid cache
    profile = data_get_profile(user_id)

    try:
        redis_set_key_profile(key, profile, redis_client)
    except RedisUnavailableError:
        # ignore, fallback only
        pass

    return profile


def do(redis_client) -> None:
    """
    Demo runner:
    - clears cache
    - fetches the same profile multiple times
    - demonstrates cache speedup
    """
    user_id = 42

    redis_clear_cache_profile(user_id, redis_client)

    for i in range(5):
        iter_time_start = time.time()
        profile = app_get_profile(user_id, redis_client)
        iter_time_stop = time.time()
        iter_dt = iter_time_stop - iter_time_start

        print(f"iter: {i}, profile: {profile}, get time: {round(iter_dt, 6)} s")


# Result
# iter: 0, profile: {'id': 42, 'name': 'Alice', 'balance': 100}, get time: 1.00127 s
# iter: 1, profile: {'id': '42', 'name': 'Alice', 'balance': '100'}, get time: 0.000259 s
# iter: 2, profile: {'id': '42', 'name': 'Alice', 'balance': '100'}, get time: 0.000739 s
# iter: 3, profile: {'id': '42', 'name': 'Alice', 'balance': '100'}, get time: 0.000612 s
# iter: 4, profile: {'id': '42', 'name': 'Alice', 'balance': '100'}, get time: 0.000455 s
