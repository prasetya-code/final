def build_isolation(response):
    """
    Menerapkan header isolasi cross-origin (COOP, COEP, CORP).
    Melindungi halaman dari serangan Spectre, XS-Leaks, dan cross-origin
    data leakage dengan mengisolasi browsing context secara ketat.

    Ketiga header ini bekerja sebagai satu kesatuan:
    COOP + COEP → mengaktifkan Cross-Origin Isolation (crossOriginIsolated = true)
                  yang diperlukan untuk SharedArrayBuffer & high-resolution timer.
    CORP        → melindungi resource server ini dari dimuat situs lain.
    """

    # =========================================================
    # CROSS-ORIGIN OPENER POLICY (COOP)
    # Mengisolasi tab/window dari halaman cross-origin lain.
    # Mencegah halaman lain mengakses window object kita via
    # window.open() atau link target="_blank".
    #
    # Cara kerja:
    #   Tanpa COOP → halaman yang membuka kita via window.open()
    #                masih bisa akses window.opener kita
    #   Dengan COOP → window.opener di-null-kan, tidak ada akses
    # =========================================================

    # → "unsafe-none"            : tidak ada isolasi (default browser)
    # → "same-origin-allow-popups" : izinkan popup ke cross-origin,
    #                                blokir akses window dari cross-origin
    # → "same-origin"            : isolasi penuh — hanya same-origin
    #                              yang boleh berbagi browsing group (pilihan kami)
    # ⚠ same-origin akan memutus integrasi OAuth / payment popup cross-origin.
    #   Gunakan "same-origin-allow-popups" jika ada flow popup cross-origin.
    COOP = "same-origin"

    # =========================================================
    # CROSS-ORIGIN EMBEDDER POLICY (COEP)
    # Memastikan semua resource yang dimuat halaman ini
    # secara eksplisit mengizinkan cross-origin embedding.
    #
    # Cara kerja:
    #   Tanpa COEP → browser bebas muat resource cross-origin apapun
    #   Dengan COEP → resource cross-origin wajib punya CORP atau CORS
    #                 yang sesuai, jika tidak maka diblokir browser
    # =========================================================

    # → "unsafe-none"    : tidak ada pembatasan (default browser)
    # → "require-corp"   : semua resource wajib punya CORP atau CORS (pilihan kami)
    # → "credentialless" : resource tanpa kredensial bebas dimuat,
    #                      resource dengan kredensial wajib punya CORP/CORS
    #                      (lebih longgar, cocok jika ada resource CDN tanpa CORP)
    # ⚠ "require-corp" akan memblokir resource pihak ketiga (CDN, API, font)
    #   yang belum pasang header CORP atau CORS.
    #   Gunakan "credentialless" sebagai alternatif yang lebih permisif.
    COEP = "require-corp"

    # =========================================================
    # CROSS-ORIGIN RESOURCE POLICY (CORP)
    # Mencegah situs lain memuat resource dari server ini
    # via tag <img>, <script>, <link>, dsb (no-cors request).
    #
    # Cara kerja:
    #   Tanpa CORP → situs manapun bisa embed resource kita
    #   Dengan CORP → browser blokir request cross-origin
    #                 yang tidak memenuhi policy ini
    # =========================================================

    # → "same-origin"  : hanya same-origin yang boleh memuat (pilihan kami)
    # → "same-site"    : izinkan seluruh site yang sama (lebih longgar),
    #                    mencakup semua subdomain dalam satu eTLD+1
    # → "cross-origin" : izinkan semua origin — gunakan ini jika server
    #                    adalah CDN atau menyajikan public asset
    # ⚠ Jika server ini menyajikan resource untuk dikonsumsi situs lain,
    #   gunakan "cross-origin" agar tidak diblokir browser mereka.
    CORP = "same-origin"

    # =========================================================
    # BUILD & APPLY
    # =========================================================

    response.headers["Cross-Origin-Opener-Policy"]   = COOP
    response.headers["Cross-Origin-Embedder-Policy"] = COEP
    response.headers["Cross-Origin-Resource-Policy"] = CORP

    return response