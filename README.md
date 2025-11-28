# radie_jsonui

[![CI/CD](https://github.com/radiece/radie_jsonui/actions/workflows/ci.yml/badge.svg)](https://github.com/radiece/radie_jsonui/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/radiece/radie_jsonui/branch/main/graph/badge.svg)](https://codecov.io/gh/radiece/radie_jsonui)
[![PyPI version](https://badge.fury.io/py/radie-jsonui.svg)](https://badge.fury.io/py/radie-jsonui)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://pepy.tech/badge/radie-jsonui)](https://pepy.tech/project/radie-jsonui)

`radie_jsonui` is a tiny static-site generator that transforms a compact JSON
definition into a responsive Bootstrap&nbsp;5 documentation site. It is designed
for automation pipelines where product specs, API docs, or knowledge bases are
stored as structured data and must be rendered into polished HTML without
hand-written templates.

## Features

- JSON Schema 2020-12 contract with lint-friendly component definitions
- Theme tokens (brand colors, typography scale, spacing rhythm)
- Composable hero, markdown, code, stats, cards, callouts, timeline, and footer
- Composable hero, markdown, code, stats, cards, callouts, timeline, FAQ,
  accordion, tabs, and columns layout blocks
- Multi-page site support with `$ref` for shared content
- Jinja2/Bootstrap 5.3 renderer with Prism.js highlighting and responsive
  layout defaults
- CLI with generate / validate / init / watch commands
- **Development server** with hot reload capabilities
- **Offline mode** to download and bundle remote assets (Bootstrap, Prism)
- **HTML/CSS minification** for production builds
- **Prettify option** for readable HTML output

## Installation

```bash
pip install radie_jsonui
```

> Inside this repo run `pip install -e radie_jsonui` (or `uv pip install -e radie_jsonui`) to use the local sources.

## Quick start

```bash
radie_jsonui init docs.json
radie_jsonui generate docs.json --out build/docs
```

The first command copies the example configuration to `docs.json`, while the
second builds a static site under `build/docs`.

## JSON structure (abridged)

- `meta`: page title, description, favicon, social preview, language
- `theme`: palette (`primary`, `secondary`, `surface`, `muted`), typography, and
  layout spacing tokens
- `navigation`: brand/title plus an array of nav links
- `sections`: ordered list of component blocks, each with `type` and payload
- `footer`: optional footer content with links and attribution

Refer to [`schema.json`](./schema.json) for the full contract.

## Documentation

For a detailed guide on configuration, CLI usage, and section types, please refer to the [Usage Guide](USAGE.md).

## CLI commands

| Command                                                 | Description                     |
| ------------------------------------------------------- | ------------------------------- |
| `radie_jsonui generate <config> [--out DIR] [--force]`  | Validate and render HTML site   |
| `radie_jsonui generate <config> [--format]`             | Generate with prettified HTML   |
| `radie_jsonui generate <config> [--minify]`             | Generate with minified HTML/CSS |
| `radie_jsonui generate <config> [--offline]`            | Download assets for offline use |
| `radie_jsonui validate <config>`                        | Schema validation only          |
| `radie_jsonui watch <config> [--out DIR] [--port PORT]` | Dev server with hot reload      |
| `radie_jsonui init <path>`                              | Copy starter example JSON       |

## Extensibility

- Extend `radie_jsonui/renderers/bootstrap.py` with new component renderers and
  register them in `COMPONENT_RENDERERS`.
- Override templates under `radie_jsonui/templates` or provide custom Jinja
  loaders when embedding.
- Use the loader/model layer to plug alternative schemas while reusing the CLI
  tooling.

## Development

- Run `pytest tests` for unit tests.
- Use `radie_jsonui generate radie_jsonui/src/radie_jsonui/examples/basic.json --out dist/site` to
  verify the rendered output.
- Keep the schema and example config synchronized when adding components.

## License

MIT License - Copyright (c) 2025 Jinto AG, Radiece Labs

See [LICENSE](LICENSE) for details.
