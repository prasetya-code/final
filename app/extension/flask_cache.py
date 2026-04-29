from flask_caching import Cache
import os

cache = Cache()


# =========================
# FILESYSTEM CACHE SETUP (OPTIONAL / RUNTIME SAFE)
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_PATH = os.path.join(BASE_DIR, "tmp", "flask_cache")

def ensure_cache_dir():
    """
    Membuat folder cache hanya jika FileSystemCache digunakan.
    Tidak dijalankan saat import (lebih aman untuk production).
    """
    try:
        os.makedirs(CACHE_PATH, exist_ok=True)
        print(f"[CACHE DEBUG] Using cache dir: {CACHE_PATH}")

    except Exception as e:
        print(f"[CACHE ERROR] {e}")


class CacheConfig:
    """ CACHE_TYPE options (Flask-Caching):

    1. "SimpleCache"
    - Cache di memory (RAM)
    - ✔ cocok: development / app kecil
    - ❌ tidak cocok: production (multi worker)
    - ❌ data hilang saat restart

    2. "NullCache"
    - Tidak ada cache (disable cache)
    - ✔ cocok: debugging / testing
    - semua request selalu fresh

    3. "FileSystemCache"
    - Cache disimpan di file (disk)
    - ✔ cocok: dev / small production tanpa Redis
    - perlu: CACHE_DIR
    - ❌ lebih lambat dari memory/Redis

    4. "RedisCache"
    - Cache pakai Redis server
    - ✔ cocok: production
    - ✔ cepat & bisa multi instance
    - perlu: Redis server

    5. "MemcachedCache"
    - Cache pakai Memcached
    - ✔ cocok: production
    - ✔ cepat
    - ❌ kurang populer dibanding Redis sekarang

    6. "SASLMemcachedCache"
    - Memcached dengan autentikasi (SASL)
    - ✔ untuk server yang butuh login

    7. "SpreadSASLMemcachedCache"
    - Versi advanced Memcached (data besar di-split)
    - jarang dipakai

    8. "UWSGICache"
    - Cache bawaan uWSGI
    - ✔ hanya kalau pakai uWSGI server
    - ❌ tidak portable

    9. Custom backend (advanced)
    - Bisa buat cache sendiri (custom class/path)
    - contoh:
        CACHE_TYPE = "yourmodule.yourcacheclass"
    """

    # =========================
    # BASIC
    # =========================
    CACHE_TYPE = os.getenv("CACHE_TYPE", "SimpleCache")
    CACHE_DEFAULT_TIMEOUT = 300
    CACHE_THRESHOLD = 500
    CACHE_IGNORE_ERRORS = True
    CACHE_KEY_PREFIX = "myapp_"

    """ # =========================
    # REDIS (production)
    # =========================
    CACHE_REDIS_HOST = "localhost"
    CACHE_REDIS_PORT = 6379
    CACHE_REDIS_DB = 0
    CACHE_REDIS_PASSWORD = None
    CACHE_REDIS_URL = "redis://localhost:6379/0"
    CACHE_REDIS_SOCKET_TIMEOUT = 5
    CACHE_REDIS_CONNECT_TIMEOUT = 5 """

    """ # =========================
    # OPTIONAL (FileSystemCache support (aktifkan kalau pakai ini))
    # =========================
    CACHE_DIR = CACHE_PATH
    CACHE_NO_NULL_WARNING = True """


def init_cache(app):

    # =========================================================
    # SAFE RUNTIME HOOK (tidak jalan saat import)
    # =========================================================
    if CacheConfig.CACHE_TYPE == "FileSystemCache":
        ensure_cache_dir()

    app.config.from_object(CacheConfig)
    cache.init_app(app)