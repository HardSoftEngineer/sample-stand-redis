from redis_client import get_client


def do(redis_client):
    key = "hello"
    value = "world"
    
    # set
    redis_client.set(key, value)
    print(f"Set key: {key}, value: {value}")
    # get
    value_redis = redis_client.get(key)
    print(f"Get key: {key}, value: {value_redis}")

    # 
    assert value == value_redis, (
        f"Value mismatch: expected={value}, actual={value_redis}"
    )

if __name__ == "__main__":
    redis_client = get_client()
    do(redis_client=redis_client)
