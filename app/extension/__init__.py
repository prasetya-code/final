import traceback

def register_extension(app):
    try:
        from .flask_compresing import init_compress
        from .flask_cache import init_cache
        from .flask_limit import init_limiter

        init_compress(app)  # compression
        init_cache(app)     # cache
        init_limiter(app)   # rate limiter


    except Exception as e:
        print("\nEXTENSION gagal di regis dan inisialisasi di create_app()")
        print("ERROR:", e)

        traceback.print_exc()