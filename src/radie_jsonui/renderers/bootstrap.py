"""Bootstrap-based renderer for radie_jsonui."""

from __future__ import annotations

import shutil
import uuid
from pathlib import Path
from typing import Any

import csscompressor  # type: ignore[import-untyped]
import httpx
import markdown as md
import minify_html
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader, select_autoescape

from ..config import (
    BOOTSTRAP_CSS,
    BOOTSTRAP_JS,
    PRISM_CSS,
    PRISM_JS,
    STATIC_PATH,
    TEMPLATES_PATH,
)
from ..models import (
    AccordionSection,
    ColumnsSection,
    MarkdownSection,
    Page,
    Section,
    SiteConfig,
    TabsSection,
)


class BootstrapRenderer:
    """Render a SiteConfig into a static HTML bundle."""

    def __init__(self) -> None:
        self.env = Environment(
            loader=FileSystemLoader(str(TEMPLATES_PATH)),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        self._markdown = md.Markdown(extensions=["extra", "sane_lists", "tables"])

    def render(
        self,
        site: SiteConfig,
        out_dir: Path,
        *,
        force: bool = False,
        format: bool = False,
        minify: bool = False,
        offline: bool = False,
        dev_mode: bool = False,
    ) -> list[Path]:
        out_dir = Path(out_dir)
        if out_dir.exists():
            if not force and any(out_dir.iterdir()):
                raise FileExistsError(
                    f"Destination {out_dir} is not empty. Use --force to overwrite."
                )
        out_dir.mkdir(parents=True, exist_ok=True)

        output_files = []
        for page in site.pages:
            payload = self._build_context(site, page, offline=offline, dev_mode=dev_mode)
            html = self.env.get_template("base.html.j2").render(payload)

            # Handle nested paths (e.g. docs/api.html)
            page_out = out_dir / page.path
            page_out.parent.mkdir(parents=True, exist_ok=True)

            if format:
                html = BeautifulSoup(html, "html.parser").prettify()
            if minify:
                html = minify_html.minify(
                    html,
                    minify_js=True,
                    minify_css=True,
                    remove_processing_instructions=True,
                )
            if dev_mode:
                html = self._inject_reload_script(html)

            page_out.write_text(html, encoding="utf-8")
            output_files.append(page_out)

        self._copy_static(out_dir)

        if offline:
            self._download_assets(out_dir)

        if minify:
            self._minify_css(out_dir)

        return output_files

    def _build_context(
        self,
        site: SiteConfig,
        page: Page,
        *,
        offline: bool = False,
        dev_mode: bool = False,
    ) -> dict[str, Any]:
        sections = [self._normalize_section(section) for section in page.sections]

        assets = {
            "bootstrap_css": BOOTSTRAP_CSS,
            "bootstrap_js": BOOTSTRAP_JS,
            "prism_css": PRISM_CSS,
            "prism_js": PRISM_JS,
        }

        if offline:
            assets = {
                "bootstrap_css": "assets/vendor/bootstrap.min.css",
                "bootstrap_js": "assets/vendor/bootstrap.bundle.min.js",
                "prism_css": "assets/vendor/prism.min.css",
                "prism_js": "assets/vendor/prism.min.js",
            }

        return {
            "meta": site.meta.model_dump(),
            "theme": site.theme.model_dump(),
            "navigation": site.navigation.model_dump() if site.navigation else None,
            "footer": site.footer.model_dump() if site.footer else None,
            "sections": sections,
            "current_page": page.model_dump(exclude={"sections"}),
            "assets": assets,
        }

    def _normalize_section(self, section: Section) -> dict[str, Any]:
        # Dump model first to avoid modifying the object in place with incompatible types
        data = section.model_dump()

        # Inject unique ID for UI components (tabs, accordion)
        data["_uid"] = str(uuid.uuid4())[:8]

        if isinstance(section, MarkdownSection):
            data["rendered_html"] = self._markdown.reset().convert(section.content)

        # Recursive normalization for layout components
        if isinstance(section, ColumnsSection):
            for col in data["columns"]:
                col["sections"] = [
                    self._normalize_section(s)
                    for s in section.columns[data["columns"].index(col)].sections
                ]
        elif isinstance(section, TabsSection):
            for i, tab in enumerate(data["tabs"]):
                tab["sections"] = [self._normalize_section(s) for s in section.tabs[i].sections]
        elif isinstance(section, AccordionSection):
            for i, item in enumerate(data["panels"]):
                item["sections"] = [self._normalize_section(s) for s in section.panels[i].sections]

        return data

    def _copy_static(self, out_dir: Path) -> None:
        src = STATIC_PATH
        if not src.exists():
            return
        dest = out_dir / "assets"
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(src, dest)

    def _download_assets(self, out_dir: Path) -> None:
        vendor_dir = out_dir / "assets" / "vendor"
        vendor_dir.mkdir(parents=True, exist_ok=True)

        assets = {
            "bootstrap.min.css": BOOTSTRAP_CSS,
            "bootstrap.bundle.min.js": BOOTSTRAP_JS,
            "prism.min.css": PRISM_CSS,
            "prism.min.js": PRISM_JS,
        }

        with httpx.Client() as client:
            for filename, url in assets.items():
                response = client.get(url)
                response.raise_for_status()
                (vendor_dir / filename).write_text(response.text, encoding="utf-8")

    def _minify_css(self, out_dir: Path) -> None:
        css_file = out_dir / "assets" / "custom.css"
        if css_file.exists():
            css_content = css_file.read_text(encoding="utf-8")
            minified_css = csscompressor.compress(css_content)
            css_file.write_text(minified_css, encoding="utf-8")

    def _inject_reload_script(self, html: str) -> str:
        """Inject hot reload script for development."""
        reload_script = """
<script>
(function() {
    const source = new EventSource('/sse');
    source.onmessage = function(event) {
        if (event.data === 'reload') {
            console.log('Reloading...');
            location.reload();
        }
    };
    source.onerror = function() {
        console.log('SSE connection lost, reconnecting...');
        setTimeout(() => location.reload(), 1000);
    };
})();
</script>
</body>"""
        return html.replace("</body>", reload_script)
