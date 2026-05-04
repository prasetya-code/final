from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from .redis_client import is_limit_redis_available, REDIS_LIMIT_URL

import os, traceback

# =========================
# CONFIG
# =========================
DEFAULT = ["200 per day", "50 per hour"]
GET_REDIS_URL = REDIS_LIMIT_URL
KEY_PREFIX = os.getenv("LIMITER_KEY_PREFIX", "rl:")


# =========================
# KEY FUNCTION
# =========================
def default_key_func():
    try:
        return get_remote_address()
    
    except Exception as e:
        print(f"[LIMITER ERROR] Failed to get remote address: {e}")
        traceback.print_exc()
        return "unknown"


# =========================
# STORAGE DECISION
# =========================
def get_storage_uri():
    """
    Menentukan backend storage untuk rate limiter.

    Flow:
    - Jika Redis tersedia → gunakan Redis
    - Jika tidak → fallback ke memory

    Catatan:
    - memory:// hanya cocok untuk development / single process
    - tidak cocok untuk multi-worker (misalnya gunicorn)
    """
    try:
        if is_limit_redis_available():
            print("[LIMITER] Using Redis storage")
            return GET_REDIS_URL

        print("[LIMITER WARNING] Using memory storage fallback")
        return "memory://"

    except Exception as e:
        print(f"[LIMITER ERROR] Storage decision failed: {e}")
        traceback.print_exc()

        # fallback paksa
        return "memory://"


# =========================
# RATE LIMIT STRATEGY (Limiter(strategy=""))
# =========================
""" 1. "fixed-window"
   - Menghitung request dalam interval waktu tetap
   - Lebih ringan & sederhana
   - Bisa terjadi burst di awal window

2. "moving-window"
   - Sliding window (lebih akurat & adil)
   - Direkomendasikan untuk production

3. "sliding-window-counter"
   - Kombinasi fixed & moving window
   - Lebih efisien dengan akurasi cukup baik

Catatan:
- Gunakan "moving-window" untuk akurasi terbaik
- "fixed-window" cocok jika butuh performa tinggi
- Strategy ini optimal jika menggunakan Redis (shared storage) """


# =========================
# LIMITER INSTANCE
# =========================
# Instance limiter dibuat tanpa app (lazy init)
fl_limiter = Limiter(
    key_func=default_key_func,
    default_limits=DEFAULT,
    strategy="moving-window",  # akurat untuk rate limiting
    headers_enabled=True,      # tambahkan header X-RateLimit
    swallow_errors=True,       # tidak crash jika limiter error
    key_prefix=KEY_PREFIX,
)


# =========================
# INIT LIMITER
# =========================
def init_limiter(app):
    try:
        # Tentukan storage backend
        storage_uri = get_storage_uri()

        # Inject ke config Flask
        app.config["RATELIMIT_STORAGE_URI"] = storage_uri
        app.config["RATELIMIT_KEY_PREFIX"] = KEY_PREFIX
        app.config["RATELIMIT_SWALLOW_ERRORS"] = True

        # Init limiter
        fl_limiter.init_app(app)

        print(f"[LIMITER] Initialized with storage: {storage_uri}")

    except Exception as e:
        print(f"[LIMITER ERROR] Failed to initialize limiter: {e}")
        traceback.print_exc()

        # =========================
        # FALLBACK MANUAL
        # =========================
        try:
            print("[LIMITER] Falling back to memory storage (manual fallback)")

            app.config["RATELIMIT_STORAGE_URI"] = "memory://"

            fl_limiter.init_app(app)

        except Exception as fallback_error:
            print(f"[LIMITER CRITICAL] Fallback failed: {fallback_error}")
            traceback.print_exc()