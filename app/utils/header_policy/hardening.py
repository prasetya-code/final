def build_hardening(response):
    """
    Menerapkan header hardening browser.
    Menutup celah keamanan sisi klien yang tidak ditangani CSP, transport,
    atau isolation — mencakup MIME sniffing, clickjacking, referrer leakage,
    dan akses JS ke hardware / API sensitif.
    """

    # =========================================================
    # MIME SNIFFING PROTECTION
    # Mencegah browser menebak tipe konten di luar apa yang
    # dideklarasikan server di header Content-Type.
    #
    # Cara kerja tanpa header ini:
    #   Server kirim file .txt → browser "baca" isinya
    #   → browser deteksi ada kode JS di dalamnya
    #   → browser jalankan sebagai JS (MIME sniffing)
    #   → celah eksekusi kode berbahaya
    # =========================================================

    # → "nosniff" : wajib; satu-satunya nilai valid.
    #               browser percaya Content-Type dari server, tidak menebak sendiri.
    CONTENT_TYPE_OPTIONS = "nosniff"

    # =========================================================
    # CLICKJACKING PROTECTION
    # Mencegah halaman ini di-embed ke dalam <iframe> oleh situs lain.
    #
    # Cara kerja serangan tanpa header ini:
    #   Penyerang embed halaman kita dalam iframe transparan
    #   → overlay tombol palsu di atasnya
    #   → user klik tombol palsu → sebenarnya klik tombol di halaman kita
    #
    # ⚠ Di browser modern, frame-ancestors di CSP sudah menggantikan header ini.
    #   Tetap dipertahankan sebagai fallback untuk browser lama.
    # =========================================================

    # → "DENY"        : blokir semua iframe dari siapapun (pilihan kami)
    # → "SAMEORIGIN"  : izinkan iframe hanya dari origin sendiri
    FRAME_OPTIONS = "DENY"

    # =========================================================
    # XSS FILTER (LEGACY)
    # Filter XSS bawaan browser lama (IE, Chrome < 78).
    # Sengaja DIMATIKAN karena filter ini justru bisa dieksploitasi
    # untuk membuat XSS baru di browser yang seharusnya terlindungi.
    # Proteksi XSS modern sudah ditangani sepenuhnya oleh CSP.
    #
    # Cara kerja filter lama (yang bermasalah):
    #   Browser deteksi pola XSS di URL → coba "potong" bagian berbahaya
    #   → hasil potongan itu sendiri bisa dimanipulasi jadi celah XSS baru
    # =========================================================

    # → "0"           : nonaktifkan filter (pilihan kami — lebih aman)
    # → "1"           : aktifkan filter, sanitasi halaman saat XSS terdeteksi
    # → "1; mode=block" : aktifkan filter, blokir total render halaman
    XSS_PROTECTION = "0"

    # =========================================================
    # REFERRER POLICY
    # Mengatur informasi URL asal (referrer) yang dikirim browser
    # saat user navigasi ke halaman lain atau saat request resource.
    #
    # Risiko tanpa header ini:
    #   User di https://toko.com/checkout?token=abc123
    #   → klik link ke situs eksternal
    #   → situs eksternal terima header: Referer: https://toko.com/checkout?token=abc123
    #   → token/data sensitif di URL bocor ke pihak lain
    # =========================================================

    # → "no-referrer"                    : tidak kirim referrer sama sekali
    # → "no-referrer-when-downgrade"     : kirim ke HTTPS, tidak kirim saat turun ke HTTP
    # → "same-origin"                    : kirim full URL hanya ke same-origin
    # → "origin"                         : kirim origin saja ke semua tujuan
    # → "strict-origin"                  : kirim origin saja, tidak kirim saat downgrade ke HTTP
    # → "origin-when-cross-origin"       : full URL ke same-origin, origin saja ke cross-origin
    # → "strict-origin-when-cross-origin": full URL ke same-origin, origin saja ke cross-origin,
    #                                      tidak kirim saat downgrade ke HTTP (pilihan kami)
    # → "unsafe-url"                     : selalu kirim full URL ke semua tujuan — HINDARI
    REFERRER_POLICY = "strict-origin-when-cross-origin"

    # =========================================================
    # PERMISSIONS POLICY
    # Menonaktifkan akses JS ke fitur browser / hardware yang tidak dibutuhkan.
    # Mencegah script jahat (termasuk dari third-party) mengakses API sensitif.
    #
    # Format nilai per fitur:
    # → ()        : blokir semua origin (termasuk halaman itu sendiri)
    # → (self)    : izinkan hanya same-origin
    # → (*)       : izinkan semua origin
    # → (self "https://domain.com") : izinkan same-origin + domain spesifik
    # =========================================================

    PERMISSIONS = [

        # --- Hardware Sensitif ---
        # Diblokir karena sangat sensitif dan tidak dibutuhkan website pada umumnya.
        # Mobile  : browser sudah minta izin user via popup native jika benar-benar dibutuhkan.
        # Desktop : secara fisik tidak punya sensor ini.
        "geolocation=()",           # GPS / lokasi pengguna
        "microphone=()",            # akses mikrofon
        "camera=()",                # akses kamera
        "usb=()",                   # akses perangkat USB
        "bluetooth=()",             # akses Bluetooth

        # --- Fitur Display ---
        "fullscreen=()",            # mode layar penuh
        "picture-in-picture=()",    # mode picture-in-picture

        # --- Payment & Identity ---
        "payment=()",                       # Payment Request API
        "publickey-credentials-get=()",     # WebAuthn / passkey

        # ✅ TIDAK DIBLOKIR — sensor gerak & cahaya:
        # accelerometer, gyroscope, magnetometer, ambient-light-sensor
        # → Belum jadi standar W3C resmi, menyebabkan warning di console browser.
        # → Mobile  : browser sudah tangani izin via popup native.
        # → Desktop : tidak punya hardware sensor ini.

        # ✅ TIDAK DIBLOKIR — fitur network:
        # sync-xhr → deprecated, browser modern sudah tidak mendukung.

        # ❌ DIHAPUS — belum standar W3C, menyebabkan warning di console:
        # "attribution-reporting=()"      → Google Privacy Sandbox
        # "private-aggregation=()"        → Google Privacy Sandbox
        # "shared-storage=()"             → Google Privacy Sandbox
        # "shared-storage-select-url=()"  → Google Privacy Sandbox
        # "interest-cohort=()"            → FLoC Google, sudah ditinggalkan
        # "browsing-topics=()"            → belum standar resmi W3C
    ]

    # =========================================================
    # BUILD & APPLY
    # =========================================================

    response.headers["X-Content-Type-Options"] = CONTENT_TYPE_OPTIONS
    response.headers["X-Frame-Options"]        = FRAME_OPTIONS
    response.headers["X-XSS-Protection"]       = XSS_PROTECTION
    response.headers["Referrer-Policy"]        = REFERRER_POLICY
    response.headers["Permissions-Policy"]     = ", ".join(PERMISSIONS)

    return response