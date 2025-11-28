"""uv entry point for the radie_jsonui CLI."""

from __future__ import annotations

from radie_jsonui.cli import app


def main() -> None:
    """Invoke the Typer application."""
    app()


if __name__ == "__main__":
    main()
