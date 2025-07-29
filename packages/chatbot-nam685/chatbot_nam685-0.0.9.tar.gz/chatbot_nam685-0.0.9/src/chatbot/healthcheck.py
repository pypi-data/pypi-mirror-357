import os
import urllib.request


def health_check():
    port = os.getenv("CONTAINER_PORT", "8000")
    url = f"http://localhost:{port}/ok"
    try:
        with urllib.request.urlopen(url) as response:
            status_code = response.getcode()
            body = response.read().decode()
            print(f"Status code: {status_code}")
            print(f"Response body: {body}")
    except Exception as e:
        print(f"Health check failed: {e}")
        exit(1)


if __name__ == "__main__":
    health_check()
