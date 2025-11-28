"""radie_jsonui package."""

from .loader import load_config, validate_config
from .renderers.bootstrap import BootstrapRenderer

__all__ = [
    "load_config",
    "validate_config",
    "BootstrapRenderer",
]

__version__ = "0.1.0"


def main() -> None:
    """Console-script entry point."""
    from .cli import app

    app()
