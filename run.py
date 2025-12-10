from app import create_app

app = create_app("dev")

if __name__ == "__main__":
    print("=" * 50)
    print("Iniciando servidor Flask...")
    print("=" * 50)
    app.run(host="127.0.0.1", port=5000, debug=True)
