"""Local server and launcher for the Three.js MoodSense interface."""

import json
import threading
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from emotion_data import EMOTIONS
from emotion_detector import analyze_emotion


ROOT = Path(__file__).parent
WEB_ROOT = ROOT / "web"


class MoodSenseHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_ROOT), **kwargs)

    def do_POST(self):
        if urlparse(self.path).path != "/api/analyze":
            self.send_error(404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 64000:
                self.send_error(400, "Request must contain at most 64000 bytes")
                return
            payload = json.loads(self.rfile.read(length) or b"{}")
            if not isinstance(payload, dict) or not isinstance(payload.get("text"), str):
                self.send_error(400, "Text must be a string")
                return
            if not payload['text'].strip() or len(payload['text']) > 5000:
                self.send_error(400, "Enter between 1 and 5000 characters")
                return
            key, scores = analyze_emotion(payload.get("text", ""))
            emotion = EMOTIONS[key]
            result = {"key": key, "label": emotion.label, "emoji": emotion.emoji, "message": emotion.message, "scores": scores}
            body = json.dumps(result).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except (ValueError, TypeError, json.JSONDecodeError):
            self.send_error(400, "Invalid analysis request")

    def log_message(self, format, *args):
        return

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()


def run_web_app() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", 0), MoodSenseHandler)
    url = f"http://127.0.0.1:{server.server_port}/index.html"
    threading.Timer(0.35, lambda: webbrowser.open(url)).start()
    print(f"MoodSense running at {url}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
