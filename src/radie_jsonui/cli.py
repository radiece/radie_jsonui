"""Command line interface for radie_jsonui."""

from __future__ import annotations

import shutil
from pathlib import Path

import typer
from rich.console import Console
from watchfiles import watch as watch_files

from . import BootstrapRenderer, validate_config
from .dev_server import DevServer
from .loader import load_config

console = Console()
app = typer.Typer(help="Generate Bootstrap documentation sites from JSON.")


def _config_path(path: Path | str) -> Path:
    resolved = Path(path).expanduser().resolve()
    if not resolved.exists():
        raise typer.BadParameter(f"Config file not found: {resolved}")
    return resolved


@app.command()
def validate(config: Path = typer.Argument(..., help="Path to JSON config")) -> None:
    """Validate a config file against the schema."""

    config_path = _config_path(config)
    try:
        validate_config(config_path)
    except Exception as exc:  # pragma: no cover - re-raised by Typer
        console.print(f"[red]Validation failed:[/red] {exc}")
        raise typer.Exit(code=1) from exc
    console.print(f"[green]✓[/green] {config_path} is valid")


@app.command()
def generate(
    config: Path = typer.Argument(..., help="Path to JSON config"),
    out: Path = typer.Option("build/site", help="Output directory"),
    force: bool = typer.Option(False, help="Overwrite existing output"),
    format: bool = typer.Option(False, help="Prettify HTML output"),
    minify: bool = typer.Option(False, help="Minify HTML output"),
    offline: bool = typer.Option(False, help="Download remote assets for offline use"),
) -> None:
    """Generate HTML from JSON."""

    config_path = _config_path(config)
    site = load_config(config_path)
    renderer = BootstrapRenderer()
    try:
        output = renderer.render(
            site, out, force=force, format=format, minify=minify, offline=offline
        )
    except FileExistsError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=1) from exc
    console.print(f"[green]✓[/green] Generated {output}")


@app.command()
def init(path: Path = typer.Argument(Path("docs.json"), help="New config path")) -> None:
    """Copy the starter example JSON to PATH."""

    dest = Path(path).expanduser()
    if dest.exists():
        console.print(f"[red]{dest} already exists[/red]")
        raise typer.Exit(code=1)

    # Ensure parent directory exists
    if dest.parent and not dest.parent.exists():
        dest.parent.mkdir(parents=True, exist_ok=True)

    example = Path(__file__).resolve().parent / "examples" / "basic.json"
    shutil.copyfile(example, dest)
    console.print(f"[green]✓[/green] Created {dest}")


@app.command("watch")
def watch_command(
    config: Path = typer.Argument(..., help="Path to JSON config"),
    out: Path = typer.Option("build/site", help="Output directory"),
    port: int = typer.Option(8000, help="Development server port"),
    debounce: float = typer.Option(0.25, help="File-system debounce in seconds"),
) -> None:
    """Start dev server with hot reload."""

    config_path = _config_path(config)

    # Start dev server
    dev_server = DevServer(directory=out, port=port)
    dev_server.start()
    console.print(f"[green]✓[/green] Dev server running at http://localhost:{port}")

    def _build() -> None:
        try:
            site = load_config(config_path)
            BootstrapRenderer().render(site, out, force=True, dev_mode=True)
            dev_server.reload()
            console.print(f"[green]✓[/green] Rebuilt {out}")
        except Exception as exc:  # pragma: no cover - interactive loop
            console.print(f"[red]Build failed:[/red] {exc}")

    debounce_ms = max(int(debounce * 1000), 50)

    console.print(f"Watching {config_path} (Ctrl+C to exit)...")
    _build()
    try:
        for changes in watch_files(config_path.parent, debounce=debounce_ms):
            relevant = any(path == str(config_path) for _, path in changes)
            if relevant:
                _build()
    except KeyboardInterrupt:  # pragma: no cover - user exit
        console.print("Stopping dev server")
        dev_server.stop()


def main() -> None:
    app()
