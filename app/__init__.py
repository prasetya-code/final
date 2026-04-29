from flask import Flask
from flask_compress import Compress

from extension.flask_cache import init_cache

compress = Compress()  # inisialisasi tanpa app dulu

def create_app():
    # initialize core
    core = Flask(__name__, static_folder='static', template_folder='templates')

    # aktifkan compression
    compress.init_app(core)
    init_cache(core)

    """ # Cegah browser cache halaman HTML (fix untuk Brave & aggressive caching)
    @core.after_request
    def set_no_cache(response):
        if "text/html" in response.content_type:
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response.headers["Pragma"]        = "no-cache"
            response.headers["Expires"]       = "0"
        return response """

    return core