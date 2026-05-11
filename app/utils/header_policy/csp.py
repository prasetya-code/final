import os

# CSP Keywords — hindari pengulangan string literal
SELF       = "'self'"
NONE       = "'none'"
UNSAFE_EVAL = "'unsafe-eval'"  # ⚠ Hanya untuk development — hapus di production


def csp_policy(nonce=None, mode="web"):
    """
    Membangun string Content-Security-Policy sesuai mode.

    mode:
        web -> website normal (default)
        spa -> frontend SPA dengan endpoint API eksternal
        api -> API backend, CSP tidak diterapkan
    """

    # script-src ➡️ Sumber JS yang boleh dieksekusi browser.
    # → 'self'          : hanya skrip dari origin sendiri
    # → 'unsafe-eval'   : izinkan eval() / new Function() — dibutuhkan beberapa framework (pilihan kami, dev only)
    # → 'nonce-<token>' : izinkan inline script dengan nonce yang cocok
    # → 'strict-dynamic': percayai script yang di-inject oleh script tepercaya (nonce-based)
    # → 'unsafe-inline' : izinkan semua inline script — JANGAN dipakai

    # ⚠ Hapus 'unsafe-eval' dan 'data:' sebelum naik ke production.
    script_src = [
        SELF,
        UNSAFE_EVAL,        # dibutuhkan React dev / beberapa bundler
        "data:",            # dibutuhkan @vitejs/plugin-legacy
        "https://code.iconify.design",
        "https://unpkg.com",
        "https://cdnjs.cloudflare.com",
    ]

    # style-src ➡️ Sumber CSS yang boleh dimuat browser.
    # → 'self'          : hanya stylesheet dari origin sendiri
    # → 'unsafe-inline' : izinkan inline <style> dan atribut style — hindari jika bisa
    # → 'nonce-<token>' : izinkan inline style dengan nonce yang cocok
    style_src = [
        SELF,
        "https://fonts.googleapis.com",
    ]

    # font-src: 'self' | 'none' | 'data:' | <url>
    # Sumber file font yang boleh diunduh browser.
    font_src = [
        SELF,
        "https://fonts.gstatic.com",
    ]

    # connect-src: 'self' | 'none' | <url>
    # Sumber yang boleh dihubungi via fetch, XHR, WebSocket, EventSource.
    connect_src = [
        SELF,
        "https://api.iconify.design",
        "https://api.simplesvg.com",
        "https://api.unisvg.com",
        "https://assets.lottiefiles.com",
        "https://lottie.host",
    ]

    # img-src: 'self' | 'none' | 'data:' | 'blob:' | <url>
    # Sumber gambar yang boleh dimuat browser.
    # → data: : izinkan gambar base64 inline
    # → blob: : izinkan gambar dari Blob URL (canvas export, file upload preview)
    img_src = [
        SELF,
        "data:",
        "https://assets.lottiefiles.com",
        "https://lottie.host",
    ]

    # frame-src: 'self' | 'none' | <url>
    # Sumber yang boleh dimuat di dalam <iframe> oleh halaman ini.
    # Berbeda dengan frame-ancestors (yang mengontrol siapa yang boleh embed KITA).
    # → 'none' : halaman ini tidak memuat iframe dari manapun (pilihan kami)
    frame_src = [NONE]

    # child-src: 'self' | 'none' | <url>
    # Fallback untuk frame-src dan worker-src di browser lama (sebelum CSP Level 3).
    # Browser modern mengabaikan ini jika frame-src / worker-src sudah ada.
    child_src = [NONE]

    # script-src-attr: 'self' | 'none' | 'unsafe-inline' | 'nonce-<token>'
    # Kontrol khusus untuk inline event handler (onclick=, onload=, dsb).
    # Terpisah dari script-src agar bisa diblokir lebih ketat.
    # → 'none' : blokir semua inline event handler atribut (pilihan kami)
    script_src_attr = [NONE]

    # style-src-attr: 'self' | 'none' | 'unsafe-inline'
    # Kontrol khusus untuk atribut style="..." inline pada elemen HTML.
    # → 'none' : blokir semua inline style atribut (pilihan kami)
    # ⚠ Banyak library JS (tooltip, animasi) menyuntikkan style atribut secara otomatis.
    #   Jika ada elemen yang rusak tampilannya, pertimbangkan 'unsafe-inline' di sini saja.
    style_src_attr = [NONE]

    # prefetch-src: 'self' | 'none' | <url>
    # Sumber yang boleh di-prefetch atau di-preload via <link rel="prefetch/preload">.
    # → 'self' : hanya resource dari origin sendiri yang boleh di-prefetch (pilihan kami)
    # ⚠ Directive ini masih dalam draft — tidak semua browser mendukung.
    prefetch_src = [SELF]

    # Nonce — token acak per-request untuk mengizinkan inline script/style tertentu
    # → format : 'nonce-<base64_random_token>'
    # ⚠ Nonce wajib berbeda setiap request. Jangan hardcode.
    if nonce:
        script_src.append(f"'nonce-{nonce}'")
        style_src.append(f"'nonce-{nonce}'")

    # Mode SPA — tambahkan endpoint API eksternal ke connect-src
    if mode == "spa":
        connect_src.append("https://api.yourdomain.com")

    return (
        # default-src: 'self' | 'none' | <url>
        # Fallback untuk semua directive yang tidak disebutkan secara eksplisit.
        f"default-src {NONE}; "

        # upgrade-insecure-requests — paksa semua resource HTTP ke HTTPS otomatis
        "upgrade-insecure-requests; "

        # block-all-mixed-content — blokir resource HTTP saat halaman dibuka via HTTPS
        # ⚠ Sudah dicakup upgrade-insecure-requests, namun tetap disertakan
        #   sebagai lapisan kedua untuk browser lama yang belum mendukung directive di atas.
        "block-all-mixed-content; "

        f"script-src {' '.join(script_src)}; "

        # script-src-elem: kontrol khusus tag <script src="..."> dan <script>inline</script>
        f"script-src-elem {' '.join(script_src)}; "

        # script-src-attr: kontrol khusus inline event handler (onclick=, onload=, dsb)
        f"script-src-attr {' '.join(script_src_attr)}; "

        f"style-src {' '.join(style_src)}; "

        # style-src-elem: kontrol khusus tag <style> dan <link rel="stylesheet">
        f"style-src-elem {' '.join(style_src)}; "

        # style-src-attr: kontrol khusus atribut style="..." inline
        f"style-src-attr {' '.join(style_src_attr)}; "

        f"font-src {' '.join(font_src)}; "
        f"img-src {' '.join(img_src)}; "
        f"connect-src {' '.join(connect_src)}; "
        f"frame-src {' '.join(frame_src)}; "
        f"child-src {' '.join(child_src)}; "
        f"prefetch-src {' '.join(prefetch_src)}; "

        # object-src: 'none' — blokir plugin lama (Flash, Java, Silverlight)
        f"object-src {NONE}; "

        # frame-ancestors: 'none' | 'self' | <url>
        # Kontrol siapa yang boleh meng-embed halaman ini ke dalam iframe.
        # → 'none' : tidak ada yang boleh embed halaman ini (pilihan kami)
        # → 'self' : hanya same-origin yang boleh embed
        f"frame-ancestors {NONE}; "

        # base-uri: 'self' | 'none'
        # Batasi nilai tag <base href="...">.
        # → 'none' : tolak semua tag <base> — cegah base tag injection
        f"base-uri {NONE}; "

        # form-action: 'self' | 'none' | <url>
        # Batasi tujuan submit <form>.
        # → 'self' : form hanya boleh submit ke origin sendiri (pilihan kami)
        f"form-action {SELF}; "

        # manifest-src: 'self' — hanya PWA manifest dari origin sendiri
        f"manifest-src {SELF}; "

        # worker-src: 'self' | 'none' | 'blob:' | <url>
        # Sumber untuk Web Worker, Service Worker, dan Shared Worker.
        # → 'self' : hanya worker dari origin sendiri (pilihan kami)
        # → 'blob:': dibutuhkan jika worker dibuat dari Blob URL
        f"worker-src {SELF}; "

        # media-src: 'self' | 'none' | <url>
        # Sumber untuk elemen <audio> dan <video>.
        f"media-src {SELF}; "

        # require-trusted-types-for 'script' — cegah DOM XSS via Trusted Types API
        # Semua assignment ke sink berbahaya (innerHTML, eval, dsb) wajib melalui Trusted Types.
        "require-trusted-types-for 'script'; "

        # trusted-types: default | <nama-policy> | 'none' | 'allow-duplicates'
        # → default : izinkan hanya policy bernama "default"
        # → 'none'  : blokir semua Trusted Types policy (sangat ketat)
        "trusted-types default; "

        # report-uri — endpoint penerima laporan pelanggaran CSP (format lama, masih luas didukung)
        "report-uri /csp-report; "

        # report-to — endpoint penerima laporan CSP (format baru, pakai Reporting API)
        # Merujuk ke group yang didefinisikan di header Report-To.
        "report-to csp-endpoint; "
    )


def csp_headers(response, nonce=None, mode="web"):
    """
    Menerapkan header CSP ke response.

    CSP_REPORT_ONLY=true → pakai Content-Security-Policy-Report-Only (debugging, tidak memblokir)
    CSP_REPORT_ONLY=false → pakai Content-Security-Policy (enforced, memblokir pelanggaran)
    """

    # Mode API tidak membutuhkan CSP — browser tidak merender halaman dari API
    if mode == "api":
        return response

    csp = csp_policy(nonce, mode)

    if os.getenv("CSP_REPORT_ONLY", "false").lower() == "true":
        # Report-Only: laporkan pelanggaran tanpa memblokir — gunakan saat development / rollout bertahap
        response.headers["Content-Security-Policy-Report-Only"] = csp
    else:
        # Enforced: blokir semua pelanggaran secara aktif
        response.headers["Content-Security-Policy"] = csp

    return response


def csp_report(response, mode="web"):
    """
    Menerapkan header Report-To untuk Reporting API browser modern.
    Digunakan bersama directive report-to di CSP.

    Report-To: {"group": "<nama>", "max_age": <detik>, "endpoints": [{"url": "<url>"}]}
    → group    : nama grup yang dirujuk oleh directive report-to di CSP
    → max_age  : berapa lama browser menyimpan konfigurasi ini (detik)
    → endpoints: daftar URL tujuan pengiriman laporan
    """

    if mode == "api":
        return response

    response.headers["Report-To"] = (
        "{"
        '"group":"csp-endpoint",'
        '"max_age":10886400,'
        '"endpoints":[{"url":"/csp-report"}]'
        "}"
    )

    return response