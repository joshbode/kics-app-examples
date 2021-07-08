import os
from random import randrange

from flask import Flask

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello, Kelves! How's it going?"


@app.route("/get-random-value")
def get_random_value() -> dict:
    random_number = randrange(0, 100)
    return {"value": random_number}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
