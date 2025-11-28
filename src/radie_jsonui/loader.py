"""Load and validate radie_jsonui configuration files."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from .models import SiteConfig


class ConfigError(Exception):
    """Raised when configuration loading fails."""


def _load_json_file(path: Path) -> dict[str, Any]:
    """Load JSON file with error handling."""
    try:
        with path.open(encoding="utf-8") as f:
            result = json.load(f)
            assert isinstance(result, dict)
            return result
    except FileNotFoundError as exc:
        raise ConfigError(f"Config file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ConfigError(f"Invalid JSON in {path}: {exc}") from exc


def _resolve_refs(data: Any, base_path: Path) -> Any:
    if isinstance(data, dict):
        if "$ref" in data:
            ref_path = (base_path / data["$ref"]).resolve()
            if not ref_path.exists():
                raise ConfigError(f"Referenced file not found: {ref_path}")
            ref_data = _load_json_file(ref_path)
            # Recursively resolve refs in the loaded file, using its directory as base
            return _resolve_refs(ref_data, ref_path.parent)
        return {k: _resolve_refs(v, base_path) for k, v in data.items()}
    elif isinstance(data, list):
        return [_resolve_refs(item, base_path) for item in data]
    return data


def validate_payload(payload: dict[str, Any]) -> SiteConfig:
    try:
        return SiteConfig.model_validate(payload)
    except ValidationError as exc:
        # Format Pydantic errors to look somewhat like the old schema errors
        messages = []
        for err in exc.errors():
            loc = "/".join(str(p) for p in err["loc"])
            msg = err["msg"]
            messages.append(f"{loc}: {msg}")
        raise ConfigError("Schema validation failed:\n" + "\n".join(messages))


def validate_config(path: Path | str) -> None:
    config_path = Path(path).resolve()  # Added this line
    payload = _load_json_file(config_path)  # Changed from _load_raw(Path(path))
    validate_payload(payload)


def load_config(path: Path | str) -> SiteConfig:
    config_path = Path(path).resolve()
    payload = _load_json_file(config_path)
    # Resolve references relative to the config file location
    resolved_payload = _resolve_refs(payload, config_path.parent)
    return validate_payload(resolved_payload)
