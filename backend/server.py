"""Local TTS server for the Google Docs -> Speech extension.

Pure standard-library HTTP server (no web-framework dependency). The browser
extension POSTs the document text here; we synthesize audio and return it.

Endpoints:
  GET  /health   -> JSON: status + available engines
  GET  /         -> tiny human-readable status page
  POST /tts      -> body: text, rate?, lang?, engine?
                    returns the audio file (audio/wav or audio/mpeg)
"""
from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from config import HOST, PORT, DEFAULT_RATE, DEFAULT_LANG
import tts_engine

_STATUS_CSS = (
    "body{font-family:system-ui,-apple-system,Segoe UI,sans-serif;"
    "background:#0A0A14;color:#E8E8F0;display:grid;place-items:center;"
    "height:100vh;margin:0}"
    ".box{padding:24px 28px;border-radius:14px;"
    "border:1px solid rgba(255,255,255,.1);background:rgba(255,255,255,.04);"
    "max-width:380px}"
    "b{color:#8B5CF6}code{color:#06B6D4}"
)


def _status_page(engines: str) -> str:
    return (
        '<!doctype html><html><head><meta charset="utf-8">'
        "<title>TTS backend</title><style>" + _STATUS_CSS + "</style></head>"
        '<body><div class="box"><h2>TTS backend running</h2>'
        "<p>Engines available: <b>" + engines + "</b></p>"
        "<p>POST text to <code>/tts</code> &middot; health at <code>/health</code></p>"
        "<p>Load the extension in <code>frontend/</code>, then open a Google Doc.</p>"
        "</div></body></html>"
    )


def _cors(h):
    h.send_header("Access-Control-Allow-Origin", "*")
    h.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    h.send_header("Access-Control-Allow-Headers", "Content-Type")


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print("[tts] " + self.address_string() + " " + (fmt % args))

    def _json(self, code, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        _cors(self)
        self.end_headers()
        self.wfile.write(body)

    def _html(self, code, html):
        body = html.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        _cors(self)
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        _cors(self)
        self.end_headers()

    def do_GET(self):
        path = self.path.rstrip("/")
        if path == "/health":
            self._json(200, {"status": "ok", "engines": tts_engine.available_engines()})
        elif path in ("", "/"):
            engines = ", ".join(tts_engine.available_engines()) or "NONE (see README)"
            self._html(200, _status_page(engines))
        else:
            self._json(404, {"error": "not found"})

    def do_POST(self):
        if self.path.rstrip("/") != "/tts":
            self._json(404, {"error": "not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length) if length else b""
            data = json.loads(raw.decode("utf-8")) if raw else {}
        except Exception as exc:
            self._json(400, {"error": "bad request: " + str(exc)})
            return

        text = data.get("text", "")
        if not text or not str(text).strip():
            self._json(400, {"error": "no text provided"})
            return

        try:
            path, engine = tts_engine.synthesize(
                text,
                rate=int(data.get("rate", DEFAULT_RATE)),
                lang=str(data.get("lang", DEFAULT_LANG)),
                engine=data.get("engine"),
            )
        except tts_engine.TTSUnavailableError as exc:
            self._json(503, {"error": str(exc)})
            return
        except Exception as exc:
            self._json(500, {"error": "synthesis failed: " + str(exc)})
            return

        audio = path.read_bytes()
        ctype = "audio/mpeg" if path.suffix == ".mp3" else "audio/wav"
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(audio)))
        self.send_header("X-TTS-Engine", engine)
        self.send_header("X-TTS-File", path.name)
        _cors(self)
        self.end_headers()
        self.wfile.write(audio)


def main():
    srv = ThreadingHTTPServer((HOST, PORT), Handler)
    engines = tts_engine.available_engines()
    print("TTS backend on http://" + HOST + ":" + str(PORT))
    print("Engines: " + (", ".join(engines) or "NONE -- run: pip install pyttsx3 (or gTTS)"))
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        srv.shutdown()


if __name__ == "__main__":
    main()
