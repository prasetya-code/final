import traceback

def register_utils(app):
    try:
        from .nonce import init_nonce

        init_nonce(app)

    except Exception as e:
        print("\nUTILS gagal di regis dan inisialisasi di create_app()")
        print("ERROR:", e)
        traceback.print_exc()