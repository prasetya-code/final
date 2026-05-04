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
# CONFIG
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
    """

    try:
        CACHE_TYPE = "RedisCache" if is_cache_redis_available() else "SimpleCache"
        
    except Exception as e:
        print(f"[CACHE WARNING] Redis check failed: {e}")
        traceback.print_exc()
        CACHE_TYPE = "SimpleCache"  # fallback paksa jika error

    # =========================
    # GENERAL CACHE SETTINGS
    # =========================
    # Default timeout cache (detik)
    CACHE_DEFAULT_TIMEOUT = int(os.getenv("CACHE_DEFAULT_TIMEOUT", 300))

    # Jumlah maksimum item dalam cache
    CACHE_THRESHOLD = int(os.getenv("CACHE_THRESHOLD", 500))

    # Abaikan error cache (tidak crash app)
    CACHE_IGNORE_ERRORS = True

    # Prefix key cache (untuk namespacing)
    CACHE_KEY_PREFIX = os.getenv("CACHE_KEY_PREFIX", "myapp_")

    # =========================
    # REDIS CONFIG
    # =========================
    # Menggunakan single source of truth dari redis_client
    CACHE_REDIS_URL = REDIS_CACHE_URL

    # =========================
    # FILESYSTEM CONFIG
    # =========================
    # Digunakan jika CACHE_TYPE = FileSystemCache
    CACHE_DIR = CACHE_PATH

    # Disable warning untuk null cache
    CACHE_NO_NULL_WARNING = True


# =========================
# INIT CACHE
# =========================
def init_cache(app):
    try:
        # Load konfigurasi ke Flask app
        app.config.from_object(CacheConfig)

        # Jika menggunakan FileSystemCache → pastikan directory ada
        if app.config["CACHE_TYPE"] == "FileSystemCache":
            ensure_cache_dir()

            print("[CACHE] Using FileSystemCache")

        # Inisialisasi cache
        fl_cache.init_app(app)

        print(f"[CACHE] Initialized with type: {app.config['CACHE_TYPE']}")

    except Exception as e:
        print(f"[CACHE ERROR] Failed to initialize cache: {e}")
        traceback.print_exc()

        # Fallback manual (extra safety)
        try:
            print("[CACHE] Falling back to SimpleCache (manual fallback)")
            app.config["CACHE_TYPE"] = "SimpleCache"
            fl_cache.init_app(app)

        except Exception as fallback_error:
            print(f"[CACHE CRITICAL] Fallback failed: {fallback_error}")
            traceback.print_exc()