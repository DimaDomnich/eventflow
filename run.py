from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()


@app.route("/health")
def health():
    return {"status": "ok"}, 200
