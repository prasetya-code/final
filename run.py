from app import create_app

if __name__ == "__main__":
    app = create_app()
    
    app.run(debug=True,
            use_reloader=True, 
            host='0.0.0.0', 
            port=5000)