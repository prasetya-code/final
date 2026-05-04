import redis
from redis.retry import Retry
from redis.backoff import ExponentialBackoff

import os, traceback, socket
from urllib.parse import urlparse


# =========================
# REDIS URL CONFIG
# =========================
REDIS_CACHE_URL = os.getenv("REDIS_CACHE_URL", "redis://localhost:6379/1")
REDIS_LIMIT_URL = os.getenv("REDIS_LIMIT_URL", "redis://localhost:6379/2")

# =========================
# GLOBAL CLIENT
# =========================
_cache_client = None
_limit_client = None

# =========================
# TIMEOUT (dalam detik)
# =========================
# Mengatur waktu maksimum untuk:
# - socket_connect_timeout → waktu untuk koneksi awal ke Redis
# - socket_timeout         → waktu tunggu response dari Redis
#
# Rekomendasi:
# - Sangat agresif : 1 - 2 detik
#   → cocok untuk system ultra cepat
#   → risiko: mudah timeout kalau network sedikit lambat
#
# - Agresif : 2 - 3 detik
#   → cocok untuk production cepat (low latency)
#
# - Normal (recommended) : 3 - 5 detik
#   → balance antara kecepatan & stabilitas
#   → cocok untuk sebagian besar aplikasi
#
# - Long / toleran : 5 - 10 detik
#   → cocok untuk network tidak stabil / cloud jauh
#   → risiko: response terasa lambat saat error
#
# Catatan:
# - Timeout terlalu kecil → sering gagal connect
# - Timeout terlalu besar → aplikasi terasa "hang" saat Redis down
#
TIMEOUT = 5  #(recommended: normal range


REDIS_COMMON_CONFIG = {
    "socket_connect_timeout": TIMEOUT,
    "socket_timeout": TIMEOUT,

    # =========================
    # CONNECTION POOL
    # =========================
    # max_connections:
    # - Membatasi jumlah koneksi ke Redis
    # - Penting untuk menghindari overload Redis server
    #
    # Tips:
    # - Sesuaikan dengan jumlah worker aplikasi
    # - Jangan terlalu besar jika Redis kecil
    "max_connections": 20,

    # =========================
    # RETRY STRATEGY (versi simpel)
    # =========================
    # retry:
    # - Akan mencoba ulang jika koneksi gagal
    #
    # Retry(..., 3):
    # - Maksimal 3 kali percobaan ulang
    #
    # ExponentialBackoff():
    # - Delay antar retry makin lama
    #
    # retry_on_timeout=True:
    # - Timeout juga akan dicoba ulang
    "retry": Retry(ExponentialBackoff(), 3),
    "retry_on_timeout": True,
}


# =========================
# DEBUG: PARSE REDIS URL
# =========================
def debug_redis_url(url):
    try:
        parsed = urlparse(url)

        print("[REDIS DEBUG] Parsed URL:")
        print(f"  - scheme : {parsed.scheme}")
        print(f"  - host   : {parsed.hostname}")
        print(f"  - port   : {parsed.port}")
        print(f"  - db     : {parsed.path}")

    except Exception as e:
        print(f"[REDIS DEBUG ERROR] Failed to parse URL: {e}")
        traceback.print_exc()


# =========================
# DEBUG: CHECK PORT
# =========================
def debug_check_port(host, port):
    try:
        print(f"[REDIS DEBUG] Checking connection to {host}:{port} ...")

        s = socket.socket()
        s.settimeout(2)
        s.connect((host, port))

        print("[REDIS DEBUG] Port is OPEN ✅")
        s.close()

    except Exception as e:
        print(f"[REDIS DEBUG] Port is CLOSED ❌: {e}")
        traceback.print_exc()


# =========================
# HEALTH CHECK
# =========================
def is_alive(client):
    try:
        client.ping()
        return True

    except Exception as e:
        print(f"[REDIS WARNING] Client not alive: {e}")
        traceback.print_exc()
        return False


# =========================
# CREATE CLIENT
# =========================
def create_client(url):
    try:
        print(f"[REDIS] Creating client for {url}")

        # Debug URL
        debug_redis_url(url)

        client = redis.Redis.from_url(url, **REDIS_COMMON_CONFIG)
        return client

    except Exception as e:
        print(f"[REDIS ERROR] Failed to create client: {e}")
        traceback.print_exc()
        return None


# =========================
# CACHE REDIS
# =========================
def get_cache_redis():
    global _cache_client

    try:
        # Gunakan client jika masih valid
        if _cache_client and is_alive(_cache_client):
            print("[REDIS CACHE] Using existing alive connection")
            return _cache_client

        print("[REDIS CACHE] Connecting...")

        # Debug koneksi
        parsed = urlparse(REDIS_CACHE_URL)
        debug_check_port(parsed.hostname, parsed.port)

        client = create_client(REDIS_CACHE_URL)

        if client is None:
            print("[REDIS CACHE] Client creation failed")
            return None

        print("[REDIS CACHE] Pinging server...")
        client.ping()

        print("[REDIS CACHE] Connected successfully ✅")

        _cache_client = client
        return _cache_client

    except Exception as e:
        print(f"[REDIS CACHE ERROR] Connection failed: {e}")
        traceback.print_exc()

        _cache_client = None
        return None


# =========================
# LIMIT REDIS
# =========================
def get_limit_redis():
    global _limit_client

    try:
        # Gunakan client jika masih valid
        if _limit_client and is_alive(_limit_client):
            print("[REDIS LIMIT] Using existing alive connection")
            return _limit_client

        print("[REDIS LIMIT] Connecting...")

        # Debug koneksi
        parsed = urlparse(REDIS_LIMIT_URL)
        debug_check_port(parsed.hostname, parsed.port)

        client = create_client(REDIS_LIMIT_URL)

        if client is None:
            print("[REDIS LIMIT] Client creation failed")
            return None

        print("[REDIS LIMIT] Pinging server...")
        client.ping()

        print("[REDIS LIMIT] Connected successfully ✅")

        _limit_client = client
        return _limit_client

    except Exception as e:
        print(f"[REDIS LIMIT ERROR] Connection failed: {e}")
        traceback.print_exc()

        _limit_client = None
        return None


# =========================
# AVAILABILITY CHECK
# =========================
def is_cache_redis_available():
    try:
        return get_cache_redis() is not None

    except Exception as e:
        print(f"[REDIS CACHE CHECK ERROR] {e}")
        traceback.print_exc()
        return False


def is_limit_redis_available():
    try:
        return get_limit_redis() is not None

    except Exception as e:
        print(f"[REDIS LIMIT CHECK ERROR] {e}")
        traceback.print_exc()
        return False