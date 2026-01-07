import json
import time
import random
import string
import statistics
import matplotlib.pyplot as plt
import redis


def random_text(length):
    return ''.join(random.choices(string.ascii_letters, k=length))

def profile_dict(text_length, text_item_number):
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
    for i in range(text_item_number):
        profile[f"item_{i}"] = random_text(text_length)
    return profile

def measure_times(profile, redis_client, range_number=3):
    # JSON string approach
    profile_key_string = "user:42:profile_string"
    redis_client.set(profile_key_string, json.dumps(profile), ex=60)
    string_dts = []
    for _ in range(range_number):
        start = time.time()
        profile_obj = json.loads(redis_client.get(profile_key_string))
        profile_obj["balance"] += 50
        redis_client.set(profile_key_string, json.dumps(profile_obj), ex=60)
        _ = json.loads(redis_client.get(profile_key_string))["balance"]
        string_dts.append(time.time() - start)

    # Redis hash
    profile_key_hash = "user:42:profile_hash"
    profile_safe = {k: str(v) if isinstance(v, bool) else v for k, v in profile.items()}
    redis_client.hset(profile_key_hash, mapping=profile_safe)
    redis_client.expire(profile_key_hash, 60)

    hash_w_dts = []
    hash_wr_dts = []
    hash_wr_pipe_dts = []

    for _ in range(range_number):
        # write only
        start = time.time()
        redis_client.hincrby(profile_key_hash, "balance", 50)
        hash_w_dts.append(time.time() - start)

        # write+read
        start = time.time()
        redis_client.hincrby(profile_key_hash, "balance", 50)
        _ = int(redis_client.hget(profile_key_hash, "balance"))
        hash_wr_dts.append(time.time() - start)

        # write+read pipeline
        start = time.time()
        pipe = redis_client.pipeline()
        pipe.hincrby(profile_key_hash, "balance", 50)
        pipe.hget(profile_key_hash, "balance")
        _ = pipe.execute()[1]
        hash_wr_pipe_dts.append(time.time() - start)

    return (
        statistics.mean(string_dts),
        statistics.mean(hash_w_dts),
        statistics.mean(hash_wr_dts),
        statistics.mean(hash_wr_pipe_dts),
        len(json.dumps(profile))  # dictionary size in bytes
    )


def do(redis_client) -> None:
    # Testing on different sizes
    # v1
    # text_lengths = [50, 100, 200, 400, 800, 1600, 3200, 6400]
    # v2
    text_lengths = [i for i in range(1, 10000, 100)]

    # v1
    # text_item_numbers = [5, 10, 20]
    # v2
    text_item_numbers = [20]
    
    results = []

    for tl in text_lengths:
        for tin in text_item_numbers:
            profile = profile_dict(tl, tin)
            string_avg, hash_w_avg, hash_wr_avg, hash_wr_pipe_avg, profile_size = measure_times(profile, redis_client)
            results.append({
                "profile_size": profile_size,
                "string_avg": string_avg,
                "hash_w_avg": hash_w_avg,
                "hash_wr_avg": hash_wr_avg,
                "hash_wr_pipe_avg": hash_wr_pipe_avg
            })
            print(f"Size={profile_size} bytes: string_avg={string_avg:.6f}, hash_w_avg={hash_w_avg:.6f}, hash_wr_avg={hash_wr_avg:.6f}, hash_wr_pipe_avg={hash_wr_pipe_avg:.6f}")

            time.sleep(0.1)

    # Building a graph
    results = sorted(results, key=lambda x: x["profile_size"])
    sizes = [r["profile_size"] for r in results]
    plt.plot(sizes, [r["string_avg"] for r in results], label="JSON String")
    plt.plot(sizes, [r["hash_w_avg"] for r in results], label="Hash Write only")
    plt.plot(sizes, [r["hash_wr_avg"] for r in results], label="Hash Write+Read")
    plt.plot(sizes, [r["hash_wr_pipe_avg"] for r in results], label="Hash Pipeline")
    plt.xlabel("Profile size (bytes)")
    plt.ylabel("Average update time (s)")
    plt.title("Redis update times vs profile size")
    plt.legend()
    plt.grid(True)
    plt.savefig("graph.png")
    plt.close()


# Result see ../../docs/media/profile_compare_string_hash_graph_[].png
