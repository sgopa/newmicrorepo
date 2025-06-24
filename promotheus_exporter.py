from prometheus_client import start_http_server, Counter
import time

REQUEST_COUNT = Counter('app_requests_total', 'Total app HTTP requests')

if __name__ == "__main__":
    start_http_server(8080)
    while True:
        REQUEST_COUNT.inc()
        time.sleep(1)

