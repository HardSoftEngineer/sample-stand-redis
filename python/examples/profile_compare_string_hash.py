import json
import time
import random
import string
import statistics


def do(redis_client) -> None:
    # profile data
    profile = {
        "id": 42,
        "name": "Alice",
        "email": "alice@example.com",
        "balance": 100,
        "level": "gold",
        "state": "hold",
        "version": "1.0.0",
        "type": "user",
        "store": True,
    }
    text_length = 333
    text_item_number = 10
    for i in range(text_item_number):
        text = random_text = ''.join(random.choices(string.ascii_letters, k=text_length))
        profile.update({f"item_{i}": text})
    
    range_number = 10

    print("=== JSON String approach ===")
    # store
    profile_key_string = "user:42:profile_string"
    redis_client.set(profile_key_string, json.dumps(profile), ex=60)
    profile_key_string_dts = []
    
    # update balance 3 times
    for i in range(range_number):
        start = time.time()
        # 
        profile_str = redis_client.get(profile_key_string)
        profile_obj = json.loads(profile_str)
        # 
        profile_obj["balance"] += 50
        redis_client.set(profile_key_string, json.dumps(profile_obj), ex=60)
        # 
        profile_str = redis_client.get(profile_key_string)
        profile_obj = json.loads(profile_str)
        balance = profile_obj['balance']
        # 
        dt = time.time() - start
        profile_key_string_dts.append(dt)
        # 
        print(f"Update {i+1}: balance={balance}, time={round(dt, 6)}s")

    print("\n=== Redis Hash approach (increment + read)===")
    # store
    profile_key_hash = "user:42:profile_hash"
    profile_key_hash_w_dts = []
    profile_key_hash_wr_dts = []
    profile_key_hash_wr_pipe_dts = []
    profile_safe = {}
    for k, v in profile.items():
        if isinstance(v, bool):
            profile_safe[k] = str(v)
        else:
            profile_safe[k] = v
    redis_client.hset(profile_key_hash, mapping=profile_safe)
    redis_client.expire(profile_key_hash, 60)

    # update balance 3 times
    for i in range(range_number):
        start = time.time()
        redis_client.hincrby(profile_key_hash, "balance", 50)
        balance = int(redis_client.hget(profile_key_hash, "balance"))
        dt = time.time() - start
        profile_key_hash_wr_dts.append(dt)
        # 
        print(f"Update {i+1}: balance={balance}, time={round(dt, 6)}s")

    print("\n=== Redis Hash approach (pipe increment + read)===")
    # update balance 3 times
    for i in range(range_number):
        start = time.time()
        
        pipe = redis_client.pipeline()
        pipe.hincrby(profile_key_hash, "balance", 50)
        pipe.hget(profile_key_hash, "balance")
        balance = pipe.execute()[1]

        dt = time.time() - start
        profile_key_hash_wr_pipe_dts.append(dt)
        # 
        print(f"Update {i+1}: balance={balance}, time={round(dt, 6)}s")

    print("\n=== Redis Hash approach (increment balance only)===")
    # update balance 3 times
    for i in range(range_number):
        start = time.time()
        redis_client.hincrby(profile_key_hash, "balance", 50)
        dt = time.time() - start
        profile_key_hash_w_dts.append(dt)
        # 
        print(f"Update {i+1}: balance=???, time={round(dt, 6)}s")

    balance = int(redis_client.hget(profile_key_hash, "balance"))
    print(f"Update {i+1}: balance{balance} time={round(time.time()-start, 6)}s")

    # 
    string_avg = statistics.mean(profile_key_string_dts)
    print(f"string_avg: \t {string_avg}")
    hash_w_avg = statistics.mean(profile_key_hash_w_dts)
    print(f"hash_w_avg: \t {hash_w_avg}")
    hash_wr_avg = statistics.mean(profile_key_hash_wr_dts)
    print(f"hash_wr_avg: \t {hash_wr_avg}")
    hash_wr_pipe_avg = statistics.mean(profile_key_hash_wr_pipe_dts)
    print(f"hash_wr_pipe_avg: \t {hash_wr_pipe_avg}")


# Result
# string_avg:      0.0011257171630859376
# hash_w_avg:      0.00031933784484863283
# hash_wr_avg:     0.0006544589996337891
# hash_wr_pipe_avg:        0.0006614446640014649
