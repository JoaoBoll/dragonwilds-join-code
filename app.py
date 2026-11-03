#!/usr/bin/env python3
"""Read-only web page for the current Dragonwilds Join Code."""

from __future__ import annotations

import html
import os
import re
import subprocess
import threading
import time
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


HOST = os.environ.get("JOIN_CODE_HOST", "127.0.0.1")
PORT = int(os.environ.get("JOIN_CODE_PORT", "8787"))
REFRESH_COMMAND = [
    "/usr/bin/sudo",
    "-n",
    "/usr/local/libexec/dragonwilds-join-code",
]
WEB_ROOT = Path(__file__).resolve().parent / "web"
JOIN_CODE_PATTERN = re.compile(r"^[A-Z0-9]{4,12}-[A-Z0-9]{4,12}$")
MIN_REFRESH_SECONDS = 3.0

_cache_lock = threading.Lock()
_cached_at = 0.0
_cached_code: str | None = None


def read_join_code() -> str:
    """Run one hard-coded helper and accept only a Join Code as output."""
    global _cached_at, _cached_code

    with _cache_lock:
        now = time.monotonic()
        if _cached_code and now - _cached_at < MIN_REFRESH_SECONDS:
            return _cached_code

        result = subprocess.run(
            REFRESH_COMMAND,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
            env={"PATH": "/usr/sbin:/usr/bin:/sbin:/bin"},
        )
        code = result.stdout.strip()
        if result.returncode != 0 or not JOIN_CODE_PATTERN.fullmatch(code):
            raise RuntimeError("join code unavailable")

        _cached_code = code
        _cached_at = now
        return code


class JoinCodeHandler(BaseHTTPRequestHandler):
    server_version = "JoinCodeWeb"
    sys_version = ""

    def _security_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'none'; style-src 'self'; frame-ancestors 'none'; base-uri 'none'",
        )

    def _send(self, status: int, content_type: str, body: bytes) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self._security_headers()
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        path = urlparse(self.path).path

        if path == "/styles.css":
            self._send(
                HTTPStatus.OK,
                "text/css; charset=utf-8",
                (WEB_ROOT / "styles.css").read_bytes(),
            )
            return

        if path != "/":
            self._send(HTTPStatus.NOT_FOUND, "text/plain; charset=utf-8", b"Not found")
            return

        try:
            code = read_join_code()
        except (RuntimeError, subprocess.TimeoutExpired):
            code = "Indisponível"

        template = (WEB_ROOT / "index.html").read_text(encoding="utf-8")
        body = template.replace("{{JOIN_CODE}}", html.escape(code)).encode("utf-8")
        self._send(HTTPStatus.OK, "text/html; charset=utf-8", body)

    def log_message(self, format: str, *args: object) -> None:
        print(f"{self.client_address[0]} - {format % args}")


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), JoinCodeHandler)
    print(f"Listening on http://{HOST}:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
