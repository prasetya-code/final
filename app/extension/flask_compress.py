from flask_compress import Compress

compress = Compress()


def init_compress(app):

    app.config.setdefault("COMPRESS_ALGORITHM", "gzip")  # bisa: gzip, br
    # gzip = paling kompatibel (semua browser)
    # br (brotli) = lebih kecil, tapi butuh browser modern

    app.config.setdefault("COMPRESS_LEVEL", 6)  # 1-9 (gzip level)
    # 1 = cepat tapi ukuran besar
    # 6 = balance (recommended)
    # 9 = paling kecil tapi berat CPU

    app.config.setdefault("COMPRESS_MIN_SIZE", 500)  # minimal ukuran response (bytes)
    # hanya response >= 500 bytes yang akan dikompres
    # tujuan: menghindari overhead untuk data kecil

    # MIME types yang akan dikompres
    app.config.setdefault(
        "COMPRESS_MIMETYPES",
        [
            "text/html",
            "text/css",
            "text/xml",
            "application/json",
            "application/javascript",
        ],
    )
    # hanya tipe file ini yang dikompres
    # tidak termasuk image/video karena sudah terkompresi secara alami

    # Variasi tambahan
    # =================
    app.config.setdefault("COMPRESS_REGISTER", True)
    # True = otomatis compress semua response Flask
    # False = harus manual handling

    app.config.setdefault("COMPRESS_BR_LEVEL", 4)  # Brotli level (kalau pakai br)
    # hanya aktif jika COMPRESS_ALGORITHM = "br"
    # range 0-11 (4 = balance antara speed & compression)

    # init extension
    compress.init_app(app)