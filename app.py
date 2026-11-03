#!/usr/bin/env python3
"""Read-only web page for the current Dragonwilds Join Code."""

from __future__ import annotations

import html
import os
import re
import threading
import time
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


HOST = os.environ.get("JOIN_CODE_HOST", "0.0.0.0")
PORT = int(os.environ.get("JOIN_CODE_PORT", "8787"))
LOG_FILE = Path(os.environ.get("JOIN_CODE_LOG_FILE", "/logs/dragonwilds.log"))
WEB_ROOT = Path(__file__).resolve().parent / "web"
JOIN_CODE_PATTERN = re.compile(
    r'Setting \["JoinCode"\].*?value\[([A-Z0-9]{4,12}-[A-Z0-9]{4,12})\]'
)
MAX_LOG_BYTES = 2 * 1024 * 1024
MIN_REFRESH_SECONDS = 3.0

_cache_lock = threading.Lock()
_cached_at = 0.0
_cached_code: str | None = None


def read_join_code() -> str:
    """Read the end of the shared log and return only a validated Join Code."""
    global _cached_at, _cached_code

    with _cache_lock:
        now = time.monotonic()
        if _cached_code and now - _cached_at < MIN_REFRESH_SECONDS:
            return _cached_code

        try:
            with LOG_FILE.open("rb") as log:
                log.seek(0, os.SEEK_END)
                size = log.tell()
                log.seek(max(0, size - MAX_LOG_BYTES))
                contents = log.read().decode("utf-8", errors="replace")
        except OSError as error:
            raise RuntimeError("join code unavailable") from error

        matches = JOIN_CODE_PATTERN.findall(contents)
        if not matches:
            raise RuntimeError("join code unavailable")

        _cached_code = matches[-1]
        _cached_at = now
        return _cached_code


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
        except RuntimeError:
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
