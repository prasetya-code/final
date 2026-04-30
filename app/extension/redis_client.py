import os
import redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

_client = None


def get_redis_client(timeout=2):
    """
    Return cached Redis client jika tersedia, jika gagal return None
    """
    global _client

    if _client is not None:
        return _client

    try:
        client = redis.Redis.from_url(
            REDIS_URL,
            socket_connect_timeout=timeout,
            socket_timeout=timeout,
        )

        client.ping()
        _client = client

        print("[REDIS] Connected successfully")
        return client

    except Exception as e:
        print(f"[REDIS WARNING] Connection failed: {e}")
        _client = None
        return None


def is_redis_available():
    return get_redis_client() is not None