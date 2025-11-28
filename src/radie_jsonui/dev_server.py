"""Development server with hot reload support."""

from __future__ import annotations

import queue
import threading
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from typing import Any


class ReloadHandler(SimpleHTTPRequestHandler):
    """HTTP handler with SSE support for hot reload."""

    reload_queue: queue.Queue[str] | None = None

    def __init__(self, *args: Any, directory: str, **kwargs: Any) -> None:
        self.directory = directory
        super().__init__(*args, directory=directory, **kwargs)

    def do_GET(self) -> None:
        if self.path == "/sse":
            self.send_sse_stream()
        else:
            super().do_GET()

    def send_sse_stream(self) -> None:
        """Send Server-Sent Events stream for reload notifications."""
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.end_headers()

        # Send initial connection message
        self.wfile.write(b"data: connected\n\n")
        self.wfile.flush()

        # Listen for reload events
        while True:
            try:
                if self.reload_queue:
                    try:
                        # Wait for reload event with timeout to check connection
                        msg = self.reload_queue.get(timeout=1.0)
                        self.wfile.write(f"data: {msg}\n\n".encode())
                        self.wfile.flush()
                        if msg == "reload":
                            break
                    except queue.Empty:
                        # Send ping to keep connection alive
                        self.wfile.write(b": ping\n\n")
                        self.wfile.flush()
                else:
                    time.sleep(1)
            except (BrokenPipeError, ConnectionResetError):
                break

    def log_message(self, format: str, *args: Any) -> None:
        """Suppress default logging."""
        pass


class DevServer:
    """Development server with hot reload."""

    def __init__(self, directory: Path, port: int = 8000) -> None:
        self.directory = directory
        self.port = port
        self.reload_queue: queue.Queue[str] = queue.Queue()
        self.server: HTTPServer | None = None
        self.server_thread: threading.Thread | None = None

    def start(self) -> None:
        """Start the development server."""

        def handler(*args: Any, **kwargs: Any) -> ReloadHandler:
            h = ReloadHandler(*args, directory=str(self.directory), **kwargs)
            h.reload_queue = self.reload_queue
            return h

        self.server = HTTPServer(("localhost", self.port), handler)
        self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.server_thread.start()

    def reload(self) -> None:
        """Trigger a reload in connected browsers."""
        self.reload_queue.put("reload")

    def stop(self) -> None:
        """Stop the development server."""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
