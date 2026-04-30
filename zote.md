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

> CDN sebaiknya di tidak di letakkan di base.html karena dia akan ikut ke load dan menambah beban load, kecuali memang butuh