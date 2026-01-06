import time 
import json 
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
    Store profile in Redis as JSON string with TTL.
    """
    try:
        profile_dump = json.dumps(profile)
        redis_client.set(key, profile_dump, ex=30)
    except (TypeError, ValueError) as exc:
        print(f"[ERROR] Failed to serialize profile: {exc}")
    except Exception as exc:
        raise RedisUnavailableError(f"Failed to write to Redis key={key}") from exc


def redis_get_key_profile(key: str, redis_client) -> str | None:
    """
    Infrastructure layer: retrieve cached profile from Redis.
    Raises RedisUnavailableError if Redis is unreachable
    """
    try:
        return redis_client.get(key)
    except Exception as exc:  # ловим все ошибки redis-py
        # raise RedisUnavailableError(f"Failed to read from Redis key={key}") from exc
        raise RedisUnavailableError(f"Failed to read from Redis key={key}") 


def redis_clear_cache_profile(user_id: int, redis_client) -> None:
    """
    Explicit cache invalidation.
    """
    try:
        key = redis_get_user_key(user_id)
        redis_client.delete(key)
    except Exception as exc:
        # raise RedisUnavailableError(f"Failed to clear cache key={key}") from exc
        raise RedisUnavailableError(f"Failed to clear cache key={key}")


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
        profile_str = redis_get_key_profile(key, redis_client)
    except RedisUnavailableError:
        # degraded mode: treat as cache miss
        profile_str = None

    if profile_str:
        try:
            # Cache hit
            return json.loads(profile_str)
        except json.JSONDecodeError as exc:
            # Corrupted cache entry → ignore cache
            print(f"[WARN] Invalid JSON in cache: {exc}")

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
