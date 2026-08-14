from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route("/")
def home():
    return "Hello from DevOps!"


@app.route("/health")
def health():
    return {
        "status": "UP",
        "application": "DevOps Employee Portal"
    }


@app.route("/api")
def api():
    return {
        "message": "DevOps API is working!"
    }


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
