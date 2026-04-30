from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from functools import wraps
import os, redis


# =========================
# CONFIG
# =========================
DEFAULT_LIMITS = ["200 per day", "50 per hour"]

REDIS_URL = os.getenv("LIMITER_REDIS_URL", "redis://localhost:6379/0")
KEY_PREFIX = os.getenv("LIMITER_KEY_PREFIX", "rl:")


# =========================
# KEY FUNCTION
# =========================
def default_key_func():
    return get_remote_address()


# =========================
# STORAGE
# =========================
def get_storage_uri():
    try:
        if REDIS_URL.startswith("redis://") or REDIS_URL.startswith("rediss://"):
            client = redis.Redis.from_url(
                REDIS_URL,

                # REDIS CHECK
                socket_connect_timeout=2,
                socket_timeout=2,
            )
            client.ping()

            print("[LIMITER] Redis connected")
            return REDIS_URL

    except Exception as e:
        print(f"[LIMITER WARNING] Redis failed, fallback memory: {e}")

    return "memory://"


# =========================
# LIMITER INSTANCE
# =========================
limiter = Limiter(
    key_func=default_key_func,
    default_limits=DEFAULT_LIMITS,
    storage_uri=get_storage_uri(),
    strategy="moving-window",
    headers_enabled=True,
    swallow_errors=True,
    key_prefix=KEY_PREFIX,
)


# =========================
# ENDPOINT LIMITS
# =========================
ENDPOINT_LIMITS = {
    "main.index": ["20 per minute", "150 per hour"],
    "main.about": ["15 per minute", "100 per hour"],
    "main.project": ["15 per minute", "100 per hour"],
    "debug.health": ["5 per minute", "20 per hour"],
}


# =========================
# DECORATOR
# =========================
def apply_limits(key):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        limited = wrapper

        for limit in reversed(ENDPOINT_LIMITS.get(key, [])):
            limited = limiter.limit(limit)(limited)

        return limited

    return decorator


# =========================
# ERROR HANDLER
# =========================
def rate_limit_exceeded(e):
    print(f"[SECURITY] Rate limit exceeded: {e.description}")

    return {
        "error": "Too many requests",
        "message": "Rate limit exceeded"
    }, 429


# =========================
# INIT LIMITER
# =========================
def init_limiter(app):
    env = app.config.get("ENV", "production")

    # =========================
    # DEV MODE
    # =========================
    if env == "development":
        print("[LIMITER] Disabled in development mode")
        limiter.enabled = False
        limiter.init_app(app)
        return

    storage_uri = get_storage_uri()

    app.config["RATELIMIT_STORAGE_URI"] = storage_uri
    app.config["RATELIMIT_KEY_PREFIX"] = KEY_PREFIX
    app.config["RATELIMIT_SWALLOW_ERRORS"] = True

    limiter.init_app(app)

    app.register_error_handler(429, rate_limit_exceeded)

    print(f"[LIMITER] Initialized with storage: {storage_uri}")