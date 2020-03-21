from flask import Flask, url_for
import os
import random

app = Flask(__name__)


@app.route('/')
@app.route('/index')
def index():
    return '<h1>' + str(random.randint(-100000, 100000)) + '</h1>'


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(port=port, host='0.0.0.0')
