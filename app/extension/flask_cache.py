from flask_caching import Cache
from .redis_client import is_cache_redis_available, REDIS_CACHE_URL

import os, traceback

fl_cache = Cache()

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
        print(f"[CACHE ERROR] Failed to create cache directory: {e}")
        traceback.print_exc()


# =========================
# CONFIG (STATIC ONLY)
# =========================
class CacheConfig:
    """CACHE_TYPE options (yang paling sering digunakan):

    1. "SimpleCache"
       - In-memory cache (fallback default)
       - Cocok untuk development / aplikasi kecil

    2. "RedisCache"
       - Menggunakan Redis sebagai backend
       - Cocok untuk production (scalable & shared cache)

    3. "FileSystemCache"
       - Cache disimpan di filesystem (disk)
       - Perlu set CACHE_DIR
       - Alternatif jika tidak ada Redis

    4. "NullCache"
       - Tidak melakukan caching sama sekali
       - Berguna untuk debugging

    Catatan:
    - Gunakan RedisCache untuk production jika memungkinkan
    - SimpleCache tidak cocok untuk multi-worker (misal gunicorn)

    ⚠️ IMPORTANT:
    - Class ini hanya berisi konfigurasi statis
    - Logic pemilihan CACHE_TYPE dilakukan di init_cache()
    """

    # =========================
    # GENERAL CACHE SETTINGS
    # =========================
    CACHE_DEFAULT_TIMEOUT = int(os.getenv("CACHE_DEFAULT_TIMEOUT", 300))
    CACHE_THRESHOLD = int(os.getenv("CACHE_THRESHOLD", 500))
    CACHE_IGNORE_ERRORS = True
    CACHE_KEY_PREFIX = os.getenv("CACHE_KEY_PREFIX", "myapp_")

    # =========================
    # REDIS CONFIG
    # =========================
    CACHE_REDIS_URL = REDIS_CACHE_URL

    # =========================
    # FILESYSTEM CONFIG
    # =========================
    CACHE_DIR = CACHE_PATH

    # Disable warning untuk null cache
    CACHE_NO_NULL_WARNING = True


# =========================
# INIT CACHE
# =========================
def init_cache(app):
    try:
        # =========================
        # LOAD STATIC CONFIG
        # =========================
        app.config.from_object(CacheConfig)

        # =========================
        # ENV CONTROL (OPTIONAL)
        # =========================
        USE_REDIS_CACHE = os.getenv("USE_REDIS_CACHE", "true").lower() == "true"

        # =========================
        # GLOBAL CONTROL (MASTER SWITCH)
        # =========================
        global_redis = app.config.get("GLOBAL_REDIS", True)

        # print(f"[CACHE] GLOBAL_REDIS = {global_redis}")
        print(f"[CACHE] ENV USE_REDIS_CACHE = {USE_REDIS_CACHE}")

        # =========================
        # DECISION FLOW
        # =========================
        if not global_redis:
            print("[CACHE] Disabled Redis")
            cache_type = "SimpleCache"

        elif not USE_REDIS_CACHE:
            print("[CACHE] Disabled via ENV → using SimpleCache")
            cache_type = "SimpleCache"

        else:
            print("[CACHE] Checking Redis availability...")

            if is_cache_redis_available():
                print("[CACHE] Redis available → using RedisCache")
                cache_type = "RedisCache"
            else:
                print("[CACHE WARNING] Redis not available → fallback to SimpleCache")
                cache_type = "SimpleCache"

        # =========================
        # APPLY CACHE TYPE
        # =========================
        app.config["CACHE_TYPE"] = cache_type

        # =========================
        # FILESYSTEM HANDLING
        # =========================
        if cache_type == "FileSystemCache":
            ensure_cache_dir()
            print("[CACHE] Using FileSystemCache")

        # =========================
        # INIT CACHE
        # =========================
        fl_cache.init_app(app)

        print(f"[CACHE] Initialized with type: {cache_type} \n")

    except Exception as e:
        print(f"[CACHE ERROR] Failed to initialize cache: {e}")
        traceback.print_exc()

        # =========================
        # FALLBACK
        # =========================
        try:
            print("[CACHE] Falling back to SimpleCache (manual fallback)")
            app.config["CACHE_TYPE"] = "SimpleCache"
            fl_cache.init_app(app)

        except Exception as fallback_error:
            print(f"[CACHE CRITICAL] Fallback failed: {fallback_error}")
            traceback.print_exc()