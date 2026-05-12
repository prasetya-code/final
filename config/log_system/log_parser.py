import os

from .rotate_parser import setup_logger

# =========================================================
# BASE FIELDS
# =========================================================

BASE_FIELDS = [
    "asctime",
    "levelname",
    "name",
    "message",
    "request_id",
    "client_ip",
    "filename",
    "funcName",
    "lineno",
]

# =========================================================
# ACCESS LOGGER FIELDS
# =========================================================

ACCESS_FIELDS = BASE_FIELDS + [
    "city",
    "country",
    "lat",
    "lon",
    "source",
    "confidence",
    "method",
    "path",
    "query_string",
    "http_version",
    "referer",
    "status_code",
    "bytes_sent",
    "response_time",
    "host",
    "device",
    "os",
    "browser",
]

# =========================================================
# APP LOGGER FIELDS
# =========================================================

APP_FIELDS = BASE_FIELDS + [
    "environment",
    "app_version",
    "hostname",
    "pid",
    "tid",
    "method",
    "url",
    "status_code",
    "response_time",
]

# =========================================================
# SECURITY LOGGER FIELDS
# =========================================================

SECURITY_FIELDS = BASE_FIELDS + [
    "event_type",
    "threat_type",
    "severity",
    "auth_user",
    "auth_method",
    "login_result",
    "blocked",
    "method",
    "url",
    "status_code",
    "city",
    "country",
    "lat",
    "lon",
    "source",
    "confidence",
    "user_agent",
    "log_hash",
]

# =========================================================
# DEFAULT EXTRA VALUES
# =========================================================

DEFAULT_EXTRA = {
    "request_id": None,
    "client_ip": None,
    "city": None,
    "country": None,
    "lat": None,
    "lon": None,
    "source": None,
    "confidence": None,
    "method": None,
    "path": None,
    "query_string": None,
    "http_version": None,
    "referer": None,
    "status_code": None,
    "bytes_sent": None,
    "response_time": None,
    "host": None,
    "device": None,
    "os": None,
    "browser": None,
    "environment": None,
    "app_version": None,
    "hostname": None,
    "pid": os.getpid(),
    "tid": None,
    "url": None,
    "event_type": None,
    "threat_type": None,
    "severity": None,
    "auth_user": None,
    "auth_method": None,
    "login_result": None,
    "blocked": None,
    "user_agent": None,
    "log_hash": None,
}

# =========================================================
# CENTRALIZED LOGGERS
# =========================================================

app_logger = setup_logger(
    logger_name="APP",
    fields=APP_FIELDS
)

access_logger = setup_logger(
    logger_name="ACCESS",
    fields=ACCESS_FIELDS
)

security_logger = setup_logger(
    logger_name="SECURITY",
    fields=SECURITY_FIELDS
)