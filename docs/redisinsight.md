# RedisInsight 

## Docs 
https://redis.io/insight/

https://hub.docker.com/r/redis/redisinsight


## Auto-setup attempts

### Goal

Automatically have Redis connection available in RedisInsight UI after container startup.

Captures attempts to preconfigure RedisInsight connections automatically via Docker.

### Attempt 1: Environment variables
---
**Configuration**

docker/docker-compose.yml
```yaml
services:
  redisinsight:
    image: redis/redisinsight:2.70
    container_name: sample-stand-redisinsight
    environment:
      - REDIS_HOST=sample-stand-redis
      - REDIS_PORT=6379
...
```

**Expected**

Redis database appears in RedisInsight UI on startup.

**Actual**

No connections appear.

**Notes**

RedisInsight does not use these variables for connection setup.


### Attempt 2: Pre-seeded connections file
---

**Configuration**

https://redis.io/docs/latest/operate/redisinsight/configuration/

docker/docker-compose.yml 
```yaml
services:
  redisinsight:
    image: redis/redisinsight:2.70
    container_name: sample-stand-redisinsight
    environment:
        RI_PRE_SETUP_DATABASES_PATH: /confs/connections.json
    volumes:
        - ./redisinsight/connections.json:/confs/connections.json:ro
...
```

docker/redisinsight/connections.json
```json
{
  "connections": [
    {
      "id": "sample-stand-redis",
      "name": "Sample Stand Redis",
      "host": "sample-stand-redis",
      "port": 6379,
      "username": "default",
      "password": "",
      "tls": false
    }
  ]
}
```

Find for "connectionType": "CLUSTER" 

https://github.com/redis/RedisInsight/issues/4737

**Expected**

RedisInsight loads connections from JSON file.

**Actual**

No connections appear.

**Notes**

- JSON format is undocumented and version-dependent
- File is not loaded or is overridden at startup


### Conclusion

As of current RedisInsight 2.70 version, there is no reliable and supported way to pre-configure Redis connections via Docker.

Manual setup in UI is required.
