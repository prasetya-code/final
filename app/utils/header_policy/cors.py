def build_cors(response, *, allow_public: bool = False):
    """
    Menerapkan header CORS (Cross-Origin Resource Sharing).
    Mengontrol browser mana yang boleh mengakses resource ini
    dari halaman yang berbeda origin.

    Cara kerja CORS:
      Browser kirim request cross-origin → server balas dengan header CORS
      → browser baca header → izinkan atau blokir response ke JS client
      Untuk request kompleks (POST JSON, custom header) → browser kirim
      preflight OPTIONS dulu → server balas → browser lanjut request asli

    Parameter:
    → allow_public=False : hanya untuk frontend same-origin (default)
    → allow_public=True  : terbuka untuk pihak ketiga / publik
    """

    if not allow_public:
        # Same-origin tidak butuh CORS header sama sekali.
        # Browser secara default izinkan semua request ke same-origin.
        return response

    # =========================================================
    # ORIGIN
    # =========================================================

    # Access-Control-Allow-Origin — origin mana yang boleh mengakses resource ini
    # → *                      : semua origin (pilihan kami untuk publik)
    # → https://domain.com     : satu origin spesifik
    # → (dinamis dari request) : cocokkan dengan whitelist origin yang diizinkan
    # ⚠ Nilai "*" tidak bisa dikombinasikan dengan Allow-Credentials: true.
    #   Jika butuh credentials (cookie, auth header), ganti "*" dengan origin spesifik.
    ALLOW_ORIGIN = [
        "*",
        # "https://app.domain.com",   # aktifkan jika ingin batasi origin spesifik
        # "https://partner.com",
    ]

    # Access-Control-Allow-Credentials — izinkan browser kirim credentials cross-origin
    # → true  : izinkan cookie, Authorization header, TLS client certificate
    # → false : tidak izinkan (default browser) — cukup hapus header ini
    # ⚠ Hanya aktifkan jika benar-benar dibutuhkan.
    #   Wajib kombinasikan dengan ALLOW_ORIGIN spesifik (bukan "*").
    ALLOW_CREDENTIALS = False

    # =========================================================
    # PREFLIGHT REQUEST
    # Browser kirim OPTIONS sebelum request POST/PUT/DELETE atau
    # request dengan custom header — untuk tanya izin ke server dulu.
    # =========================================================

    # Access-Control-Allow-Methods — HTTP method yang diizinkan
    # → OPTIONS : wajib ada agar preflight berhasil
    # → GET     : baca resource
    # → POST    : buat resource baru
    # → PUT     : ganti seluruh resource
    # → PATCH   : ubah sebagian resource
    # → DELETE  : hapus resource
    # → HEAD    : seperti GET tapi tanpa body (untuk cek metadata)
    ALLOW_METHODS = [
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "OPTIONS",
        # "HEAD",   # aktifkan jika endpoint mendukung HEAD request
    ]

    # Access-Control-Allow-Headers — request header yang boleh dikirim client cross-origin
    # → Content-Type     : wajib untuk request dengan body JSON / form
    # → Authorization    : wajib untuk Bearer token / Basic auth
    # → Accept           : untuk content negotiation (JSON, XML, dsb)
    # → X-Requested-With : penanda AJAX request (jQuery, Axios)
    # → X-API-Key        : untuk autentikasi via custom API key header
    # → X-Request-Id     : untuk tracing, bisa dikirim dari client
    ALLOW_HEADERS = [
        "Content-Type",
        "Authorization",
        "Accept",
        "X-Requested-With",
        "X-API-Key",
        "X-Request-Id",
        # "X-Custom-Header",  # tambahkan custom header lain jika dibutuhkan
    ]

    # Access-Control-Max-Age — berapa lama browser cache hasil preflight (detik)
    # → 0      : tidak di-cache, selalu preflight ulang
    # → 3600   : 1 jam
    # → 86400  : 1 hari (pilihan kami — kurangi jumlah preflight request)
    # → 7200   : batas maksimum di Chromium
    # ⚠ Firefox membatasi maksimum 86400, Chromium 7200.
    #   Nilai di atas 7200 akan diabaikan Chromium.
    MAX_AGE = "86400"

    # =========================================================
    # EXPOSE HEADERS
    # Header response yang boleh dibaca JS client cross-origin.
    # Secara default browser hanya ekspos header "safe" (Content-Type, dsb).
    # Header custom wajib didaftarkan di sini agar bisa dibaca JS.
    # =========================================================

    # Access-Control-Expose-Headers — response header yang bisa diakses JS
    # → X-Request-Id         : ID unik per request untuk tracing / laporan error
    # → X-RateLimit-Limit    : total kuota request dalam satu window
    # → X-RateLimit-Remaining: sisa kuota request
    # → X-RateLimit-Reset    : waktu reset kuota (Unix timestamp)
    # → X-API-Version        : versi API yang melayani request
    EXPOSE_HEADERS = [
        "X-Request-Id",
        "X-RateLimit-Limit",
        "X-RateLimit-Remaining",
        "X-RateLimit-Reset",
        "X-API-Version",
        # "X-Custom-Header",  # tambahkan header lain yang perlu dibaca JS client
    ]

    # =========================================================
    # BUILD & APPLY
    # =========================================================

    response.headers["Access-Control-Allow-Origin"]   = ", ".join(ALLOW_ORIGIN)
    response.headers["Access-Control-Allow-Methods"]  = ", ".join(ALLOW_METHODS)
    response.headers["Access-Control-Allow-Headers"]  = ", ".join(ALLOW_HEADERS)
    response.headers["Access-Control-Max-Age"]        = MAX_AGE
    response.headers["Access-Control-Expose-Headers"] = ", ".join(EXPOSE_HEADERS)

    if ALLOW_CREDENTIALS:
        response.headers["Access-Control-Allow-Credentials"] = "true"

    # Vary: Origin — wajib jika origin di-whitelist secara dinamis (bukan "*")
    # Memberitahu proxy/CDN bahwa response berbeda per origin.
    # → aktifkan jika ALLOW_ORIGIN berisi domain spesifik (bukan "*")
    # response.headers["Vary"] = "Origin"

    return response