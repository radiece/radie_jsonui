# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-11-28

### Added

- Initial release of radie_jsonui
- JSON Schema 2020-12 contract for configuration
- Bootstrap 5.3 responsive renderer with Jinja2 templates
- Multiple component types:
  - Hero sections
  - Markdown content with Prism.js syntax highlighting
  - Card grids
  - Statistics displays
  - Code blocks
  - Callouts
  - Timelines
  - FAQ accordions
  - Layout components (columns, tabs, accordion)
- Multi-page site support with `$ref` for shared content
- CLI commands:
  - `radie_jsonui init` - Create starter configuration
  - `radie_jsonui generate` - Build static site
  - `radie_jsonui validate` - Schema validation
  - `radie_jsonui watch` - Development server with hot reload
- Development server with Server-Sent Events (SSE) for hot reload
- HTML/CSS minification support (`--minify`)
- HTML prettification support (`--format`)
- Offline mode to bundle remote assets (`--offline`)
- Theme customization (colors, typography, layout)
- Navigation and footer configuration
- Comprehensive test coverage (93%)
- Production-ready verification script

[Unreleased]: https://github.com/radiece/radie_jsonui/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/radiece/radie_jsonui/releases/tag/v0.1.0
