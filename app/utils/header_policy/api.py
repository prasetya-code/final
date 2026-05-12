from .cors   import build_cors
from .cache  import build_cache


def build_api(response, *, allow_public: bool = False):
    """
    Menerapkan header khusus API response.
    Mencakup stealth, content negotiation, rate limiting, tracing, dan versioning.

    Header yang dikelola file ini:
      Server, X-Powered-By, X-Runtime, X-Generator  (stealth)
      Content-Type                                   (content negotiation)
      X-RateLimit-Limit, X-RateLimit-Remaining,
      X-RateLimit-Reset, Retry-After                 (rate limiting)
      X-Request-Id                                   (tracing)
      X-API-Version, Deprecation, Sunset             (versioning)

    Didelegasikan ke file lain:
      cache.py  → Cache-Control, Pragma, Expires
      cors.py   → semua header Access-Control-*

    Header browser (hardening, CSP, transport, isolation)
    TIDAK diset di sini — gunakan browser_privacy() untuk halaman HTML.

    Parameter:
    → allow_public=False : API hanya untuk frontend same-origin (default)
    → allow_public=True  : API terbuka untuk pihak ketiga / publik
    """

    # =========================================================
    # STEALTH & ANTI-FINGERPRINTING
    # Menyembunyikan identitas stack teknologi dari response header.
    # Informasi ini biasa dipakai penyerang untuk reconnaissance
    # sebelum melancarkan serangan yang ditargetkan.
    # =========================================================

    # Server — identitas software web server
    # → default bawaan  : "Werkzeug/3.0.1 Python/3.12.2" / "gunicorn/21.2.0" / "nginx/1.25.3"
    # → stealth         : ganti dengan nilai generik tanpa versi (pilihan kami)
    # ⚠ Nilai kosong "" kadang tidak dikirim oleh beberapa framework —
    #   gunakan nilai generik sebagai gantinya agar header tetap terkirim.
    response.headers["Server"] = "webserver"

    # X-Powered-By — framework atau runtime yang dipakai
    # → default bawaan  : "Express", "PHP/8.2", "ASP.NET"
    # → stealth         : hapus header ini sama sekali (pilihan kami)
    response.headers.pop("X-Powered-By", None)

    # X-Runtime — durasi eksekusi request di server (ms)
    # → default bawaan  : "0.123" — dikirim Rails, Laravel, dan beberapa framework lain
    # → stealth         : hapus agar tidak bocorkan info timing internal server
    response.headers.pop("X-Runtime", None)

    # X-Generator — CMS atau generator halaman yang dipakai
    # → default bawaan  : "WordPress 6.4", "Drupal 10", "Jekyll"
    # → stealth         : hapus header ini (pilihan kami)
    response.headers.pop("X-Generator", None)

    # =========================================================
    # CONTENT NEGOTIATION
    # Mendeklarasikan format dan encoding body response secara eksplisit
    # agar client tidak perlu menebak dan tidak bisa di-sniff browser.
    # =========================================================

    # Content-Type — format body response beserta encoding karakter
    # → application/json; charset=utf-8  : JSON UTF-8 (pilihan kami)
    # → application/xml; charset=utf-8   : XML
    # → text/plain; charset=utf-8        : plain text
    # → application/octet-stream         : binary / file download
    # ⚠ Selalu sertakan charset=utf-8 agar browser tidak menebak encoding sendiri
    #   dan untuk mencegah serangan UTF-7 / charset sniffing di browser lama.
    response.headers["Content-Type"] = "application/json; charset=utf-8"

    # Cache dikelola di cache.py
    build_cache(response)

    # CORS dikelola di cors.py
    build_cors(response, allow_public=allow_public)

    # =========================================================
    # RATE LIMITING
    # Menginformasikan client tentang kuota request yang berlaku.
    # Membantu client throttle sendiri sebelum kena 429.
    #
    # ⚠ Nilai di sini hanya placeholder — wajib diisi dinamis
    #   dari sistem rate limiter (Redis, middleware, dsb).
    # =========================================================

    # X-RateLimit-Limit — total request yang diizinkan dalam satu window waktu
    # → nilai    : integer, contoh "1000" artinya 1000 request per jam
    # → dinamis  : ambil dari rate limiter, bukan hardcode
    response.headers["X-RateLimit-Limit"] = "1000"

    # X-RateLimit-Remaining — sisa kuota request yang masih boleh dilakukan
    # → nilai    : integer yang berkurang setiap request
    # → dinamis  : wajib diisi dari rate limiter per request
    response.headers["X-RateLimit-Remaining"] = "999"

    # X-RateLimit-Reset — waktu reset window kuota dalam Unix timestamp (epoch detik)
    # → nilai    : integer epoch, contoh "1735689600"
    # → dinamis  : wajib diisi dari rate limiter
    # → client bisa hitung: kapan boleh request lagi = Reset - now()
    response.headers["X-RateLimit-Reset"] = "0"

    # Retry-After — berapa detik client harus tunggu sebelum boleh retry
    # → nilai    : integer detik, contoh "60"
    # → dikirim  : hanya saat status 429 Too Many Requests atau 503 Service Unavailable
    # → format   : detik (integer) atau HTTP-date ("Wed, 21 Oct 2025 07:28:00 GMT")
    # ⚠ Aktifkan hanya di error handler 429/503, bukan di setiap response.
    # response.headers["Retry-After"] = "60"

    # =========================================================
    # REQUEST TRACING
    # ID unik per request untuk debugging, logging terpusat,
    # dan korelasi lintas service di arsitektur microservice.
    # =========================================================

    # X-Request-Id — ID unik yang mewakili satu siklus request-response
    # → format   : UUID v4, contoh "550e8400-e29b-41d4-a716-446655440000"
    # → dinamis  : wajib diisi dari middleware tracing, bukan hardcode
    # → manfaat  : client lampirkan ID ini saat laporan bug untuk korelasi log
    # ⚠ Aktifkan baris di bawah setelah middleware tracing tersedia.
    # response.headers["X-Request-Id"] = generate_request_id()

    # =========================================================
    # API VERSIONING
    # Menginformasikan versi API yang aktif melayani request ini.
    # Membantu client deteksi versi tanpa harus parse URL atau body.
    # =========================================================

    # X-API-Version — versi API yang sedang aktif
    # → format   : semantic versioning "MAJOR.MINOR.PATCH"
    # → ganti    : sesuaikan dengan versi API yang sedang berjalan
    response.headers["X-API-Version"] = "1.0.0"

    # Deprecation — RFC 9745, menandai endpoint yang akan segera dihentikan
    # → format   : HTTP-date "Sat, 01 Jan 2026 00:00:00 GMT"
    # → dikirim  : hanya untuk endpoint yang sudah masuk fase deprecation
    # response.headers["Deprecation"] = "Sat, 01 Jan 2026 00:00:00 GMT"

    # Sunset — RFC 8594, tanggal pasti endpoint dihentikan total
    # → format   : HTTP-date "Sat, 01 Jul 2026 00:00:00 GMT"
    # → dikirim  : bersama Deprecation agar client tahu deadline migrasi
    # response.headers["Sunset"] = "Sat, 01 Jul 2026 00:00:00 GMT"

    return response