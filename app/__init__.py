from flask import Flask
import traceback

def create_app():
    # initialize core
    # ===================
    core = Flask(__name__, static_folder='static', template_folder='templates')

    try: 
        # register extension
        # ===================
        from app.extension import register_extension
        register_extension(core)

        # register routes
        # ===================
        from app.routes import register_routes
        register_routes(core)


    except Exception as e:
        print("\nFAILURE")
        print("ERROR:", e)

        traceback.print_exc() 


    return core