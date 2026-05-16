import multiprocessing
import os
import socket
import sys
import time
import urllib.request
from pathlib import Path

import uvicorn
import webview

if getattr(sys, "frozen", False):
    bundle_dir = Path(getattr(sys, "_MEIPASS", Path(sys.executable).resolve().parent))
    runtime_dir = Path(sys.executable).resolve().parent
else:
    bundle_dir = Path(__file__).resolve().parent
    runtime_dir = bundle_dir

os.chdir(runtime_dir)
sys.path.insert(0, str(bundle_dir))

from app.main import app


def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def start_backend(port):
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")


def wait_for_backend(port, timeout=30):
    deadline = time.time() + timeout
    url = f"http://127.0.0.1:{port}/"
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1):
                return True
        except Exception:
            time.sleep(0.3)
    return False


def main():
    port = find_free_port()
    backend_process = multiprocessing.Process(target=start_backend, args=(port,))
    backend_process.daemon = True
    backend_process.start()

    wait_for_backend(port)

    webview.create_window(
        "YOLO Disease Classification System",
        f"http://127.0.0.1:{port}",
        width=1200,
        height=800,
        resizable=True,
    )

    webview.start()
    backend_process.terminate()


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
