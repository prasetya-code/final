from flask_caching import Cache
import os

cache = Cache()

# =========================
# CACHE DIRECTORY
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_PATH = os.path.join(BASE_DIR, "tmp", "flask_cache")


def ensure_cache_dir():
    try:
        os.makedirs(CACHE_PATH, exist_ok=True)
        print(f"[CACHE] Directory ready: {CACHE_PATH}")

    except Exception as e:
        print(f"[CACHE ERROR] Failed to create cache dir: {e}")


# =========================
# CONFIG
# =========================
class CacheConfig:
    CACHE_TYPE = os.getenv("CACHE_TYPE", "SimpleCache")

    CACHE_DEFAULT_TIMEOUT = int(os.getenv("CACHE_DEFAULT_TIMEOUT", 300))
    CACHE_THRESHOLD = int(os.getenv("CACHE_THRESHOLD", 500))
    CACHE_IGNORE_ERRORS = True
    CACHE_KEY_PREFIX = os.getenv("CACHE_KEY_PREFIX", "myapp_")

    CACHE_REDIS_URL = os.getenv("CACHE_REDIS_URL", "redis://localhost:6379/0")

    CACHE_DIR = CACHE_PATH
    CACHE_NO_NULL_WARNING = True


# =========================
# INIT CACHE
# =========================
def init_cache(app):
    app.config.from_object(CacheConfig)

    cache_type = app.config.get("CACHE_TYPE")

    # =========================
    # FILESYSTEM CACHE
    # =========================
    if cache_type == "FileSystemCache":
        ensure_cache_dir()
        print("[CACHE] Using FileSystemCache")

    # =========================
    # REDIS CHECK
    # =========================
    if cache_type == "RedisCache":
        try:
            import redis

            r = redis.Redis.from_url(
                app.config["CACHE_REDIS_URL"],

                # REDIS CHECK
                socket_connect_timeout=2,
                socket_timeout=2,
            )
            r.ping()

            print("[CACHE] Redis connected successfully")

        except Exception as e:
            print(f"[CACHE WARNING] Redis failed, fallback to SimpleCache: {e}")
            app.config["CACHE_TYPE"] = "SimpleCache"

    cache.init_app(app)