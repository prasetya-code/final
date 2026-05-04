# Cache

| Kebutuhan                          | Pakai ini           |
| ---------------------------------- | ------------------- |
| API pakai query (`?page=1`)        | `query_string=True` |
| Data beda tiap user                | `make_cache_key`    |
| Jangan cache saat kondisi tertentu | `unless`            |
| Jangan cache error                 | `response_filter`   |
| Mau nama cache sendiri             | `key_prefix`        |

## Contoh penerapan praktis

1. API dengan query (query_string=True)
```py
@cache.cached(timeout=60, query_string=True)
def api_data():
    return {"data": "ok"}
```

2. Cache per user (make_cache_key=function)
```py
from flask import request

def user_key():
    return f"user_{request.args.get('user_id')}"

@cache.cached(timeout=60, make_cache_key=user_key)
def profile():
    return {"profile": "user data"}
```

3. Jangan cache kalau user login (unless=lambda: )
```py
from flask_login import current_user

@cache.cached(timeout=60, unless=lambda: current_user.is_authenticated)
def home():
    return "public page"
```

4. Hindari cache error (response_filter=lambda r: r.status_code == 200)
```py
@cache.cached(
    timeout=60,
    response_filter=lambda r: r.status_code == 200
)
def api_safe():
    return {"data": "aman"}
```

5. Custom nama cache (key_prefix=)
```py
@cache.cached(timeout=60, key_prefix="homepage")
def index():
    return "home"
```

# NOTE

> Terapkan extension **python-json-logger** untuk centralized log agar bisa ➡️ **production-grade logging**

## Yang murni HTTP response header

1. transport.py → Strict-Transport-Security
2. isolation.py → Cross-Origin-Opener-Policy, Cross-Origin-Embedder-Policy, Cross-Origin-Resource-Policy
3. browser.py → X-Content-Type-Options, X-Frame-Options, Permissions-Policy, Referrer-Policy
4. csp.py → Content-Security-Policy
5. cors.py → Access-Control-Allow-Origin, Access-Control-Allow-Methods, dll
6. hardening.py → X-Permitted-Cross-Domain-Policies, Server, Accept-CH, dll
7. caching.py → Cache-Control
8. api.py → membersihkan header yang tidak perlu


## Yang bukan murni header

1. cookie_policy.py — header Set-Cookie memang ada, tapi atribut Secure, HttpOnly, SameSite itu bagian dari nilai header tersebut, bukan header tersendiri. Dan di sisi Flask, konfigurasinya lewat app.config, bukan langsung tulis header.

2. subresource_integrity.py — sama sekali tidak bermain di header. SRI bekerja di atribut HTML tag <script integrity="..."> dan <link integrity="...">. Browser yang memeriksa hash file CDN sebelum dieksekusi.

3. csp_report_endpoint.py — ini adalah server-side handler, bukan header. Browser mengirim laporan POST ke endpoint ini berdasarkan instruksi report-uri di CSP header. Jadi endpoint ini adalah penerima, bukan yang mengirim header.

4. rate_limit.py — header RateLimit-* dan Retry-After adalah informasi tambahan untuk client, bukan policy enforcement. Enforcement-nya ada di logika aplikasi (Flask-Limiter), header hanya memberi tahu client tentang status limit mereka.

## Satu hal yang perlu dipahami
Header ini sifatnya advisory untuk browser — browser yang kooperatif (Chrome, Firefox, Safari) akan menaatinya. Tapi header ini tidak melindungi dari serangan server-to-server seperti request langsung via curl atau script, karena yang membaca dan menegakkan aturan hanya browser. Untuk proteksi di sisi server (rate limit, autentikasi, validasi input), itu domain yang berbeda dari security headers.