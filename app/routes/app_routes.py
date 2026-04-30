from flask import Blueprint, render_template

from app.extension.flask_cache import cache
from app.extension.flask_limit import limiter


main_bp = Blueprint('main', __name__)


# =========================
# APP ROUTES
# =========================

@main_bp.route("/", methods=["POST"])
@limiter.limit("5 per minute")
@cache.cached(timeout=60, response_filter=lambda r: getattr(r, "status_code", 200) == 200)
def index():
    return render_template("app/index.html")


# =========================
# ERROR HANDLER
# =========================

@main_bp.app_errorhandler(429)
def ratelimit_handler(e):
    return render_template("handler/429.html"), 429


@main_bp.app_errorhandler(405)
def method_not_allowed_handler(e):
    return render_template("handler/405.html"), 405