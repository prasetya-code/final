from flask import Blueprint, render_template

from extension.flask_cache import cache


main_bp = Blueprint('main', __name__)


# =========================
# APP ROUTES
# =========================

@main_bp.route("/")
@cache.cached(timeout=60, response_filter=lambda r: r.status_code == 200)
def index():
    return render_template("app/index.html")


# =========================
# ERROR HANDLER
# =========================

@main_bp.app_errorhandler(429)
def ratelimit_handler(e):
    return render_template("error/429.html"), 429


@main_bp.app_errorhandler(405)
def method_not_allowed_handler(e):
    return "Method Not Allowed", 405