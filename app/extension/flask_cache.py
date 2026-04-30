from flask_caching import Cache
from .redis_client import is_redis_available

import os

cache = Cache()

# =========================
# CACHE DIRECTORY
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_PATH = os.path.join(BASE_DIR, "tmp", "flask_cache")


def ensure_cache_dir():
    os.makedirs(CACHE_PATH, exist_ok=True)
    print(f"[CACHE] Directory ready: {CACHE_PATH}")


# =========================
# CONFIG
# =========================
class CacheConfig:
    # Single decision point
    CACHE_TYPE = "RedisCache" if is_redis_available() else "SimpleCache"

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

    if app.config["CACHE_TYPE"] == "FileSystemCache":
        ensure_cache_dir()
        print("[CACHE] Using FileSystemCache")

    cache.init_app(app)

    print(f"[CACHE] Initialized with type: {app.config['CACHE_TYPE']}")