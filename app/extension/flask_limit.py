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
# ENV CONTROL (SECONDARY)
# =========================
# Change val env (str) into boolean (TRUE / FALSE)
USE_REDIS_LIMITER = os.getenv("USE_REDIS_LIMITER", "true").lower() == "true"


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
fl_limiter = Limiter(
    key_func=default_key_func,
    default_limits=DEFAULT,
    strategy="moving-window",
    headers_enabled=True,
    swallow_errors=True,
    key_prefix=KEY_PREFIX,
)


# =========================
# INIT LIMITER
# =========================
def init_limiter(app):
    try:
        # =========================
        # GLOBAL CONTROL (MASTER SWITCH)
        # =========================
        global_redis = app.config.get("GLOBAL_REDIS", True)

        # print(f"[LIMITER] GLOBAL_REDIS = {global_redis}")
        print(f"[LIMITER] ENV USE_REDIS_LIMITER = {USE_REDIS_LIMITER}")

        # =========================
        # STORAGE DECISION
        # =========================
        # PRIORITY:
        # 1. GLOBAL_REDIS
        # 2. ENV (USE_REDIS_LIMITER)
        # 3. Redis availability
        #
        if not global_redis:
            print("[LIMITER] Disabled Redis")
            storage_uri = "memory://"

        elif not USE_REDIS_LIMITER:
            print("[LIMITER] Disabled via ENV → using memory storage")
            storage_uri = "memory://"

        else:
            print("[LIMITER] Checking Redis availability...")

            if is_limit_redis_available():
                print("[LIMITER] Using Redis storage")
                storage_uri = GET_REDIS_URL
            else:
                print("[LIMITER WARNING] Redis not available → fallback to memory")
                storage_uri = "memory://"

        # =========================
        # APPLY CONFIG
        # =========================
        app.config["RATELIMIT_STORAGE_URI"] = storage_uri
        app.config["RATELIMIT_KEY_PREFIX"] = KEY_PREFIX
        app.config["RATELIMIT_SWALLOW_ERRORS"] = True

        # =========================
        # INIT LIMITER
        # =========================
        fl_limiter.init_app(app)

        print(f"[LIMITER] Initialized with storage: {storage_uri} \n")

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