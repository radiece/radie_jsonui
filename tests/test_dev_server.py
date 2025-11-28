"""Tests for dev_server module."""

from pathlib import Path
from time import sleep

from radie_jsonui.dev_server import DevServer


def test_dev_server_start_stop(tmp_path: Path) -> None:
    """Test dev server can start and stop."""
    server = DevServer(directory=tmp_path, port=8765)
    server.start()
    sleep(0.1)  # Give server time to start
    assert server.server is not None
    assert server.server_thread is not None
    assert server.server_thread.is_alive()
    server.stop()
    sleep(0.1)  # Give server time to stop
    assert not server.server_thread.is_alive()


def test_dev_server_reload(tmp_path: Path) -> None:
    """Test dev server reload queue."""
    server = DevServer(directory=tmp_path, port=8766)
    server.reload()
    assert not server.reload_queue.empty()
    msg = server.reload_queue.get()
    assert msg == "reload"


def test_dev_server_multiple_reloads(tmp_path: Path) -> None:
    """Test multiple reload events."""
    server = DevServer(directory=tmp_path, port=8767)
    server.reload()
    server.reload()
    assert server.reload_queue.qsize() == 2
