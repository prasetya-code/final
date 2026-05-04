from flask import Blueprint, jsonify, current_app
from ..extension.redis_client import redis_health_status, redis_health_meta

import os, time

# =========================
# BLUEPRINT
# =========================
monitor_bp = Blueprint("monitor", __name__)


# =========================
# CONFIG
# =========================
START_TIME = time.time()
APP_NAME = os.getenv("APP_NAME", "my-app")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")


# =========================
# HELPER
# =========================
def get_uptime():
    return int(time.time() - START_TIME)


def get_status(value):
    """
    Convert:
    True  → "up"
    False → "down"
    None  → "unknown"
    """
    if value is True:
        return "up"
    if value is False:
        return "down"
    return "unknown"


def build_dependency(name, key):
    """
    Build detail dependency response
    """
    status = get_status(redis_health_status.get(key))
    meta = redis_health_meta.get(key, {})

    return {
        "status": status,
        "latency_ms": meta.get("latency"),
        "last_check": meta.get("last_check"),
        "fail_count": meta.get("fail_count"),
        "circuit_open": meta.get("circuit_open"),
    }


# =========================
# REDIS STATUS BUILDER
# =========================
def build_redis_response():
    global_redis = current_app.config.get("GLOBAL_REDIS", True)

    # =========================
    # CASE 1: REDIS DISABLED
    # =========================
    if not global_redis:
        dependencies = {
            "redis_cache": {
                "status": "disabled",
                "message": "Redis cache is disabled via GLOBAL_REDIS"
            },
            "redis_limiter": {
                "status": "disabled",
                "message": "Redis limiter is disabled via GLOBAL_REDIS"
            }
        }

        return {
            "status": "degraded",
            "mode": "no-redis",
            "reason": "Redis is globally disabled",
            "redis_enabled": False,

            "service": APP_NAME,
            "version": APP_VERSION,
            "uptime": get_uptime(),

            "dependencies": dependencies
        }, 200

    # =========================
    # CASE 2: REDIS ENABLED
    # =========================
    cache_dep = build_dependency("CACHE", "cache")
    limit_dep = build_dependency("LIMIT", "limit")

    dependencies = {
        "redis_cache": cache_dep,
        "redis_limiter": limit_dep
    }

    cache_status = cache_dep["status"]
    limit_status = limit_dep["status"]

    # =========================
    # OVERALL STATUS LOGIC
    # =========================
    overall = "up"
    reason = "All systems operational"

    if "down" in [cache_status, limit_status]:
        overall = "degraded"
        reason = "One or more Redis services are down"

    if "unknown" in [cache_status, limit_status]:
        overall = "degraded"
        reason = "Redis health status not ready"

    # 🔥 BONUS: circuit breaker awareness
    if cache_dep["circuit_open"] or limit_dep["circuit_open"]:
        overall = "degraded"
        reason = "Circuit breaker active (Redis unstable)"

    # =========================
    # HTTP STATUS
    # =========================
    http_code = 200 if overall != "down" else 500

    return {
        "status": overall,
        "mode": "redis",
        "reason": reason,
        "redis_enabled": True,

        "service": APP_NAME,
        "version": APP_VERSION,
        "uptime": get_uptime(),

        "dependencies": dependencies
    }, http_code


# =========================
# 🔥 CHECK REDIS (PRODUCTION)
# =========================
@monitor_bp.route("/check_redis", methods=["GET"])
def check_redis():
    try:
        response, code = build_redis_response()
        return jsonify(response), code

    except Exception as e:
        return jsonify({
            "status": "down",
            "error": str(e)
        }), 500


# =========================
# 🔍 DETAIL CHECK REDIS
# =========================
@monitor_bp.route("/check_redis/detail", methods=["GET"])
def check_redis_detail():
    try:
        response, code = build_redis_response()

        # Tambahan debug info
        response["timestamp"] = int(time.time())

        return jsonify(response), code

    except Exception as e:
        return jsonify({
            "status": "down",
            "error": str(e)
        }), 500