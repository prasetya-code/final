def register_routes(app):
    from .app_routes import main_bp


    # Apply Blueprint
    app.register_blueprint(main_bp)         # App Routes
