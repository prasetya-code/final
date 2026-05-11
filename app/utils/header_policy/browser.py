def browser_privacy(response):
    """
    Menerapkan header keamanan dan privasi browser.
    Mencegah berbagai serangan sisi klien dan kebocoran informasi.
    """

    # X-Content-Type-Options ➡️ Mencegah browser menebak tipe konten (MIME sniffing).
    # → nosniff : wajib; satu-satunya nilai valid.
    response.headers["X-Content-Type-Options"] = "nosniff"

    # X-Frame-Options ➡️ Mencegah halaman ini di-embed iframe oleh situs manapun.
    # → DENY       : blokir semua iframe (pilihan kami)
    # → SAMEORIGIN : izinkan hanya same-origin
    response.headers["X-Frame-Options"] = "DENY"

    # X-XSS-Protection ➡️ Filter XSS bawaan browser lama — sengaja DIMATIKAN.
    # → 0               : nonaktifkan (pilihan kami — lebih aman di browser lama)
    # → 1               : aktifkan filter
    # → 1;mode=block    : aktifkan + blokir rendering saat terdeteksi

    # Proteksi XSS modern sudah ditangani oleh CSP di bawah.
    response.headers["X-XSS-Protection"] = "0"

    # Referrer-Policy ➡️ Mengatur informasi referrer yang dikirim browser saat navigasi.
    # → no-referrer                     : tidak kirim referrer sama sekali
    # → same-origin                     : kirim hanya ke same-origin
    # → strict-origin                   : kirim origin saja, tidak kirim saat downgrade ke HTTP
    # → strict-origin-when-cross-origin : full URL ke same-origin, origin saja ke cross-origin (pilihan kami)
    # → unsafe-url                      : selalu kirim full URL (tidak aman)
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    # Permissions-Policy: nama_fitur=(allowlist)
    # Format  → fitur=()          : blokir semua origin
    #         → fitur=(self)      : izinkan hanya same-origin
    #         → fitur=(*)         : izinkan semua origin

    # Tidak diblokir: sensor gerak (accelerometer, gyroscope, magnetometer,
    # ambient-light-sensor) — belum standar W3C, memicu warning di console.
    response.headers["Permissions-Policy"] = (
        "geolocation=(), "              # GPS / lokasi pengguna
        "microphone=(), "               # akses mikrofon
        "camera=(), "                   # akses kamera
        "usb=(), "                      # akses perangkat USB
        "bluetooth=(), "                # akses Bluetooth
        "fullscreen=(), "               # mode layar penuh
        "picture-in-picture=(), "       # mode picture-in-picture
        "payment=(), "                  # Payment Request API
        "publickey-credentials-get=()"  # WebAuthn / passkey
    )

    # Strict-Transport-Security ➡️ Memaksa browser selalu pakai HTTPS — mencegah SSL stripping & downgrade.
    # → max-age=31536000  : browser ingat selama 1 tahun (minimum yang disarankan)
    # → includeSubDomains : berlaku untuk semua subdomain
    # → preload           : daftarkan ke browser HSTS preload list (kunjungan pertama langsung HTTPS)
    
    """ # ⚠ Pastikan seluruh aplikasi sudah 100% HTTPS sebelum mengaktifkan ini.
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains; preload"
    ) """

    # Content-Security-Policy ➡️ Whitelist sumber konten yang boleh dimuat — lapisan utama pertahanan XSS.
    # → default-src 'self'        : fallback semua resource ke same-origin
    # → script-src 'self'         : JS hanya dari same-origin
    # → style-src 'self'          : CSS hanya dari same-origin
    # → img-src 'self' data:      : gambar dari same-origin + data URI base64
    # → font-src 'self'           : font hanya dari same-origin
    # → connect-src 'self'        : XHR / fetch / WebSocket hanya ke same-origin
    # → frame-ancestors 'none'    : perkuat X-Frame-Options DENY
    # → base-uri 'self'           : cegah injeksi tag <base> berbahaya
    # → form-action 'self'        : submit form hanya ke same-origin
    # → object-src 'none'         : nonaktifkan plugin lama (Flash, Java, dll)
    # → upgrade-insecure-requests : paksa resource HTTP ke HTTPS otomatis
    
    # ⚠ Tambahkan domain CDN / API eksternal ke directive yang sesuai jika diperlukan.
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self'; "
        "img-src 'self' data:; "
        "font-src 'self'; "
        "connect-src 'self'; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self'; "
        "object-src 'none'; "
        # "upgrade-insecure-requests"
    )

    # Cross-Origin-Opener-Policy ➡️ Mengisolasi tab/window dari halaman cross-origin yang dibuka via window.open().
    # → unsafe-none                 : tidak ada isolasi (default browser)
    # → same-origin-allow-popups    : izinkan popup ke cross-origin, blokir sebaliknya
    # → same-origin                 : isolasi penuh — hanya same-origin berbagi browsing group (pilihan kami)

    # Diperlukan bersama COEP untuk mengaktifkan SharedArrayBuffer & high-res timer.
    response.headers["Cross-Origin-Opener-Policy"] = "same-origin"

    # Cross-Origin-Embedder-Policy ➡️ Memastikan semua resource yang dimuat halaman ini mengizinkan cross-origin embedding.
    # → unsafe-none   : tidak ada pembatasan (default browser)
    # → require-corp  : semua resource wajib punya CORP atau CORS (pilihan kami)
    # → credentialless: resource tanpa kredensial bebas dimuat, dengan CORP/CORS untuk yang lain
    
    """ # ⚠ Pastikan semua resource pihak ketiga sudah mendukung CORP/CORS sebelum mengaktifkan ini.
    response.headers["Cross-Origin-Embedder-Policy"] = "require-corp" """

    # Cross-Origin-Resource-Policy ➡️ Mencegah situs lain memuat resource dari server ini via <img>, <script>, dll.
    # → same-origin  : hanya same-origin yang boleh memuat (pilihan kami)
    # → same-site    : izinkan seluruh site yang sama (lebih longgar)
    # → cross-origin : izinkan semua — gunakan ini jika server adalah CDN / public asset
    response.headers["Cross-Origin-Resource-Policy"] = "same-origin"

    return response