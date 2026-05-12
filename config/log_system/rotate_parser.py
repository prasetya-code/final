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

