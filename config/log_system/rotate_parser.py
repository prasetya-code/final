import os, logging

from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

from pythonjsonlogger import jsonlogger

# =========================================================
# LOG DIRECTORY
# =========================================================

LOG_DIR = "logs"

os.makedirs(LOG_DIR, exist_ok=True)

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
# LOGGER SETUP
# =========================================================

def setup_logger(
    logger_name,
    fields,
    level=logging.INFO
):

    # =====================================================
    # LOGGER
    # =====================================================

    logger = logging.getLogger(logger_name)

    logger.setLevel(level)

    logger.propagate = False

    # =====================================================
    # AVOID DUPLICATE HANDLER
    # =====================================================

    if not logger.handlers:

        # =================================================
        # DATE FORMAT
        # =================================================

        current_date = datetime.now().strftime("%Y-%m-%d")

        # =================================================
        # FILE FORMAT
        # =================================================

        log_filename = (f"{logger_name.lower()}_{current_date}.log")

        # =================================================
        # FULL LOG PATH
        # =================================================

        log_path = os.path.join(
            LOG_DIR,
            log_filename
        )

        # =================================================
        # ROTATING HANDLER
        # =================================================

        handler = TimedRotatingFileHandler(
            filename=log_path,
            when="midnight",
            interval=1,
            backupCount=30,
            encoding="utf-8"
        )

        # =================================================
        # JSON FORMATTER
        # =================================================

        formatter = jsonlogger.JsonFormatter(
            "%(asctime)s %(levelname)s %(name)s %(message)s "
            + " ".join([
                f"%({field})s"
                for field in fields
            ])
        )

        handler.setFormatter(formatter)

        # =================================================
        # AUTO FLUSH
        # =================================================

        handler.flush = handler.stream.flush

        # =================================================
        # ADD HANDLER
        # =================================================

        logger.addHandler(handler)

    return logger

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

# =========================================================
# EXAMPLE APP LOG
# =========================================================

app_logger.info(
    "Application started",
    extra={
        **DEFAULT_EXTRA,

        "request_id": "REQ-001",
        "client_ip": "127.0.0.1",

        "environment": "production",
        "app_version": "1.0.0",
        "hostname": "server-01",

        "tid": 1001,

        "method": "GET",
        "url": "/",

        "status_code": 200,
        "response_time": 10,
    }
)

# =========================================================
# EXAMPLE ACCESS LOG
# =========================================================

access_logger.info(
    "Incoming request",
    extra={
        **DEFAULT_EXTRA,

        "request_id": "REQ-002",
        "client_ip": "192.168.1.1",

        "city": "Bandung",
        "country": "Indonesia",

        "lat": "-6.9",
        "lon": "107.6",

        "source": "maxmind",
        "confidence": "high",

        "method": "GET",
        "path": "/login",

        "query_string": "next=dashboard",

        "http_version": "HTTP/1.1",

        "referer": "https://google.com",

        "status_code": 200,

        "bytes_sent": 2048,

        "response_time": 35,

        "host": "example.com",

        "device": "Desktop",
        "os": "Windows",
        "browser": "Chrome",
    }
)

# =========================================================
# EXAMPLE SECURITY LOG
# =========================================================

security_logger.warning(
    "Rate limit exceeded",
    extra={
        **DEFAULT_EXTRA,

        "request_id": "REQ-003",
        "client_ip": "10.0.0.1",

        "event_type": "RATE_LIMIT",
        "threat_type": "BRUTE_FORCE",
        "severity": "HIGH",

        "auth_user": "admin",
        "auth_method": "PASSWORD",

        "login_result": "FAILED",

        "blocked": True,

        "method": "POST",
        "url": "/admin/login",

        "status_code": 429,

        "city": "Jakarta",
        "country": "Indonesia",

        "lat": "-6.2",
        "lon": "106.8",

        "source": "ipapi",
        "confidence": "medium",

        "user_agent": "Mozilla/5.0",

        "log_hash": "abc123xyz",
    }
)