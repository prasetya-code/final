from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os


DEFAULT_LIMIT = ["200 per day", "50 per hour"]


# =========================
# KEY FUNCTION (IDENTITY)
# =========================
def default_key_func():
    return get_remote_address()


# =========================
# STORAGE SELECTION (SCALABLE + FALLBACK)
# =========================
def get_storage_uri():
    """
    Prioritas:
    1. Redis (production)
    2. Memory (fallback / dev)
    """

    redis_url = os.getenv("LIMITER_REDIS_URL")

    if redis_url:
        try:
            # simple validation attempt (optional safe guard)
            if redis_url.startswith("redis://"):
                return redis_url
        except Exception:
            pass

    # fallback default
    return "memory://"


# =========================
# INIT LIMITER
# =========================

"""
LIMITER CONFIG OPTIONS (Flask-Limiter)

1. key_func
- Fungsi untuk menentukan identitas user yang dikenai limit
- Default: get_remote_address (IP address client)
- ✔ cocok: simple API / public endpoint
- ❗ bisa diganti ke user_id untuk sistem login


2. default_limits
- Limit global untuk semua endpoint
- ✔ cocok: baseline protection API
- contoh:
    ["200 per day", "50 per hour"]


3. storage_uri
- Tempat penyimpanan data hit request
- Redis:
    - ✔ production scalable
    - ✔ multi instance / load balancer

- memory://
    - ✔ fallback dev
    - ❌ tidak persistent


4. strategy
- Cara menghitung rate limit
- "moving-window"
    - ✔ lebih smooth & akurat
    - ✔ cocok production


5. headers_enabled
- Menambahkan header rate limit:
    - X-RateLimit-Limit
    - X-RateLimit-Remaining
    - X-RateLimit-Reset


6. swallow_errors
- Jika True:
    - app tidak crash saat storage error
    - limiter fallback ke behavior default
"""

limiter = Limiter(
    key_func=default_key_func,
    default_limits=DEFAULT_LIMIT,
    storage_uri=get_storage_uri(),
    strategy="moving-window",
    headers_enabled=True,
    swallow_errors=True
)