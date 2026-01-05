def do(redis_client):
    key = "hello"
    value = "world"

    redis_client.delete(key)
    
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
