import traceback

# =========================
# 🔥 GLOBAL CONTROL
# =========================
GLOBAL_REDIS = False

def register_extension(app):
    try:
        from .flask_compressing import init_compress
        from .flask_cache import init_cache
        from .flask_limit import init_limiter

        # =========================
        # GLOBAL CONFIG INJECTION
        # =========================
        # Ini akan dipakai oleh cache & limiter
        app.config["GLOBAL_REDIS"] = GLOBAL_REDIS

        print(f"[GLOBAL] GLOBAL_REDIS = {GLOBAL_REDIS} \n")

        # =========================
        # INIT EXTENSIONS
        # =========================
        init_compress(app)
        init_cache(app)
        init_limiter(app)

    except Exception as e:
        print("\nEXTENSION gagal di regis dan inisialisasi di create_app()")
        print("ERROR:", e)

        traceback.print_exc()