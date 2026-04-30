from flask import Flask


def create_app():
    # initialize core
    core = Flask(__name__, static_folder='static', template_folder='templates')

    

    # register extension
    from app.extension import register_extension
    register_extension(core)

    """ # register config
    from config import register_config
    register_config(core)

    # register middleware
    from app.middleware import register_middleware
    register_middleware(core) """

    # register routes
    from app.routes import register_routes
    register_routes(core)

    """ # Cegah browser cache halaman HTML (fix untuk Brave & aggressive caching)
    @core.after_request
    def set_no_cache(response):
        if "text/html" in response.content_type:
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response.headers["Pragma"]        = "no-cache"
            response.headers["Expires"]       = "0"
        return response """

    return core