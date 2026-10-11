"""Serves dist/ro-physics.html. Usage: python serve.py [--port 8080] [--host 0.0.0.0]

Stdlib only; no install step. The page is self-contained.
"""
import argparse
import os
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

DIST = Path(__file__).resolve().parent / "dist"
PAGE = "ro-physics.html"


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", "/index.html") or self.path.startswith("/?"):
            self.path = "/" + PAGE
        elif self.path == "/whoami":
            # Diagnostic: shows which headers reach the app (e.g. a user identity from the proxy).
            skip = {"cookie", "authorization"}
            body = "\n".join(f"{k}: {v}" for k, v in self.headers.items() if k.lower() not in skip)
            body += f"\n\nclient: {self.client_address[0]}\n"
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(body.encode())
            return
        elif self.path == "/healthz":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"ok\n")
            return
        super().do_GET()

    def end_headers(self):
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default=os.environ.get("RO_HOST", "0.0.0.0"))
    ap.add_argument("--port", type=int, default=int(os.environ.get("RO_PORT", "8080")))
    a = ap.parse_args()
    if not (DIST / PAGE).exists():
        raise SystemExit(f"{DIST / PAGE} not found; run: python build.py")
    srv = ThreadingHTTPServer((a.host, a.port), partial(Handler, directory=str(DIST)))
    print(f"Serving {PAGE} on http://{a.host}:{a.port}/")
    srv.serve_forever()
