from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from .redis_client import is_redis_available

import os

# =========================
# CONFIG
# =========================
DEFAULT = ["200 per day", "50 per hour"]

REDIS_URL = os.getenv("LIMITER_REDIS_URL", "redis://localhost:6379/1")
KEY_PREFIX = os.getenv("LIMITER_KEY_PREFIX", "rl:")


# =========================
# KEY FUNCTION
# =========================
def default_key_func():
    return get_remote_address()


# =========================
# STORAGE DECISION
# =========================
def get_storage_uri():
    if is_redis_available():
        print("[LIMITER] Using Redis storage")
        return REDIS_URL

    print("[LIMITER WARNING] Using memory storage fallback")
    return "memory://"


# =========================
# LIMITER INSTANCE
# =========================
limiter = Limiter(
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
    storage_uri = get_storage_uri()

    app.config["RATELIMIT_STORAGE_URI"] = storage_uri
    app.config["RATELIMIT_KEY_PREFIX"] = KEY_PREFIX
    app.config["RATELIMIT_SWALLOW_ERRORS"] = True

    limiter.init_app(app)

    print(f"[LIMITER] Initialized with storage: {storage_uri}")