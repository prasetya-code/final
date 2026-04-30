import traceback

def register_extension(app):
    try:
        from flask_compress import Compress
        
        from app.extension.flask_cache import init_cache
        from app.extension.flask_limiter import init_limiter

        compress = Compress()  # inisialisasi tanpa app dulu

        # aktifkan compression
        compress.init_app(app)
        
        # cache
        init_cache(app)

        # rate limiter
        init_limiter(app)

        print("extension sudah di inisialisasi di create_app()")

    except Exception as e:
        print("extension gagal di inisialisasi di create_app()")
        print("ERROR:", e)
        traceback.print_exc()