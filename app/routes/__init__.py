import traceback

def register_routes(app):
    try:
        from .app_routes import main_bp
        app.register_blueprint(main_bp)

    except Exception as e:
        print("\nROUTE gagal di regis dan inisialisasi di create_app()")
        print("ERROR:", e)
        traceback.print_exc()