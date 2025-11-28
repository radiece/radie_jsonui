# radie_jsonui Usage Guide

This guide provides detailed instructions on how to use `radie_jsonui` to generate beautiful documentation sites from JSON configuration files.

## Table of Contents

- [Installation](#installation)
- [CLI Reference](#cli-reference)
- [Configuration Guide](#configuration-guide)
  - [Meta](#meta)
  - [Theme](#theme)
  - [Navigation & Footer](#navigation--footer)
- [Section Types](#section-types)
  - [Hero](#hero)
  - [Markdown](#markdown)
  - [Cards](#cards)
  - [Callout](#callout)
  - [Stats](#stats)
  - [Code](#code)
  - [Timeline](#timeline)
  - [FAQ](#faq)
- [Multi-page Sites](#multi-page-sites)
- [Using References](#using-references)
- [Deployment](#deployment)

## Installation

Install `radie_jsonui` using `uv` (recommended) or `pip`:

```bash
# Using uv
uv pip install radie_jsonui

# Using pip
pip install radie_jsonui
```

## CLI Reference

The `radie_jsonui` command-line interface provides four main commands:

### `init`

Initialize a new project with a starter configuration file.

```bash
radie_jsonui init docs.json
```

### `validate`

Validate your configuration file against the schema without generating output.

```bash
radie_jsonui validate docs.json
```

### `generate`

Generate the static HTML site.

```bash
radie_jsonui generate docs.json --out build/site
```

**Options:**

- `--out DIR`: Output directory (default: `build/site`).
- `--force`: Overwrite the output directory if it is not empty.
- `--format`: Generate prettified HTML for better readability.
- `--minify`: Minify HTML and CSS for production.
- `--offline`: Download remote assets (Bootstrap, Prism) for offline use.

**Examples:**

```bash
# Generate with all optimizations for production
radie_jsonui generate docs.json --offline --minify

# Generate with readable HTML for debugging
radie_jsonui generate docs.json --format
```

### `watch`

Start a development server with hot reload. The server automatically rebuilds the site when the configuration file changes and reloads the browser.

```bash
radie_jsonui watch docs.json --out build/site
```

**Options:**

- `--out DIR`: Output directory (default: `build/site`).
- `--port PORT`: Development server port (default: `8000`).
- `--debounce FLOAT`: Delay in seconds before rebuilding (default: `0.25`).

**Example:**

```bash
# Start dev server on custom port
radie_jsonui watch docs.json --port 9000
```

## Configuration Guide

The configuration file is a standard JSON file. The root object contains the following keys:

### Meta

Metadata for the generated site, used for SEO and social sharing.

```json
"meta": {
  "title": "My Documentation",
  "description": "A comprehensive guide to my project.",
  "language": "en",
  "favicon": "https://example.com/favicon.ico",
  "ogImage": "https://example.com/og-image.png"
}
```

### Theme

Customize the look and feel of your site.

```json
"theme": {
  "colors": {
    "primary": "#0d6efd",
    "secondary": "#6610f2",
    "surface": "#ffffff",
    "muted": "#f8f9fa"
  },
  "typography": {
    "fontFamily": "Inter, system-ui, sans-serif",
    "headingsFont": "Space Grotesk, sans-serif",
    "baseSize": "1rem"
  },
  "layout": {
    "maxWidth": "960px",
    "gutter": "1.5rem",
    "radius": "0.75rem"
  }
}
```

### Navigation & Footer

Configure the top navigation bar and the footer.

```json
"navigation": {
  "brand": "My Project",
  "links": [
    { "label": "Home", "href": "#hero" },
    { "label": "GitHub", "href": "https://github.com/my/project", "external": true }
  ]
},
"footer": {
  "text": "© 2025 My Project. All rights reserved.",
  "links": [
    { "label": "Privacy", "href": "/privacy" }
  ]
}
```

## Section Types

The `sections` array defines the content of your page. Each section must have a `type` property.

### Hero

A large introductory banner with a heading, subheading, actions, and optional media.

```json
{
  "type": "hero",
  "id": "hero",
  "heading": "Welcome to My Project",
  "subheading": "The best tool for doing things.",
  "actions": [
    { "label": "Get Started", "href": "#docs", "variant": "primary" },
    { "label": "Learn More", "href": "#features", "variant": "secondary" }
  ],
  "media": {
    "src": "https://placehold.co/600x400",
    "alt": "Hero Image"
  }
}
```

### Markdown

Render standard Markdown content.

```json
{
  "type": "markdown",
  "id": "docs",
  "content": "### Getting Started\n\nRun `pip install my-project` to begin.",
  "background": "default"
}
```

### Cards

Display a grid or list of cards, useful for features or resources.

```json
{
  "type": "cards",
  "title": "Features",
  "layout": "grid",
  "items": [
    {
      "title": "Fast",
      "body": "Blazing fast performance.",
      "icon": "bi-lightning-fill"
    },
    {
      "title": "Secure",
      "body": "Enterprise-grade security.",
      "icon": "bi-shield-lock-fill"
    }
  ]
}
```

### Callout

Highlight important information with a colored box.

```json
{
  "type": "callout",
  "title": "Important Note",
  "body": "This feature is currently in beta.",
  "variant": "warning",
  "actions": [{ "label": "Read Docs", "href": "#beta-docs" }]
}
```

### Stats

Showcase key metrics or statistics.

```json
{
  "type": "stats",
  "title": "By the Numbers",
  "items": [
    { "label": "Downloads", "value": "1M+" },
    { "label": "Stars", "value": "5k" }
  ]
}
```

### Code

Display a code snippet with syntax highlighting.

```json
{
  "type": "code",
  "title": "Example Usage",
  "language": "python",
  "content": "print('Hello, World!')",
  "showLineNumbers": true
}
```

### Timeline

Visualize a sequence of events or a roadmap.

```json
{
  "type": "timeline",
  "title": "Roadmap",
  "items": [
    {
      "title": "v1.0 Release",
      "description": "Initial launch.",
      "timestamp": "Q1 2025",
      "status": "done"
    },
    {
      "title": "v2.0 Features",
      "description": "New exciting capabilities.",
      "timestamp": "Q3 2025",
      "status": "active"
    }
  ]
}
```

### FAQ

A list of frequently asked questions.

```json
{
  "type": "faq",
  "title": "Frequently Asked Questions",
  "items": [
    {
      "question": "Is it free?",
      "answer": "Yes, it is open source."
    }
  ]
}
```

## Multi-page Sites

You can create multi-page documentation sites by using the `pages` array instead of `sections`.

```json
{
  "meta": { ... },
  "pages": [
    {
      "path": "index.html",
      "title": "Home",
      "sections": [ ... ]
    },
    {
      "path": "about.html",
      "title": "About",
      "sections": [ ... ]
    },
    {
      "path": "docs/api.html",
      "title": "API Reference",
      "sections": [ ... ]
    }
  ]
}
```

## Using References

You can split your configuration into multiple files using `$ref`. This is useful for keeping your main configuration file clean and reusable components.

**main.json**

```json
{
  "meta": { ... },
  "pages": [
    {
      "path": "index.html",
      "sections": [
        { "$ref": "./sections/hero.json" },
        { "$ref": "./sections/features.json" }
      ]
    }
  ]
}
```

**sections/hero.json**

```json
{
  "type": "hero",
  "heading": "Welcome",
  ...
}
```

## Deployment

The output of `radie_jsonui generate` is a static HTML site (an `index.html` file and an `assets` folder). You can deploy this to any static hosting provider, such as:

- **GitHub Pages**
- **Netlify**
- **Vercel**
- **Amazon S3**

Simply upload the contents of the output directory to your web root.
