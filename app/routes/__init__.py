import traceback

def register_routes(app):
    try:
        from .app_routes import main_bp
        app.register_blueprint(main_bp)

        print("route sudah di inisialisasi di create_app()")

    except Exception as e:
        print("route gagal di inisialisasi di create_app()")
        print("ERROR:", e)
        traceback.print_exc()