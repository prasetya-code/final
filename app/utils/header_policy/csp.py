def build_csp(response):
    """
    Menerapkan header Content-Security-Policy (CSP).
    Whitelist sumber konten yang boleh dimuat browser — lapisan utama pertahanan XSS.

    Setiap directive berbentuk list/array agar mudah ditambah atau dihapus per item.
    Tambahkan domain eksternal langsung ke array directive yang relevan.
    """

    # =========================================================
    # FETCH DIRECTIVES
    # Mengontrol dari mana browser boleh memuat resource.
    # Urutan prioritas: directive spesifik > default-src.
    #
    # Nilai umum yang bisa ditambahkan ke array:
    # → 'self'              : hanya origin sendiri (protokol + domain + port sama)
    # → 'none'              : blokir semua
    # → 'unsafe-inline'     : izinkan inline script/style — HINDARI
    # → 'unsafe-eval'       : izinkan eval() — HINDARI jika bisa
    # → 'nonce-<token>'     : izinkan elemen dengan nonce spesifik
    # → 'strict-dynamic'    : percayai script yang sudah diizinkan nonce/hash
    # → 'wasm-unsafe-eval'  : izinkan WebAssembly
    # → data:               : izinkan data URI base64
    # → blob:               : izinkan blob URL
    # → https:              : izinkan semua HTTPS
    # → https://domain.com  : izinkan domain spesifik
    # → wss://domain.com    : izinkan WebSocket ke domain spesifik
    # =========================================================

    # default-src — fallback untuk semua directive fetch yang tidak didefinisikan
    DEFAULT_SRC = [
        "'self'",
    ]

    # script-src — sumber JS yang boleh dieksekusi
    # ⚠ Jangan tambahkan 'unsafe-inline' — ini membatalkan proteksi XSS.
    SCRIPT_SRC = [
        "'self'",
    ]

    # style-src — sumber CSS yang boleh diterapkan
    # ⚠ Framework CSS modern kadang butuh 'unsafe-inline' —
    #   pertimbangkan 'nonce-<token>' sebagai alternatif yang lebih aman.
    STYLE_SRC = [
        "'self'",
        # "'unsafe-inline'",          # aktifkan jika pakai Tailwind CDN / inline style
        # "https://fonts.googleapis.com",  # aktifkan jika pakai Google Fonts
    ]

    # img-src — sumber gambar (<img>, background-image CSS, favicon)
    IMG_SRC = [
        "'self'",
        "data:",                       # base64 inline image / placeholder
        # "blob:",                     # aktifkan jika ada preview upload
        # "https://cdn.domain.com",    # aktifkan jika gambar dari CDN eksternal
    ]

    # font-src — sumber file font (@font-face)
    FONT_SRC = [
        "'self'",
        # "https://fonts.gstatic.com", # aktifkan jika pakai Google Fonts
    ]

    # connect-src — sumber untuk koneksi JS (fetch, XHR, WebSocket, EventSource)
    CONNECT_SRC = [
        "'self'",
        # "https://api.domain.com",    # aktifkan jika ada API eksternal
        # "wss://ws.domain.com",       # aktifkan jika ada WebSocket eksternal
    ]

    # media-src — sumber untuk <audio> dan <video>
    MEDIA_SRC = [
        "'none'",                      # tidak ada kebutuhan media — blokir semua
        # "'self'",                    # aktifkan jika ada audio/video dari server sendiri
    ]

    # worker-src — sumber untuk Web Worker, Service Worker, SharedWorker
    WORKER_SRC = [
        "'self'",
        # "blob:",                     # aktifkan jika pakai bundler (Webpack, Vite)
    ]

    # child-src — sumber untuk <frame>, <iframe>, dan worker
    #             (fallback sebelum worker-src / frame-src didefinisikan)
    CHILD_SRC = [
        "'none'",                      # blokir semua child context
    ]

    # manifest-src — sumber untuk file Web App Manifest (manifest.json)
    MANIFEST_SRC = [
        "'self'",
    ]

    # =========================================================
    # DOCUMENT DIRECTIVES
    # Mengontrol properti dokumen itu sendiri, bukan resource-nya.
    # =========================================================

    # base-uri — nilai yang diizinkan untuk tag <base href="">
    # ⚠ Tanpa ini, penyerang bisa inject <base href="https://evil.com">
    #   sehingga semua relative URL mengarah ke domain mereka.
    BASE_URI = [
        "'self'",
        # "'none'",                    # alternatif: larang tag <base> sama sekali
    ]

    # =========================================================
    # NAVIGATION DIRECTIVES
    # Mengontrol ke mana browser boleh dinavigasikan.
    # =========================================================

    # form-action — URL yang diizinkan sebagai target <form action="">
    # ⚠ Tanpa ini, form bisa di-hijack untuk submit ke domain penyerang.
    FORM_ACTION = [
        "'self'",
        # "https://api.domain.com",    # aktifkan jika form submit ke API eksternal
    ]

    # frame-ancestors — siapa yang boleh embed halaman ini via <iframe>, <frame>, <object>
    # ⚠ Directive ini MENGGANTIKAN X-Frame-Options di browser modern.
    FRAME_ANCESTORS = [
        "'none'",                      # tidak boleh di-embed siapapun
        # "'self'",                    # alternatif: izinkan embed oleh origin sendiri
        # "https://dashboard.domain.com", # alternatif: izinkan domain spesifik
    ]

    # =========================================================
    # OTHER DIRECTIVES
    # =========================================================

    # object-src — sumber untuk <object>, <embed>, <applet> (plugin lama: Flash, Java)
    # ⚠ Plugin lama adalah vektor serangan besar — selalu set ke 'none'.
    OBJECT_SRC = [
        "'none'",
    ]

    # upgrade-insecure-requests — paksa semua request HTTP menjadi HTTPS otomatis
    # ⚠ Berbeda dengan HSTS: directive ini hanya berlaku dalam scope halaman,
    #   bukan di level browser secara keseluruhan.
    UPGRADE_INSECURE = True

    # =========================================================
    # BUILD & APPLY
    # Susun semua directive dari array menjadi satu string header CSP.
    # =========================================================

    directives = {
        "default-src":     DEFAULT_SRC,
        "script-src":      SCRIPT_SRC,
        "style-src":       STYLE_SRC,
        "img-src":         IMG_SRC,
        "font-src":        FONT_SRC,
        "connect-src":     CONNECT_SRC,
        "media-src":       MEDIA_SRC,
        "worker-src":      WORKER_SRC,
        "child-src":       CHILD_SRC,
        "manifest-src":    MANIFEST_SRC,
        "base-uri":        BASE_URI,
        "form-action":     FORM_ACTION,
        "frame-ancestors": FRAME_ANCESTORS,
        "object-src":      OBJECT_SRC,
    }

    policy = "; ".join(
        f"{directive} {' '.join(sources)}"
        for directive, sources in directives.items()
    )

    if UPGRADE_INSECURE:
        policy += "; upgrade-insecure-requests"

    response.headers["Content-Security-Policy"] = policy

    return response