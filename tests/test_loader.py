"""Tests for the loader module."""

import json
from pathlib import Path
from typing import Any

import pytest

from radie_jsonui.loader import ConfigError, load_config, validate_payload
from radie_jsonui.models import (
    CalloutSection,
    MarkdownSection,
    SiteConfig,
    TimelineSection,
)

EXAMPLE = Path("src/radie_jsonui/examples/basic.json")


def test_loads_example_config() -> None:
    site = load_config(EXAMPLE)
    assert site.meta.title == "Radie Docs Starter"
    assert len(site.pages) == 1
    assert len(site.pages[0].sections) > 0
    assert isinstance(site, SiteConfig)


def test_load_config_error(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text("invalid json", encoding="utf-8")
    with pytest.raises(ConfigError):
        load_config(config_path)


def test_load_raw_errors(tmp_path: Path) -> None:
    # File not found
    with pytest.raises(ConfigError, match="Config file not found"):
        load_config(tmp_path / "nonexistent.json")

    # Invalid JSON
    bad_json = tmp_path / "bad.json"
    bad_json.write_text("{invalid", encoding="utf-8")
    with pytest.raises(ConfigError, match="Invalid JSON"):
        load_config(bad_json)


def test_validate_payload_error() -> None:
    # Missing required field
    payload: dict[str, Any] = {"meta": {}}
    with pytest.raises(ConfigError, match="Schema validation failed"):
        validate_payload(payload)


def test_build_sections_invalid_type_error() -> None:
    # Invalid section type
    payload: dict[str, Any] = {
        "meta": {"title": "Test"},
        "pages": [{"sections": [{"type": "unknown_type"}]}],
    }
    with pytest.raises(ConfigError, match="Schema validation failed"):
        validate_payload(payload)


def test_merge_theme_defaults() -> None:
    # Test that defaults are applied correctly
    payload: dict[str, Any] = {
        "meta": {"title": "Test"},
        "pages": [],
        "theme": {"colors": {"primary": "red"}},
    }
    site = validate_payload(payload)
    assert site.theme.colors.primary == "red"
    # Check that other defaults are preserved
    assert site.theme.colors.secondary == "#6610f2"


def test_build_navigation_none() -> None:
    payload: dict[str, Any] = {
        "meta": {"title": "Test"},
        "pages": [],
        "navigation": None,
    }
    site = validate_payload(payload)
    assert site.navigation is None


def test_build_footer_none() -> None:
    payload: dict[str, Any] = {"meta": {"title": "Test"}, "pages": [], "footer": None}
    site = validate_payload(payload)
    assert site.footer is None


def test_build_full_sections() -> None:
    payload: dict[str, Any] = {
        "meta": {"title": "Test"},
        "pages": [
            {
                "sections": [
                    {"type": "callout", "title": "Callout", "body": "Body"},
                    {
                        "type": "timeline",
                        "title": "Timeline",
                        "items": [{"title": "T1", "description": "D1"}],
                    },
                ]
            }
        ],
    }
    site = validate_payload(payload)
    assert len(site.pages) == 1
    assert len(site.pages[0].sections) == 2
    assert isinstance(site.pages[0].sections[0], CalloutSection)
    assert isinstance(site.pages[0].sections[1], TimelineSection)


def test_loader_refs(tmp_path: Path) -> None:
    # Create a referenced file
    ref_file = tmp_path / "section.json"
    ref_file.write_text(
        json.dumps({"type": "markdown", "content": "Referenced content"}),
        encoding="utf-8",
    )

    # Create config referencing it
    config_file = tmp_path / "config.json"
    config_file.write_text(
        json.dumps(
            {
                "meta": {"title": "Ref Test"},
                "pages": [{"sections": [{"$ref": "section.json"}]}],
            }
        ),
        encoding="utf-8",
    )

    site = load_config(config_file)
    assert len(site.pages) == 1
    section = site.pages[0].sections[0]
    assert isinstance(section, MarkdownSection)
    assert section.content == "Referenced content"


def test_loader_missing_ref(tmp_path: Path) -> None:
    config_file = tmp_path / "config.json"
    config_file.write_text(
        json.dumps(
            {
                "meta": {"title": "Ref Test"},
                "pages": [{"sections": [{"$ref": "missing.json"}]}],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ConfigError, match="Referenced file not found"):
        load_config(config_file)


def test_loader_multipage() -> None:
    payload = {
        "meta": {"title": "Multi Page"},
        "pages": [
            {
                "path": "index.html",
                "title": "Home",
                "sections": [{"type": "markdown", "content": "Home"}],
            },
            {
                "path": "about.html",
                "title": "About",
                "sections": [{"type": "markdown", "content": "About"}],
            },
        ],
    }
    site = validate_payload(payload)
    assert len(site.pages) == 2
    assert site.pages[0].path == "index.html"
    assert site.pages[1].path == "about.html"
