from __future__ import annotations

from pathlib import Path

import pytest

from radie_jsonui import BootstrapRenderer, load_config

EXAMPLE = Path("src/radie_jsonui/examples/basic.json")


def test_renderer_outputs_html(tmp_path: Path) -> None:
    site = load_config(EXAMPLE)
    output_dir = tmp_path / "site"
    output_files = BootstrapRenderer().render(site, output_dir)
    assert len(output_files) == 1
    html = (output_dir / "index.html").read_text(encoding="utf-8")
    assert "Ship product docs from JSON." in html
    assert "Bootstrap" in html or "jsonui" in html


def test_render_file_exists_error(tmp_path: Path) -> None:
    site = load_config(EXAMPLE)
    output_dir = tmp_path / "site"
    output_dir.mkdir()
    (output_dir / "existing.txt").touch()

    renderer = BootstrapRenderer()
    with pytest.raises(FileExistsError):
        renderer.render(site, output_dir, force=False)


def test_copy_static_missing(tmp_path: Path) -> None:
    site = load_config(EXAMPLE)
    output_dir = tmp_path / "site"

    from unittest.mock import patch

    # Mock STATIC_PATH to point to a non-existent path
    with patch("radie_jsonui.renderers.bootstrap.STATIC_PATH", tmp_path / "nonexistent"):
        BootstrapRenderer().render(site, output_dir)
        # Should not raise, just skip copying
        assert (output_dir / "index.html").exists()
        assert not (output_dir / "assets").exists()


def test_renderer_multipage(tmp_path: Path) -> None:
    from radie_jsonui.models import MarkdownSection, Page

    site = load_config(EXAMPLE)
    # Add a second page
    site.pages.append(
        Page(
            path="about.html",
            title="About",
            sections=[MarkdownSection(content="About page")],
        )
    )

    output_dir = tmp_path / "site"
    output_files = BootstrapRenderer().render(site, output_dir)

    assert len(output_files) == 2
    assert (output_dir / "index.html").exists()
    assert (output_dir / "about.html").exists()
    assert "About page" in (output_dir / "about.html").read_text(encoding="utf-8")


def test_renderer_layouts(tmp_path: Path) -> None:
    layout_example = Path("src/radie_jsonui/examples/layout.json")
    site = load_config(layout_example)
    output_dir = tmp_path / "layout_site"
    BootstrapRenderer().render(site, output_dir)

    html = (output_dir / "index.html").read_text(encoding="utf-8")

    # Check Columns
    assert 'class="row g-4"' in html
    assert 'class="col-6"' in html
    assert "Left Column" in html

    # Check Tabs
    assert 'class="nav nav-tabs' in html
    assert 'id="tab-' in html
    assert "Content for Tab 1" in html

    # Check Accordion
    assert 'class="accordion"' in html
    assert 'class="accordion-button' in html
    assert "Content for Item 1" in html


def test_renderer_format(tmp_path: Path) -> None:
    """Test HTML formatting (prettify)."""
    site = load_config(EXAMPLE)
    output_dir = tmp_path / "formatted"
    BootstrapRenderer().render(site, output_dir, format=True)

    html = (output_dir / "index.html").read_text(encoding="utf-8")
    # Prettified HTML should have indentation and newlines
    assert "\n" in html
    assert "  <" in html  # Should have some indentation


def test_renderer_minify(tmp_path: Path) -> None:
    """Test HTML/CSS minification."""
    site = load_config(EXAMPLE)
    output_dir = tmp_path / "minified"
    BootstrapRenderer().render(site, output_dir, minify=True)

    html = (output_dir / "index.html").read_text(encoding="utf-8")
    assert "Ship product docs from JSON." in html

    # CSS should be minified
    css_file = output_dir / "assets" / "custom.css"
    if css_file.exists():
        css = css_file.read_text(encoding="utf-8")
        # Minified CSS should not have unnecessary whitespace
        assert "\n\n" not in css


def test_renderer_offline(tmp_path: Path) -> None:
    """Test offline mode (download remote assets)."""
    from unittest.mock import MagicMock, patch

    site = load_config(EXAMPLE)
    output_dir = tmp_path / "offline"

    # Mock httpx to avoid actual downloads
    mock_response = MagicMock()
    mock_response.text = "/* mock css */"
    mock_client = MagicMock()
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=False)
    mock_client.get = MagicMock(return_value=mock_response)

    with patch("radie_jsonui.renderers.bootstrap.httpx.Client", return_value=mock_client):
        BootstrapRenderer().render(site, output_dir, offline=True)

    html = (output_dir / "index.html").read_text(encoding="utf-8")
    # Should reference local assets
    assert "assets/vendor/bootstrap.min.css" in html

    # Vendor directory should exist
    vendor_dir = output_dir / "assets" / "vendor"
    assert vendor_dir.exists()
    assert (vendor_dir / "bootstrap.min.css").exists()


def test_renderer_dev_mode(tmp_path: Path) -> None:
    """Test dev mode (inject reload script)."""
    site = load_config(EXAMPLE)
    output_dir = tmp_path / "dev"
    BootstrapRenderer().render(site, output_dir, dev_mode=True)

    html = (output_dir / "index.html").read_text(encoding="utf-8")
    # Should have reload script
    assert "EventSource('/sse')" in html
    assert "location.reload()" in html


def test_renderer_nested_page_path(tmp_path: Path) -> None:
    """Test rendering page with nested path."""
    from radie_jsonui.models import MarkdownSection, Page

    site = load_config(EXAMPLE)
    site.pages.append(
        Page(
            path="docs/api.html",
            title="API",
            sections=[MarkdownSection(content="API docs")],
        )
    )

    output_dir = tmp_path / "nested"
    output_files = BootstrapRenderer().render(site, output_dir)

    assert len(output_files) == 2
    assert (output_dir / "docs" / "api.html").exists()
    assert "API docs" in (output_dir / "docs" / "api.html").read_text(encoding="utf-8")
