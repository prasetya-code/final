import redis
from redis.retry import Retry
from redis.backoff import ExponentialBackoff

import os, traceback, socket, threading, time
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
# HEALTH STATUS (GLOBAL)
# =========================
redis_health_status = {
    "cache": None,
    "limit": None,
}

# =========================
# HEALTH META (ADVANCED)
# =========================
redis_health_meta = {
    "cache": {
        "latency": None,
        "last_check": None,
        "fail_count": 0,
        "circuit_open": False,
    },
    "limit": {
        "latency": None,
        "last_check": None,
        "fail_count": 0,
        "circuit_open": False,
    }
}

# =========================
# CIRCUIT BREAKER CONFIG
# =========================
FAIL_THRESHOLD = 3   # gagal berapa kali → open circuit
RECOVERY_TIME = 10  # detik sebelum retry lagi


# =========================
# TIMEOUT (dalam detik)
# =========================
TIMEOUT = 5  #(recommended: normal range


REDIS_COMMON_CONFIG = {
    "socket_connect_timeout": TIMEOUT,
    "socket_timeout": TIMEOUT,

    # =========================
    # CONNECTION POOL
    # =========================
    "max_connections": 20,

    # =========================
    # RETRY STRATEGY (versi simpel)
    # =========================
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
# HEALTH CHECK (SINGLE)
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
        if _cache_client and is_alive(_cache_client):
            print("[REDIS CACHE] Using existing alive connection")
            return _cache_client

        print("[REDIS CACHE] Connecting...")

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
        if _limit_client and is_alive(_limit_client):
            print("[REDIS LIMIT] Using existing alive connection")
            return _limit_client

        print("[REDIS LIMIT] Connecting...")

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
# 🔥 ADVANCED HEALTH CHECK (LATENCY + CIRCUIT BREAKER)
# =========================
def check_redis_health(name, client_getter, key):
    try:
        meta = redis_health_meta[key]

        # =========================
        # CIRCUIT OPEN → SKIP
        # =========================
        if meta["circuit_open"]:
            now = time.time()

            if meta["last_check"] and (now - meta["last_check"] < RECOVERY_TIME):
                print(f"[REDIS {name}] Circuit OPEN → skip")
                redis_health_status[key] = False
                return

            print(f"[REDIS {name}] Circuit HALF-OPEN → retry")

        start = time.time()

        client = client_getter()

        if client is None:
            raise Exception("Client is None")

        client.ping()

        latency = (time.time() - start) * 1000

        # SUCCESS
        redis_health_status[key] = True
        meta["latency"] = round(latency, 2)
        meta["last_check"] = int(time.time())
        meta["fail_count"] = 0
        meta["circuit_open"] = False

        print(f"[REDIS {name}] UP ({meta['latency']} ms)")

    except Exception as e:
        print(f"[REDIS {name} ERROR] {e}")
        traceback.print_exc()

        meta = redis_health_meta[key]

        redis_health_status[key] = False
        meta["fail_count"] += 1
        meta["last_check"] = int(time.time())

        if meta["fail_count"] >= FAIL_THRESHOLD:
            meta["circuit_open"] = True
            print(f"[REDIS {name}] Circuit OPEN (fail={meta['fail_count']})")


# =========================
# 🔥 BACKGROUND HEALTH CHECK
# =========================
HEALTH_CHECK_INTERVAL = 10

def _health_loop():
    print("[REDIS HEALTH] Background thread started")

    while True:
        try:
            check_redis_health("CACHE", get_cache_redis, "cache")
            check_redis_health("LIMIT", get_limit_redis, "limit")

        except Exception as e:
            print(f"[REDIS HEALTH CRITICAL] {e}")
            traceback.print_exc()

        time.sleep(HEALTH_CHECK_INTERVAL)


def start_redis_health_check(global_redis=True):
    try:
        if not global_redis:
            print("[REDIS HEALTH] Disabled (GLOBAL_REDIS=False)")
            return

        print("[REDIS HEALTH] Starting background checker...")

        t = threading.Thread(target=_health_loop, daemon=True)
        t.start()

    except Exception as e:
        print(f"[REDIS HEALTH ERROR] Failed to start: {e}")
        traceback.print_exc()


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