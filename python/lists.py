def do(redis_client):
    key = "queue"

    redis_client.delete(key)
    redis_client.lpush(key, "a", "b", "c")

    value = redis_client.rpop(key)
    print(f"[RPOP] {value}")

    rest = redis_client.lrange(key, 0, -1)
    print(f"[LRANGE] {rest}")

    assert value == "a"

if __name__ == "__main__":
    redis_client = get_client()
    do(redis_client=redis_client)
