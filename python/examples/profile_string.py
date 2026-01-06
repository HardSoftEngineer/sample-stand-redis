import time 
import json 


def data_get_profile(user_id, slow_operation=True):
    if slow_operation:
        time.sleep(1)
    # 
    profile = {
            "id": user_id,
            "name": "Alice",
            "balance": 100
        }
    return profile

def redis_get_user_key(user_id):
    cache_key = f"user:{user_id}:profile"
    return cache_key

def redis_set_key_profile(key, profile, redis_client):
    profile_dump = json.dumps(profile)
    redis_client.set(key, profile_dump, ex=30)

def redis_get_key_profile(key, redis_client):
    profil = redis_client.get(key)
    return profil

def redis_clear_cache_profile(user_id, redis_client):
    key = redis_get_user_key(user_id)
    redis_client.delete(key)

def app_get_profile(user_id, redis_client):
    key = redis_get_user_key(user_id)
    profile_str = redis_get_key_profile(key, redis_client)
    if profile_str:
        profile = json.loads(profile_str)
    else:
        profile = data_get_profile(user_id)
        redis_set_key_profile(key, profile, redis_client)
    return profile

def do(redis_client):
    user_id = 42
    redis_clear_cache_profile(user_id, redis_client)
    for i in range(5):
        iter_time_start = time.time()
        profile = app_get_profile(user_id, redis_client)
        iter_time_stop = time.time()
        iter_dt = iter_time_stop - iter_time_start

        print(f"profile: {profile} get time: {round(iter_dt, 6)}")
