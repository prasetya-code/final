from flask import g, request

import secrets, re

# 32 bytes = 256-bit entropy (rekomendasi W3C CSP Level 3)
NONCE_BYTES = 32

# Prefix route API yang tidak perlu nonce
API_PATH_PREFIXES = ("/api/", "/api")

# Validasi format nonce (URL-safe base64: A-Z a-z 0-9 - _)
_NONCE_PATTERN = re.compile(r"^[A-Za-z0-9\-_]+$")


def generate_nonce() -> str:
    return secrets.token_urlsafe(NONCE_BYTES)


def attach_nonce() -> None:
    """
    Before-request hook untuk generate CSP nonce per request.
    Hanya untuk non-API.

    Cara daftarkan:
        app.before_request(attach_nonce)
    """
    if not request.path.startswith(API_PATH_PREFIXES):
        g.csp_nonce = generate_nonce()


def get_nonce() -> str | None:
    """Ambil nonce dari request context. Return None jika tidak tersedia."""
    return getattr(g, "csp_nonce", None)


def is_valid_nonce(value: str) -> bool:
    """Validasi format nonce sebelum digunakan."""
    if not value or not isinstance(value, str):
        return False
    
    if not 22 <= len(value) <= 86:
        return False
    
    return bool(_NONCE_PATTERN.match(value))


def init_nonce(app) -> None:
    """
    Daftarkan nonce ke Flask app sekaligus:
        - before_request hook untuk generate nonce tiap request
        - Jinja2 global agar {{ get_nonce() }} bisa dipakai di template

    Cara pakai:
        from nonce import init_nonce
        init_nonce(app)
    """
    app.before_request(attach_nonce)
    app.jinja_env.globals["get_nonce"] = get_nonce