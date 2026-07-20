# Changelog

All notable changes to the `style-agent` plugin are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); the plugin adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.6.0] - 2026-07-20

### Added
- `/css` — turns a plain-language description into a CSS/SCSS rule or an inline `style` attribute, reusing the project's existing custom properties when they match, backed by bundled references for modern-CSS features with known footguns (`@container`, `@layer`, `clamp()` fluid type, `@supports`, logical properties, modern selectors, state selectors, viewport units). Class mode prints the rule by default and appends to a stylesheet only when you name a target file, confirming the target path and class name first. Inline mode refuses (with a stated reason, falling back to class mode) when the description implies `:hover`, `:focus-visible`, `@media`, `@container`, `@layer`, `@supports`, or a pseudo-element. Interactive elements get a `:focus-visible` rule, custom properties are never invented, and the summary names which references were consulted. Complements `/create-utilities`, which emits a utility-class string rather than a raw rule.

## [0.5.1] - 2026-06-22

### Added
- **Getting-started tutorial** (`docs/tutorial.md`) — a guided "your first class" walkthrough that chains all three then-shipped skills in composition order (`/create-utilities` → `/css-to-class` → `/inline-style-to-class`), front-loads the read-only vs. writes-to-disk distinction, and calls out the `@media`/`@supports`/`@layer` context-preservation and `var()`-fallback correctness notes. Mirrors the structure of `acss-kit`'s tutorial. Docs-only — no command or skill behavior changes.

## [0.5.0] - 2026-06-14

### Added
- **COMPONENT.md spec** — a framework-neutral format for describing a component's structure, props, behavior, and accessibility that an agent projects into any framework (React, HTML, Astro, Angular, Vue, Svelte, web-component), themed by a sibling DESIGN.md. Ships the spec (`docs/component-md/spec.md`), a complete worked example (`docs/component-md/examples/button.component.md`), and an advisory rule (`.claude/rules/component-md.md`). Docs-only — no command or skill behavior changes. Companion to DESIGN.md: DESIGN.md owns tokens, COMPONENT.md owns components, coupled via `{token.path}` references.

## [0.4.0] - 2026-05-27

### Changed
- `/inline-style-to-class` — now replaces hard-coded colors, units, and values in the migrated declarations with CSS variables. Reuses a project variable when one already holds the value; otherwise creates a new variable (named to match the project's convention, or a generic semantic scheme) and declares it in an existing tokens file or `:root` block, falling back to a new `:root` block at the top of the target stylesheet. Values already written as `var(...)` pass through untouched, and the original literal is kept as the `var()` fallback.

## [0.3.0] - 2026-05-14

### Added
- `/create-utilities` — generate a utility class string from a plain-language visual description. Detects acss-kit, Tailwind, Bootstrap, or falls back to Tailwind-compatible naming. Applies framework-specific focus defaults for interactive elements (`focus-visible:ring` for Tailwind/fallback, `focus-ring` for Bootstrap); for acss-kit, emits a summary warning that no focus utility exists in the bundle and recommends adding `:focus-visible` CSS or using an acss-kit component class. Includes contrast warnings in the summary.

## [0.2.0] - 2026-05-08

### Added
- `/inline-style-to-class` — convert an inline style attribute, JSX style object, or `<style>` block into a single named CSS class and append it to the project stylesheet.

## [0.1.0] - 2026-05-08

### Added
- `/css-to-class` — extract a list of CSS utility classes from an HTML element or class string into a single named CSS class. Resolves declarations by grepping the project's own CSS files; no external processor required.
