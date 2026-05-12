def build_transport(response):
    """
    Menerapkan header keamanan transport layer.
    Memastikan semua komunikasi antara browser dan server berjalan
    melalui kanal yang aman (HTTPS / TLS).
    """

    # =========================================================
    # STRICT TRANSPORT SECURITY (HSTS)
    # Memaksa browser selalu menggunakan HTTPS untuk domain ini.
    # Mencegah serangan SSL stripping dan downgrade ke HTTP.
    #
    # Cara kerja:
    #   Kunjungan pertama → server kirim header ini via HTTPS
    #   Kunjungan berikutnya → browser langsung pakai HTTPS
    #                          tanpa perlu redirect dari server
    #
    # ⚠ Pastikan seluruh aplikasi sudah 100% HTTPS sebelum mengaktifkan.
    #   Jika masih ada resource HTTP, browser akan memblokir semuanya
    #   dan tidak bisa di-undo sebelum max-age habis.
    # =========================================================

    # max-age — berapa lama browser mengingat aturan HSTS (dalam detik)
    # → 0        : hapus HSTS dari browser (gunakan saat ingin menonaktifkan)
    # → 300      : 5 menit (gunakan saat pertama kali testing)
    # → 86400    : 1 hari
    # → 2592000  : 30 hari
    # → 31536000 : 1 tahun — nilai minimum untuk masuk preload list (pilihan kami)
    HSTS_MAX_AGE = 31536000

    # include_subdomains — terapkan HSTS ke seluruh subdomain
    # → True  : semua subdomain wajib HTTPS (pilihan kami)
    # → False : hanya berlaku untuk domain utama
    # ⚠ Pastikan SEMUA subdomain sudah HTTPS sebelum mengaktifkan.
    #   Subdomain yang masih HTTP akan tidak bisa diakses browser.
    HSTS_INCLUDE_SUBDOMAINS = True

    # preload — daftarkan domain ke browser HSTS preload list
    # → True  : browser langsung pakai HTTPS sejak kunjungan pertama,
    #           bahkan sebelum pernah mengunjungi situs ini (pilihan kami)
    # → False : HSTS aktif hanya setelah kunjungan HTTPS pertama
    # ⚠ Preload bersifat permanen dan sulit dicabut.
    #   Daftar manual di https://hstspreload.org setelah siap.
    #   Syarat: max-age >= 31536000 + includeSubDomains + preload harus aktif.
    HSTS_PRELOAD = True

    # =========================================================
    # BUILD & APPLY
    # =========================================================

    hsts_parts = [f"max-age={HSTS_MAX_AGE}"]

    if HSTS_INCLUDE_SUBDOMAINS:
        hsts_parts.append("includeSubDomains")

    if HSTS_PRELOAD:
        hsts_parts.append("preload")

    response.headers["Strict-Transport-Security"] = "; ".join(hsts_parts)

    return response