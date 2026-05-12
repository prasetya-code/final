def build_cache(response):
    """
    Menerapkan header Cache-Control sesuai tipe konten response.
    Data sensitif tidak di-cache, static asset di-cache agresif.

    Header yang dikelola file ini:
      Cache-Control, Pragma, Expires
    """

    if response.mimetype == "application/json":

        # =====================================================
        # JSON / DATA API — dilarang cache
        # Berisi data dinamis atau sensitif per user/session.
        #
        # Cache-Control:
        # → no-store          : jangan simpan di cache manapun — browser, proxy, CDN (pilihan kami)
        # → no-cache          : simpan tapi wajib validasi ke server sebelum dipakai
        # → private           : hanya boleh di-cache browser, bukan proxy/CDN
        # → max-age=0         : langsung expired, kombinasikan dengan must-revalidate
        # → must-revalidate   : setelah expired, wajib tanya server sebelum pakai cache lama
        # =====================================================
        response.headers["Cache-Control"] = "no-store"

    elif response.mimetype == "text/html":

        # =====================================================
        # HTML — cache singkat, wajib revalidasi
        # Sering mengandung data user-specific (nama, sesi, CSRF token).
        # Tidak boleh di-cache proxy/CDN karena tiap user bisa dapat
        # konten berbeda dari URL yang sama.
        #
        # Cache-Control:
        # → private           : hanya boleh di-cache browser, bukan proxy/CDN (pilihan kami)
        # → no-store          : jangan cache sama sekali
        # → max-age=0         : langsung expired (pilihan kami)
        # → must-revalidate   : setelah expired, wajib validasi ke server (pilihan kami)
        # → no-cache          : simpan tapi selalu validasi sebelum pakai
        # ⚠ Jangan pakai no-store untuk HTML — browser butuh cache untuk tombol Back.
        # =====================================================
        response.headers["Cache-Control"] = "private, max-age=0, must-revalidate"

    else:

        # =====================================================
        # STATIC ASSET — cache agresif
        # JS, CSS, gambar, font — konten tidak berubah selama nama file sama.
        # Aman di-cache lama karena static asset wajib pakai cache-busting hash.
        #
        # Cache-Control:
        # → public                   : boleh di-cache browser, proxy, dan CDN (pilihan kami)
        # → private                  : hanya boleh di-cache browser saja
        # → max-age=31536000         : cache berlaku 1 tahun sejak response (pilihan kami)
        # → s-maxage=N               : override max-age khusus untuk proxy/CDN
        # → immutable                : file tidak berubah selama max-age —
        #                              browser skip re-validasi saat refresh (pilihan kami)
        # → must-revalidate          : setelah expired, wajib validasi ke server
        # → stale-while-revalidate=N : sajikan cache lama selama N detik
        #                              sambil fetch versi baru di background
        # ⚠ Wajib pakai cache-busting hash di nama file sebelum memakai max-age panjang + immutable.
        #   Contoh: main.a3f9c1.js — jika file berubah, nama berubah,
        #   cache lama otomatis tidak terpakai.
        # =====================================================
        response.headers["Cache-Control"] = "public, max-age=31536000, immutable"

    # Pragma: no-cache
    # Header cache lama untuk HTTP/1.0 client dan proxy lama
    # yang tidak mengenal Cache-Control.
    # → no-cache : satu-satunya nilai yang relevan di sini
    # ⚠ Hanya berlaku untuk response yang memang tidak boleh di-cache.
    #   Untuk static asset, header ini tidak dikirim.
    if response.mimetype in ("application/json", "text/html"):
        response.headers["Pragma"]  = "no-cache"

        # Expires: 0
        # Tanggal kedaluwarsa untuk HTTP/1.0 client.
        # → 0    : sudah expired — paksa client selalu fetch ulang
        # → <HTTP-date> : tanggal spesifik kedaluwarsa cache
        response.headers["Expires"] = "0"

    return response