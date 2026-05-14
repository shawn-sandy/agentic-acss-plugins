# Changelog

All notable changes to the `style-agent` plugin are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); the plugin adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.3.0] - 2026-05-14

### Added
- `/create-utilities` — generate a utility class string from a plain-language visual description. Detects acss-kit, Tailwind, Bootstrap, or falls back to Tailwind-compatible naming. Includes automatic focus-visible defaults for interactive elements and contrast warnings in the summary.

## [0.2.0] - 2026-05-08

### Added
- `/inline-style-to-class` — convert an inline style attribute, JSX style object, or `<style>` block into a single named CSS class and append it to the project stylesheet.

## [0.1.0] - 2026-05-08

### Added
- `/css-to-class` — extract a list of CSS utility classes from an HTML element or class string into a single named CSS class. Resolves declarations by grepping the project's own CSS files; no external processor required.
