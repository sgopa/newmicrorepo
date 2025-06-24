from flask import Flask, Response
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

REQUEST_COUNTER = Counter('app_requests_total', 'Total number of requests to the root endpoint')

@app.route("/")
def index():
    REQUEST_COUNTER.inc()
    return "Hello from satish micro!"

@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

