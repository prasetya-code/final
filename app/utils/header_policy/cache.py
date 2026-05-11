def cache_data(response):
    """
    Menerapkan header cache sesuai tipe konten.
    Data sensitif tidak di-cache, static asset di-cache agresif.
    """

    if response.mimetype == "application/json":
        # Cache-Control ➡️ Data API / sensitif — jangan simpan di cache manapun.
        # → no-store       : jangan simpan di cache browser, proxy, maupun CDN (pilihan kami)
        # → no-cache       : simpan cache tapi wajib validasi ke server sebelum dipakai
        # → private        : hanya boleh di-cache browser, bukan proxy/CDN
        # → max-age=0      : langsung expired, kombinasikan dengan must-revalidate
        response.headers["Cache-Control"] = "no-store"

    elif response.mimetype == "text/html":
        # Cache-Control ➡️ HTML sering mengandung data user-specific — jangan cache di proxy/CDN.
        # → private         : hanya boleh di-cache browser, bukan proxy/CDN (pilihan kami)
        # → max-age=0       : langsung expired, browser tanya server di request berikutnya
        # → must-revalidate : setelah expired, wajib validasi ke server sebelum pakai cache lama
        
        # ⚠ Jangan pakai no-store untuk HTML — browser butuh cache untuk tombol Back.
        response.headers["Cache-Control"] = "private, max-age=0, must-revalidate"

    else:
        # Cache-Control: public | max-age=N | immutable | s-maxage=N | stale-while-revalidate=N
        # Static asset (JS, CSS, gambar, font) — cache agresif selama 1 tahun.
        # → public                  : boleh di-cache browser, proxy, dan CDN (pilihan kami)
        # → private                 : hanya boleh di-cache browser saja
        # → max-age=31536000        : cache berlaku 1 tahun sejak response (pilihan kami)
        # → s-maxage=N              : override max-age khusus untuk proxy/CDN
        # → immutable               : file tidak berubah selama max-age, browser skip re-validasi saat refresh (pilihan kami)
        # → must-revalidate         : setelah expired, wajib validasi ke server sebelum pakai cache lama
        # → stale-while-revalidate=N: sajikan cache lama selama N detik sambil fetch baru di background
        
        # ⚠ Wajib pakai cache-busting hash di nama file sebelum memakai max-age panjang + immutable.
        #   Contoh: main.a3f9c1.js — jika file berubah, nama berubah, cache lama otomatis tidak terpakai.
        response.headers["Cache-Control"] = "public, max-age=31536000, immutable"

    return response