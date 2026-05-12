import traceback

def register_config(app): 
    try:
        print('h')

    except Exception as e:
        print("\nROUTE gagal di regis dan inisialisasi di create_app()")
        print("ERROR:", e)
        traceback.print_exc()