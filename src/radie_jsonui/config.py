"""Package-wide configuration and constants."""

from __future__ import annotations

from pathlib import Path
from typing import Final

PACKAGE_ROOT: Final[Path] = Path(__file__).resolve().parent
SCHEMA_PATH: Final[Path] = PACKAGE_ROOT / "schema.json"
TEMPLATES_PATH: Final[Path] = PACKAGE_ROOT / "templates"
STATIC_PATH: Final[Path] = PACKAGE_ROOT / "static"

BOOTSTRAP_CSS: Final[str] = (
    "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css"
)
BOOTSTRAP_JS: Final[str] = (
    "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"
)
PRISM_CSS: Final[str] = "https://cdn.jsdelivr.net/npm/prismjs@1.29.0/themes/prism.min.css"
PRISM_JS: Final[str] = "https://cdn.jsdelivr.net/npm/prismjs@1.29.0/prism.min.js"

DEFAULT_THEME = {
    "colors": {
        "primary": "#0d6efd",
        "secondary": "#6610f2",
        "surface": "#ffffff",
        "muted": "#f8f9fa",
    },
    "typography": {
        "fontFamily": "Inter, system-ui, -apple-system, BlinkMacSystemFont",
        "headingsFont": "Space Grotesk, Inter, sans-serif",
        "baseSize": "1rem",
    },
    "layout": {
        "maxWidth": "960px",
        "gutter": "1.5rem",
        "radius": "0.75rem",
    },
}
