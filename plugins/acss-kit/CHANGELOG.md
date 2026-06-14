# Changelog

All notable changes to the `acss-kit` plugin are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); the plugin adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [1.8.0] - 2026-06-14

### Added

- **`/theme-from-figma <figma-url>` — generate a theme from a Figma file's variables (Workstream C PR 6).** Pulls design tokens via the Figma MCP server's `get_variable_defs`, then runs the **pure-Python** pipeline (no Node/`npx` after the MCP call) to `light.css` / `dark.css` + `space-radius.css` + `typography.css`, gated by WCAG contrast. The standards-based evolution of the `/theme-extract` Figma path; the inbound half of the Figma ⇄ DESIGN.md ⇄ theme bridge (Appendix B).
- **`scripts/figma_to_tokens.py`** (generator/validator) — normalizes Figma's freeform `category/name` variables (`color/primary`, `spacing/md`, `radius/md`, `fontSize/body-md`, …) into the css-tailwind `@theme` form and **reuses `design_md_to_tokens.build_tokens`** — the same Appendix A color mapping, OKLCH gap synthesis, and spacing/rounded/typography lift as `/theme-from-design`. One Figma-specific table (`FIGMA_CATEGORIES`) is the only reconciliation point; no second mapping, no drift. Bare numeric dimensions are coerced to `px`. 18 self-tests.
- **`tests/run.sh` step 7f** now self-tests `figma_to_tokens.py` and runs a Figma bridge end-to-end check (`get_variable_defs` fixture → tokens → `tokens_to_css.py` → `validate_theme.py` contrast gate).

> **Code Connect (outbound):** the `/theme-from-figma` flow documents the optional code→design push (`add_code_connect_map`) to bind `component-<name>` ↔ Figma nodes, and a Figma → DESIGN.md path (`figma_to_tokens.py | tokens_to_design_md.py`). Both are MCP-driven, performed only with user confirmation.

## [1.7.0] - 2026-06-14

### Added

- **`/design-export [--format=design-md|dtcg|tailwind]` — publish the project's theme as a [DESIGN.md](https://github.com/google-labs-code/design.md) (Workstream A PR 5).** The **outbound** half of the bridge and the import-*into*-DESIGN.md path the upstream CLI lacks, turning the generator into a DESIGN.md *producer*. `--format=design-md` (default) is **pure Python — no Node required**; `--format=dtcg|tailwind` shells `npx @google/design.md export` and **requires Node/`npx`**.
- **`scripts/tokens_to_design_md.py`** (generator/validator) — the inverse of `design_md_to_tokens.py`. Reads the tokens JSON (`css_to_tokens.py` over `light.css` + `space-radius.css` + `typography.css`), applies the **inverse of Appendix A** (our 18 `--color-*` roles → DESIGN.md token names), and emits deterministic YAML front-matter (`colors`/`spacing`/`rounded`/`typography`, hex values quoted for YAML `#` safety) plus a prose skeleton with the canonical `##` sections and `TODO` rationale placeholders. Accepts `<tokens.json>` / `--stdin` / `--dir=<dir>`.
- **`tests/run.sh` step 7f** now self-tests `tokens_to_design_md.py` and runs an **export round-trip** (theme → DESIGN.md → re-import through `design_md_to_tokens.py` → `tokens_to_css.py` → `validate_theme.py` contrast gate), proving the closed loop still gates.

> **Semantic round-trip, not lossless:** the 18 `--color-*` roles are emitted under DESIGN.md names; M3 ladder tokens we do not model (`surface-tint`, the `*-container` pairs, `*-fixed*`) are not reproduced, and roles with no M3 slot (`success`, `warning`, `focus-ring`, `text-subtle`) keep our names — the adapter (`design_md_to_tokens.COLOR_SOURCES`) carries matching candidates so a DESIGN.md we exported round-trips them, while an external M3 DESIGN.md (which omits them) re-synthesizes. Only `light` mode is exported (standard DESIGN.md front-matter is mode-thin). The exact front-matter group/sub-keys are isolated in the `ROLE_TO_DMD` / `DMD_GROUPS` / `TYPO_KEYS` tables — the single reconciliation point against the spec. See `docs/plans/design-md-spec-alignment.md` (§Round-trip & export).

## [1.6.0] - 2026-06-14

### Added

- **`/theme-from-design <DESIGN.md>` — generate a full theme from a Google [DESIGN.md](https://github.com/google-labs-code/design.md) (Workstream A PR 4).** Produces `light.css` / `dark.css` (colors) plus `space-radius.css` and `typography.css`, gated by WCAG contrast. Route 1 (decided): consumes the upstream `npx @google/design.md export --format css-tailwind` output rather than parsing YAML in stdlib. **Requires Node/`npx`.**
- **`scripts/design_md_to_tokens.py`** (generator/validator) — parses the `css-tailwind` `@theme` block; maps Material-3 color names → our 18 roles (per the proposal's Appendix A); **synthesizes** the roles M3 omits (success/warning/info/focus-ring) via the OKLCH palette generator so every theme is complete and contrast-valid; lifts spacing/rounded/typography through a Tailwind→ours **name adapter** (TW `--spacing-*`/`--text-*`/`--font-weight-*`/… → our `--space-*`/`--font-<role>-*`), normalizing px→rem while preserving pill sentinels (`9999px`).
- **`scripts/validate_design_md.py`** (detector) — normalizes `npx @google/design.md lint` findings to our `{ok, reasons, warnings}` contract; **hard-fails on a missing primary** (the OKLCH seed) — stricter than the upstream linter's warning, by decision.
- **`tests/run.sh` step 7f** now self-tests both new scripts and runs an end-to-end check (fixture `css-tailwind` → adapter → `tokens_to_css.py` → `validate_theme.py` contrast gate).

> **Format boundary:** the upstream `css-tailwind` export and `lint --format json` shapes are `alpha` and were not verifiable in this build. Every name-mapping assumption is isolated in the adapter tables (`COLOR_SOURCES` / `TW_*` / `classify`), which are the single reconciliation point against the real CLI. See `docs/plans/design-md-token-parity.md`.

## [1.5.0] - 2026-06-14

### Changed

- **Bulk spacing/radius token sweep (Workstream A PR 3).** Twelve components now consume the `--space-*` / `--radius-*` token homes via nested fallbacks (`var(--comp-x, var(--space-md, <literal>))`): **alert, card, checkbox, dialog, field, icon-button, img, input, list, nav, popover, table** (button landed in 1.3.1). Mapping is deterministic (nearest scale step by value; the original literal stays as the innermost fallback), so generated output is **pixel-identical when no token files are loaded** and responds to a DESIGN.md/`/theme-*` scale when present. Intentional skips per the button-pilot discipline: `calc()` values, component-local size ladders, fixed dimensions, multi-value padding shorthands, `0` resets, and structural literals (`%`, `999px`, `1px` borders, focus outlines).
- **SCSS golden guard generalized to all components.** `tests/run.sh` step 2a now extracts each component's SCSS via `extract_full.mjs` (mirrors `/kit-add`) and diffs against per-component fixtures under `tests/fixtures/golden/component-*/`, locking the swept SCSS against silent regression. Scoped to SCSS (the sweep only changed SCSS); TSX goldens are deferred — see `docs/plans/component-tsx-followups.md`. nav has no golden (no `## TSX Template`).

### Deferred (design-sensitive — tracked for a follow-up)

- **Typography role-mapping** (component font sizes → semantic `--font-<role>-*`) — assigning each component's sizes to roles is ambiguous and needs design input; not swept here.
- **`alert` state-color wiring** (`--alert-info/success/warning/error-*` → `--color-info/success/warning/danger`) — deriving the tints via `color-mix` would change the hand-tuned no-theme appearance; deferred to a design pass. Alert received only the spacing/radius sweep.

## [1.4.0] - 2026-06-14

### Fixed

- **Token definitions are no longer self-referential (theming actually applies).** `format_palette` / `format_scales` / `format_typography` previously emitted token *definitions* as `--token: var(--token, <literal>)`. A custom property that references itself is a CSS dependency cycle → it computes to the *guaranteed-invalid value*, so consumers (`var(--token, <fallback>)`) fell through to their own literal and **generated theme/token files did not actually theme components**. Confirmed empirically in Chromium (self-ref consumer resolved to the literal `8px`; raw definition resolved to the themed `32px`). Definitions now emit **raw values** (`--color-primary: #4f46e5;`, `--space-md: 1rem;`); the `var(--token, <fallback>)` convention remains correct for **consumers** (components/utilities). Regenerated the bundled `assets/tokens/space-radius.css` + `typography.css`; updated round-trip self-tests, the `tokens_to_css.py` docstring, the `styles` SKILL, and `validate_theme.py`/`css_to_tokens.py` continue to resolve both raw and legacy `var()` forms. Affects future `/theme-create`, `/theme-from-design`, and `/theme-*` output; existing user theme files should be regenerated. See `docs/plans/token-self-reference-cycle.md`.

## [1.3.1] - 2026-06-14

### Changed

- **`component-button` consumes the token homes (Workstream A PR 2 — sweep pilot).** `button.scss` now reads `--space-sm` (gap), `--radius-md` (border-radius), and `--font-label-md-weight` (font-weight) via nested fallbacks — `var(--btn-x, var(--<token>, <original-literal>))`. With no DESIGN.md / token files present the original literals apply, so generated output is **pixel-identical** to before; with a theme present, button responds to it. Establishes the fallback-preserving, nearest-step, skip-intentional-non-scale mapping discipline the bulk sweep (PR 3) inherits.

### Fixed

- **`--color-primary-dark` debt.** `button`'s primary-hover background (and the `--btn-hover-bg` example in `kit-core/references/css-variables.md`) referenced `--color-primary-dark`, which is **not** one of the 18 canonical theme roles — it silently fell back. Repointed to `--color-primary-hover`.

### Added

- **`tests/run.sh` step 2a** — a golden guard (`tests/fixtures/golden/component-button/`) that extracts button via `extract_full.mjs` (mirrors `/kit-add`) and diffs against the locked output, so future edits can't silently regress the token sweep.

## [1.3.0] - 2026-06-14

### Added

- **Token homes for typography, spacing, and rounded (DESIGN.md parity).** The token layer is no longer colors-only. `_tokens.py` gains `SPACE_SCALE` / `RADIUS_SCALE` / `DEFAULT_TYPOGRAPHY` plus `format_scales()` / `format_typography()` writers and matching parsers. `tokens_to_css.py` now emits **`space-radius.css`** (`--space-*`, `--radius-*`) and **`typography.css`** (`--font-<role>-{family,size,weight,line,tracking}`) — each a single mode-independent `:root` block — **only when** the input JSON carries `spacing` / `rounded` / `typography` (additive; colors-only input is byte-identical). `css_to_tokens.py` round-trips the new sections. The CSS prefixes mirror the Tailwind v4 `@theme` namespaces so a DESIGN.md `css-tailwind` export remaps mechanically.
- **`scripts/validate_tokens.py`** — structural validator for the new token kinds (dimension-unit validity, recommended scale-step completeness, typography sub-property correctness); the dimension/typography counterpart to `validate_theme.py`'s contrast gate. Generator/validator contract with `--self-test`.
- **Default token assets** at `assets/tokens/space-radius.css` and `assets/tokens/typography.css` so projects with no DESIGN.md still get a sane scale.
- **`theme.schema.json`** extended with optional `spacing` / `rounded` / `typography` sections (additive; colors block unchanged). Documented in `skills/styles/references/theme-schema.md` and the `styles` SKILL.
- **`tests/run.sh` step 7f** runs the token-script self-tests plus a byte-stable round-trip of the default scales.

## [1.2.1] - 2026-05-21

### Added

- **New `hint:` front-matter field on every component skill.** Each `skills/component-*/SKILL.md` declares a `hint:` describing the invocation surfaces (`/kit-add <name>`, `/kit-create`, direct skill name) and the component-specific details to describe (variant, size, state, slots). `hint:` is a project-controlled convention; the Claude Code harness ignores unknown front-matter keys at runtime.
- **`.claude/rules/skill-front-matter.md` rule** codifies the component-tier vs orchestrator-tier front-matter convention (component-tier requires `disable-model-invocation: true` + `hint:`; orchestrator-tier — `kit-core`, `styles`, `utilities`, `setup`, `style-tune`, `kit-sync`, `prompt-book` — does not). Fires on `plugins/*/skills/**/SKILL.md`.

### Changed

- **15 component skills now set `disable-model-invocation: true`.** Each `skills/component-*/SKILL.md` is hidden from the model's initial context at session start to reduce context bloat now that acss-kit ships fifteen components. Dispatch is unchanged — `/kit-add <component>`, `/kit-create`, `/kit-list`, and the kit-core orchestrator's lookup table all route by exact path/name, not by description matching. Users invoke component skills explicitly (via the slash commands or by name); auto-routing from a vague "add a button" prompt no longer applies.
- **`acss-kit-component-author` scaffolder updated.** Newly scaffolded `component-<name>/SKILL.md` files now include `disable-model-invocation: true` and a `hint:` template by default.

## [1.2.0] - 2026-05-21

### Added

- **15 per-component skills.** Each component (alert, button, card, checkbox, dialog, field, icon, icon-button, img, input, link, list, nav, popover, table) now lives in its own `skills/component-<name>/` directory with a `SKILL.md` (description, 5-step workflow) and a `reference.md` (templates, Generation Contract, props, accessibility). Developers can now invoke `/kit-add button` via the dedicated `component-button` skill rather than the monolithic `components` skill.
- **JSDoc on `component-button/reference.md` templates.** `ButtonProps`, `Button`, `useDisabledState`, and `resolveDisabledState` now carry JSDoc annotations in the TSX template so generated files are AI-assistant- and IDE-friendly out of the box.
- **`kit-core/references/inline-components.md`.** The six inline-only components (Badge, Tag, Heading, Text/Paragraph, Details, Progress) are now documented in a dedicated file instead of the deleted `catalog.md`.

### Changed

- **`skills/components/` renamed to `skills/kit-core/`.** The monolithic components skill is now the orchestrator for `/kit-create`, `/kit-list`, `/kit-sync`, `/kit-update`, and Form/HTML/Style-Tune modes. Its description explicitly excludes per-component requests to prevent auto-trigger collision.
- **`kit-core/references/components/*.md` reference docs moved.** All 14 component reference docs (plus `form.md` and `foundation.md`) relocated to their per-component skill directories or one level up in `kit-core/references/`.
- **`/kit-add`, `/kit-list`, `/kit-create` updated** to route through per-component skills only (no more kit-core fallback).
- **`/kit-sync` updated** to enumerate components via `skills/component-*/SKILL.md` glob instead of reading `catalog.md`.
- **Maintainer skills updated:** `acss-kit-component-author` now scaffolds `component-<name>/SKILL.md` + `reference.md`; `acss-kit-component-update` resolves `component-<name>/reference.md`.
- **`component-reference-reviewer` agent updated** to check for sibling `SKILL.md` instead of catalog row.

### Removed

- **`skills/kit-core/references/components/catalog.md` deleted.** Component enumeration is now done by globbing `skills/component-*/SKILL.md`. The verification status information lives in each component's `reference.md` verification banner.

## [1.1.0] - 2026-05-21

### Removed

- **`/kit-add-html` deprecated alias removed.** The thin alias that forwarded to `/kit-add --target=html` no longer exists. Call `/kit-add --target=html <component>` directly.
- **`docs/migration-v1.md` removed.** The v0.x → v1.0 migration guide has been retired now that `acss-utilities` is no longer published from this marketplace.
- **`theme.schema.json` "deprecated" flag dropped.** The JSON-schema-level `"deprecated": true` is gone. The schema remains the internal contract for `tokens_to_css.py` / `css_to_tokens.py` round-trip; user-facing theme authoring is still the CSS Token Convention documented in `skills/styles/SKILL.md`.
- **`@deprecated` JSDoc tags on `UI.renderStyles` cleared** in both `assets/foundation/ui.tsx` and `skills/kit-core/references/foundation.md`. The prop itself is unchanged (reserved for future use); only the JSDoc marker was removed.

### Changed

- **Repo-wide `acss-utilities` references stripped.** The companion plugin was tombstoned in 1.0.0 and has now been removed from the marketplace entirely; READMEs, CLAUDE.md, AGENTS.md, hooks, and `tests/run.sh` paths now point at the acss-kit-native copies of the utility scripts and assets.

## [1.0.0] - 2026-05-14

### Added

- **All `/utility-*` commands absorbed from `acss-utilities`.** `/utility-add`, `/utility-bridge`, `/utility-list`, `/utility-tune` are now part of acss-kit — no separate `acss-utilities` install required. The `utilities` skill, all utility scripts (`generate_utilities.py`, `validate_utilities.py`, `migrate_classnames.py`), and all utility assets (`assets/utilities/`) are included.
- **`generate_bridge.py` — generated token-bridge.** `token-bridge.css` is now generated at theme-creation and theme-update time rather than being a static committed file. `generate_bridge.py` reads `vocab.json` + your active `light.css`/`dark.css` and emits a fresh bridge with hex fallbacks derived from your actual theme.
- **`vocab.json` — vocabulary mapping.** `assets/utilities/vocab.json` is the single source of truth for the acss-kit-role ↔ fpkit-name delta (`danger→error`, `surface-raised→surface-secondary`, derived `-bg` variants, `secondary→primary` fallback).
- **`detect_target.py --what=utilities`.** Utilities target detection (configured vs default, `bundlePath`, `bridgePath`) is now part of the unified `detect_target.py` rather than a separate `detect_utility_target.py`.
- **Migration guide.** `docs/migration-v1.md` covers the full upgrade path from `acss-utilities` v0.x.

### Changed

- **`/theme-create` and `/theme-update` regenerate `token-bridge.css` automatically** when a `utilitiesDir` is configured. No manual `/utility-bridge` run required after theme changes.
- **Prompt book** updated to remove `acss-utilities` install step and reflect that all utility commands are in acss-kit.
- **`acss-utilities` tombstoned at v1.0.0.** Existing installs continue to work; no new features will be added there.

## [0.13.0] - 2026-05-14

### Changed

- **`/kit-add --target=html` unifies HTML and React component generation.** The standalone `skills/components-html/` skill and its `detect_html_target.py` / `verify_html_integration.py` scripts are removed. Their workflows now live as the **HTML Target** section (`## HTML Target`, steps HT-A through HT-F) inside `skills/components/SKILL.md`. Pass `--target=html` to `/kit-add` to generate static HTML + SCSS + vanilla-JS output; the default (`--target=react`) is unchanged.
- **`/kit-add-html` deprecated.** The command is now a thin alias that forwards to `/kit-add --target=html` and prints a deprecation notice. Existing invocations continue to work.
- **Shared Python utilities extracted to `scripts/_target.py`.** `find_project_root`, `read_components_dir`, `read_html_dir`, `find_import_line`, and `iter_page_files` are no longer duplicated across four scripts. All callers import via a `sys.path` shim.
- **`detect_target.py` now handles both React and HTML target detection** via `--target=react|html`. `detect_html_target.py` is removed.
- **`verify_integration.py` now handles both React and HTML integration verification** via `--target=react|html`. `verify_html_integration.py` is removed.
- **`components` skill description updated** to cover HTML output alongside React.
- **Prompt book** updated: "When to use what" table now shows `--target=html`; section 2a notes the deprecation of `/kit-add-html`.
- **`tests/e2e.sh` step 9** added: end-to-end smoke test for the HTML target path (detect unconfigured → write config → verify unwired → wire → verify ok).

## [0.12.0] - 2026-05-14

### Changed

- **Pilot skills absorbed into parent skills.** `skills/component-creator/` and `skills/component-form/` are removed as standalone skills. Their workflows now live as **Creator Mode** (`## Creator Mode` section) and **Form Mode** (`## Form Mode` section) inside `skills/components/SKILL.md`. The `/kit-create` command continues to work unchanged — it now delegates to the merged section rather than the deleted skill file. Natural-language form generation continues to auto-trigger via the updated `components` skill description. No user-facing command behavior changed.
- **`style-tune` skill shrunk to a dispatch router.** The 357-line `style-tune/SKILL.md` is now a ~65-line router (Steps A and F). The theme-layer adjustment workflow (OKLCH shifts, paired-role rule, dark-mirror, pre-validation batch) moved to `styles/SKILL.md` under `## Style-Tune Mode`. The component-level SCSS token adjustment workflow moved to `components/SKILL.md` under `## Style-Tune Mode`. The `/style-tune` command and all natural-language triggers are unchanged.
- **`components` skill description updated** to cover natural-language component creation and form generation, allowing it to auto-trigger on the same phrases that previously triggered the pilot skills.
- **Prompt book** updated to reflect that Creator Mode and Form Mode are sections of the `components` skill rather than separate auto-triggering pilots.

## [0.11.2] - 2026-05-08

### Added

- **Pilot skill failure modes documented** in `docs/troubleshooting.md`. Three new sections describe the conditions under which `component-creator`, `component-form`, and `style-tune` decline to handle a prompt, and the explicit-command fallbacks (drop down to `/kit-add` and edit by hand, or use a v1 phrase from the published vocabulary). Until now these decline paths existed silently; the doc surfaces them so users know the skills haven't broken.
- **Graduation criteria appended to each pilot's `description:` front-matter** (`component-creator`, `component-form`, `style-tune`). Each pilot now declares the explicit observable condition under which it will be considered graduated to v1 (auto-trigger reliability across a full release cycle plus a coverage milestone specific to the pilot — inline-entry promotion for creator, field-type grammar for form, v2 component scope for style-tune). The change is descriptive only; no skill behavior is altered.

## [0.11.1] - 2026-05-08

### Changed

- **`/kit-list` now surfaces HTML-output status.** The no-arg listing appends `[HTML]` to each component whose row in the components reference catalog's `## HTML Output Status` table is marked **Verified** (Button, Card, Alert, Dialog), and the per-component view (`/kit-list <name>`) prints a dedicated `HTML output:` line. Helps users discover which components `/kit-add-html` can generate before invoking it. No script or generation behavior changed.
- **`commands/kit-list.md` slimmed to a thin entry point** that delegates to the new "`/kit-list` workflow" section in `skills/components/SKILL.md`, matching the delegation convention already followed by every other command file in the plugin.

## [0.11.0] - 2026-05-07

### Added

- **`assets/foundation/foundation.css`** — compiled CSS barrel providing the missing fpkit base layer: CSS reset, base typography for `<h1>`–`<h6>` / `<p>` / `<ul>` / `<blockquote>`, root layout tokens (`--spacing-*`, `--shadow-*`, `--fs-*`, `--spc-*`), shadow scale, grid helpers, and the 12-column system. Vendored from `@fpkit/acss@6.5.0` (SHA `9063512fa822963d8151c972bed9f5b0e531df0f`) with four documented patches (P1–P4).
- **`assets/foundation/sass/`** — full SCSS source tree alongside the compiled barrel so consumer projects with a Sass pipeline can fork or override individual partials.
- **`assets/foundation/SOURCE.md`** — upstream pin, patch enumeration (P1–P4 with rationale), manual refresh workflow (`gh api` + `npx sass` + `wrap_foundation_layer.py`), and verification checklist.
- **`scripts/wrap_foundation_layer.py`** — pipeline helper that wraps a compiled raw CSS file in `@layer foundation { }` and appends the P3 reduced-motion block. Second step of the `foundation.css` refresh pipeline.
- **`/kit-add` foundation install matrix** — three-case logic in Step A4: first-run copies both `ui.tsx` and `foundation.css` + `sass/` tree; existing install (ui.tsx present, foundation.css absent) prompts before copying; already-installed skips silently. Prevents silent visual regressions on existing projects.
- **Two new `validate_theme.py` focus-on-surface contrast pairs** — `--color-focus-ring` × `--color-surface` (3:1) and `--color-focus-ring` × `--color-surface-raised` (3:1), enforcing WCAG 1.4.11 for focus indicators on card/panel/popover surfaces introduced by the foundation layer.
- **`/color-scale` command** — generate a 10-step OKLCH color scale (steps 50–900) from any seed color. Accepts a hex value (`#4f46e5`), a CSS named color (`cornflowerblue`), or a theme role name (`background`, `primary`, `surface`). When given a role name the skill reads the hex fallback directly from the project's `light.css` (or `dark.css`). Output includes a ready-to-paste `:root { … }` CSS block with `var(--color-<name>-50, <hex>)` properties and a Markdown table summarising each step's hex and OKLCH values. Chroma and hue from the seed color are preserved across all steps; lightness spans 0.970 (step 50, near-white) to 0.135 (step 900, near-black) with automatic sRGB gamut clamping so every step is a valid, renderable color. Use `--format=css` to get CSS-only stdout for piping or redirection; the slash command writes to a file only when the user explicitly requests a path.
- **`scripts/generate_color_scale.py`** — generator/validator script that produces the 10-step scale. Accepts `<hex-color> [--name=<name>] [--format=css|json|both]` (default format: `both`). Validates `--name` as a kebab-case identifier and rejects unknown flags (exit 2). JSON output includes `seed_oklch` for transparency; `--format=both` emits the JSON section followed by a blank line and the CSS block. CSS output follows the `var(--x, <fallback>)` convention. Reuses `_oklch.py` for all OKLCH ↔ sRGB math. Exit 0/1/2 per generator contract.

### Changed

- **`/kit-add` first-run output** now copies `foundation.css` and the `foundation/sass/` tree alongside `ui.tsx`. Existing projects (where `ui.tsx` is present but `foundation.css` is absent) receive a prompt explaining the visual change and the manual revert path — no silent modification.
- **CSS `@layer` ordering is now the canonical cascade contract.** `foundation.css` declares `@layer foundation, components, utilities, theme` at the top. Consumer projects must load theme files and utility files after `foundation.css` so the cascade order is honoured. Theme files win over all other layers; utilities beat foundation and components.
- **`kit-sync` Step S6** updated to track `foundation.css` and each file under `foundation/sass/` in `.acss-kit/manifest.json` with `kind: "foundation"`. Mirrors the `/kit-add` three-case matrix — the backward-compat prompt fires when `ui.tsx` is present but `foundation.css` is absent.
- **`foundation.md` reference doc** extended with a `## CSS Layer` section covering the upstream pin, P1–P4 patch table, `@layer` ordering, the `/kit-add` install matrix, the manual revert path, and a foundation verification table.

## [0.10.0] - 2026-05-04

### Added

- **`/kit-add-html` command and `components-html` skill** — generate static HTML versions of fpkit-style components for projects that don't use React (server-rendered apps, static sites, design-system docs, email templates, prototypes). Reads the same component reference docs as `/kit-add`, but emits `<name>.html` (markup fragment), `<name>.scss` (byte-identical to the React generator's SCSS — the framework-agnostic CSS is shared), and `<name>.js` (small ES module wiring behavior, only for stateful components). On first run, prompts for the target directory (default `components/html`), persists the choice to `.acss-html-target.json`, and copies the foundation helper `_stateful.js` into the target. Same dependency resolution and bottom-up generation order as `/kit-add`. Skips files that already exist. After generation runs `verify_html_integration.py` and reports any pages missing `<link>` / `<script>` references.
- **`assets/html-foundation/_stateful.js`** — vanilla-JS counterpart to React's inlined `useDisabledState` hook. Exports `wireDisabled(el, opts)` that reads `aria-disabled` directly off the DOM, short-circuits `click` and `keydown` (Enter / Space) when disabled, and toggles the `is-disabled` class so SCSS can target either selector. Plus `wireDisabledAll(selector, root)` convenience. The HTML output stays accessibility-equivalent to the React version (WCAG 2.1.1) — disabled controls keep their tab stop and accessible name.
- **`scripts/detect_html_target.py`** — detector that reads or initializes `.acss-html-target.json` for the static-HTML generator. Framework-agnostic: unlike `detect_target.py`, it does not require a React project root — any directory the user can write into is valid. Reports `source: "configured"` when the config file exists with a `componentsHtmlDir` field, `source: "none"` otherwise. Includes `--self-test` covering missing-config, malformed-config, foundation-present, and foundation-missing cases.
- **`scripts/verify_html_integration.py`** — read-only post-step that scans the project tree for pages (`*.html`, `*.css`, `*.scss`, `*.tsx`, `*.vue`, `*.svelte`, `*.njk`, `*.liquid`, `*.erb`, `*.php`, `*.astro`, `*.md`, `*.mdx`) and verifies each generated `.scss` / `.js` artifact is referenced by `<link rel="stylesheet">`, `<script src>`, or an `@import` statement. `*.html` snippets are listed but not checked — they're fragments meant to be copy-pasted. Skips `node_modules`, `dist`, `build`, `.git`, `.next`, `.cache`, `out`. Detector contract; exit 0 / 1 with `reasons` array. Includes `--self-test`.
- **`skills/components-html/references/stateful-js-patterns.md`** — vanilla-JS recipes for stateful components (disabled state via `wireDisabled`, dialog open/close/backdrop via native `<dialog>.showModal()`, popover wiring via the native HTML Popover API, input validation announcement). Explicitly documents idempotence — every per-component `init()` is safe to call multiple times.
- **HTML Template + Vanilla JS sections in `button.md`, `card.md`, `alert.md`, `dialog.md`** — first batch of reference docs augmented for static-HTML output. Button covers the disabled-state pattern; Card covers the optional-stateful (interactive variant) pattern; Alert covers the multi-variant + behavior-hook pattern (`useAlertBehavior` ported to vanilla); Dialog covers the native-element-driven stateful pattern. Remaining components fall through to a "not yet" warning in `/kit-add-html` until backfilled via `/component-update`.
- **`HTML Output Status` table in `references/components/catalog.md`** — tracks which components carry `## HTML Template` and `## Vanilla JS` sections. Single source of truth for `/kit-add-html`'s reference-doc lookup.

## [0.9.0] - 2026-05-03

### Added

- **`/kit-sync` command and `kit-sync` skill** — bulk-install every shipped acss-kit component, the `ui.tsx` foundation, and a starter OKLCH theme into a project in a single command. Walks `references/components/catalog.md`, resolves each component's Generation Contract `dependencies:` recursively, dedupes the union, and generates files bottom-up. Then copies `assets/foundation/ui.tsx`, runs `generate_palette.py` + `tokens_to_css.py` on a seed hex (prompted, or via `--seed=<hex>`), and writes the result to `<projectRoot>/.acss-kit/manifest.json` so subsequent runs can detect drift. Flags: `--target=<dir>`, `--styles-dir=<dir>`, `--seed=<hex>`, `--skip-styles`, `--dry-run`. If the manifest already exists, every file is routed through the `/kit-update` drift check before writing — modified files are skipped, clean files overwritten, no user customizations clobbered.
- **`/kit-update` command** — safe re-copy after a plugin upgrade. Reads `.acss-kit/manifest.json`, computes drift via `diff_status.py` (normalized sha256 comparison), and overwrites only files whose on-disk content still matches the recorded hash. Modified files are skipped by default and listed in the summary. Flags: `<component>...` (filter), `--check` (report only, no writes), `--force` (overwrite modified files too, writes `<file>.bak` first).
- **`scripts/hash_file.py`** — generator/validator that hashes a file or stdin content with sha256 after applying the kit-sync normalization rules (LF endings, strip trailing whitespace per line, collapse trailing blank lines to one). Stdlib only. Both written content and on-disk content during drift detection share the same normalization, so a Prettier or editor save doesn't trigger spurious "modified" classifications.
- **`scripts/manifest_read.py`** — detector that reads `.acss-kit/manifest.json` from a project root and emits its contents as JSON. Distinguishes three failure shapes: `exists: false` (manifest missing, malformed JSON, or top-level/`files` not an object), and `exists: true, schemaMismatch: true` (manifest is on disk but written by a different `schemaVersion`, so callers must halt rather than fall through to fresh-install and bypass drift protection). Detector contract; exit 0/1.
- **`scripts/manifest_write.py`** — generator/validator that atomically merges a stdin JSON payload into `.acss-kit/manifest.json` (write-temp + rename). Preserves entries not mentioned in the payload, accepts a `removePaths` array for pruning, and stamps `generatedAt` with the current UTC timestamp on every write.
- **`scripts/diff_status.py`** — detector that classifies every file recorded in the manifest as `clean`, `modified`, or `missing` by comparing the normalized on-disk sha256 to the recorded hash. Includes `--self-test` that exercises the full hash → write → read → diff (clean / edited / deleted) round-trip plus the CRLF-vs-LF normalization invariant. Wired into `tests/run.sh` as Step 7d so the manifest contract is verified on every harness run.

## [0.8.0] - 2026-05-03

### Added

- **`/prompt-book` command and bundled prompt book** — a copy-paste catalogue of natural-language prompts mapped to every shipped slash command across `acss-kit` and `acss-utilities`. Run `/prompt-book` to print the full book, or `/prompt-book <section-number>` to print a single section. The book itself lives at `plugins/acss-kit/docs/prompt-book.md`, ships with the plugin install, and is the canonical entry point for new users who want to see what they can ask Claude Code to do without memorising command syntax.

## [0.7.0] - 2026-05-02

### Added

- **Pilot `component-creator` skill and `/kit-create` command** — natural-language creator mode that works on any component with a dedicated `references/components/<name>.md` reference doc (Button, Alert, Card, Dialog, Link, Input, Field, Checkbox, IconButton, Img, Icon, List, Table, Popover, Nav). Describe a UI element ("primary pill button that says 'Add to cart'", "soft warning alert titled 'Heads up' with body 'Your card expires next month'", "card with a heading 'Plan' and content 'Premium tier'") and the skill loads the matched component's reference doc at runtime, parses its Props Interface, and resolves the user's phrases against the declared prop set. Two global synonym tables (colour family and size family) collapse common adjectives onto whichever colour-like / size-like prop the matched component carries, so "primary" maps to `color` on Button and `severity` on Alert without per-component lookup tables in the skill. Single-element components (Button, Alert, Link, IconButton, Img, Icon, Input, Checkbox, Field) and compound components (Card, Table, List with their dotted children) are both supported. Two carve-outs from no-silent-defaults: A3.5 for state-control props (`open`, `expanded`, `visible`, `checked`) with paired `on*` callback no-ops, and A3.6 for component-declared safe defaults (Button's `type="button"`). Refinement turns ("make it larger", "swap to secondary", "change the title to '<X>'") merge into the in-memory spec and re-emit. A two-tier validation matrix (generic rules + any `## Generation Notes — Creator Mode` block on the matched reference doc) blocks broken combinations before any disk write. Components that live only as inline catalog entries (currently Badge, Tag, Heading, Text/Paragraph, Details, Progress) are deferred to v0.2 — promote them via the `component-author` maintainer skill first. Multi-component compositions in a single prompt are deferred to v0.3.
- **`scripts/detect_css_entry.py`** — new detector that locates candidate CSS / SCSS entry files (e.g. `src/styles/index.scss`, `src/index.css`, `app/globals.css`) and reports which `light.css`, `dark.css`, `token-bridge.css`, and `utilities.css` imports each candidate already carries. Detector contract; stdlib only; includes `--self-test`. Used by `/setup` Step 7.5 to wire generated theme imports into the project's main stylesheet without editing the TSX entrypoint.
- **`/setup` Step 7.5 — auto-wire theme imports** — after seeding `light.css` and `dark.css`, `/setup` now detects the project's main CSS/SCSS entry, prompts the user to pick when multiple candidates exist (or to specify a path when none is found), and idempotently appends `@import` lines for the theme files. The chosen path is persisted at `stack.cssEntryFile` in `.acss-target.json` so re-runs and `verify_integration.py` both honor the user's choice. Skipped under `--no-theme`.
- **`scripts/detect_stack.py`** — new detector that classifies the user's build stack so `/kit-add`, `/theme-create`, and `/utility-add` can tailor integration advice. Resolves `framework` (vite, next, remix, astro, cra, or unknown), `bundler`, `cssPipeline` (any of tailwind, sass, postcss, css-modules), `tsconfig` presence, and `entrypointFile`. Detector contract; stdlib only; includes `--self-test` covering all five frameworks plus mixed-pipeline cases. The components and styles SKILLs persist its result into `.acss-target.json` under a `stack` key with `detectedAt` for cheap freshness checks.
- **`scripts/verify_integration.py`** — read-only post-step that checks the user's entrypoint actually imports the artifacts produced by `/kit-add`, `/theme-create`, and `/utility-add`. Verifies `token-bridge.css`, `utilities.css` (and that the bridge import precedes the utilities import on a line-number basis), theme CSS (`light.css`/`dark.css`), and that `<componentsDir>/ui.tsx` is referenced from at least one source file under `src/`. Detector contract — exit 0 on full wire-up, exit 1 with a `reasons` array listing each missing import. Never edits user files; SKILLs surface the reasons as a fix-up list.
- **Components SKILL — Step A3.1 (detect stack) + Step G (verify integration)** — `/kit-add` now writes a `stack` block into `.acss-target.json` on first run and runs `verify_integration.py` after Step F's summary, surfacing missing imports as a numbered fix-up list rather than auto-editing the entrypoint.
- **Styles SKILL — "Integration verification (all flows)" section** — `/theme-create`, `/theme-brand`, `/theme-update`, and `/theme-extract` all run `verify_integration.py` after `validate_theme.py` succeeds, so generated theme CSS is checked against the user's actual entrypoint imports.

- **Pilot `style-tune` skill and `/style-tune` command** — natural-language adjustment of acss-kit components and theme roles. Routes "warmer button", "softer card", "tone down the primary", "more spacious cards", "more elevated dialog", "smaller buttons", "narrower dialog", "taller dialog" between theme-role edits (delegated to `/theme-update` with WCAG pre-validation) and component SCSS token edits. Six v1 token families (color, radius, spacing, elevation, size, height) across six components (button, card, alert, dialog, input, nav). Atomic batch pre-validation guarantees paired roles and light/dark mirrors never desync. `references/intent-vocabulary.md` documents the full modifier → token-family table.
- **`scripts/oklch_shift.py`** — new CLI helper that takes a hex color plus per-channel OKLCH offsets (`--hue`, `--chroma`, `--lightness`) and emits the shifted hex. Generator/validator contract; stdlib only. Exits 0 whenever a usable hex was produced (with `clamped: true` and a populated `reasons` array when the math hit a gamut boundary). Powers `style-tune`'s color deltas.
- **`scripts/_oklch.py`** — internal shared module exposing `hex_to_oklch`, `oklch_to_hex`, `in_gamut`. Extracted from `generate_palette.py` so both palette generation and `oklch_shift.py` use the same conversion math. `oklch_to_hex` defensively clamps `L` to `[0, 1]` upfront and falls back to a directly-synthesized achromatic hex on gamut failure (no recursion).
- **`tests/setup.sh --with-style-tune`** — opt-in fixture flag that seeds `light.css` and `dark.css` from a baseline palette so end-to-end style-tune prompts have a populated theme to edit. Component vendoring (`/kit-add`) still requires an interactive Claude session — `RECIPE.md` walks through that step.

### Changed

- **`.acss-target.json` schema is now additive with a `stack` block** — `{ framework, bundler, cssPipeline, tsconfig, entrypointFile, cssEntryFile, detectedAt }`. Existing `componentsDir` / `utilitiesDir` consumers are unaffected; the detectors and verifiers degrade gracefully when the block is absent (they emit a reason pointing back to `detect_stack.py`). `cssEntryFile` is populated by `/setup` Step 7.5 when the user picks (or supplies) a CSS/SCSS entry.
- **`scripts/verify_integration.py` — accepts wired-up artifacts in `stack.cssEntryFile`** in addition to the TSX `entrypointFile`. The cross-file scan covers `light.css`, `dark.css`, `token-bridge.css`, and `utilities.css` (so `/utility-*` flows that route imports through SCSS no longer trip the verifier). The bridge-before-utilities ordering check now runs inside whichever file holds both imports and is skipped when the imports are split across files. `find_import_line()` recognises Sass `@import`, `@use`, and `@forward` lines. When `stack.cssEntryFile` is configured but the file does not exist, an explicit reason directs the user to re-run `/setup` or remove the stale entry.

### Fixed

- **`detect_stack.py` — Next.js `src/` directory layouts** (`src/app/layout.{tsx,jsx}`, `src/pages/_app.{tsx,jsx}`) are now recognized as entrypoint candidates so stack detection no longer returns `entrypointFile: null` on standard Next projects that use the `src/` convention.
- **`detect_stack.py` — `*.module.sass` (Sass indented syntax) files now register as `css-modules`** in `cssPipeline`, alongside `*.module.css` and `*.module.scss`.
- **`detect_stack.py` — `source: "detected"` now requires a non-null `entrypointFile`.** Known framework + missing entrypoint downgrades to `source: "unknown"` (exit 1) so the SKILL prompts the developer for the entrypoint instead of persisting an unverifiable result.
- **`verify_integration.py` — `find_any_use()` no longer matches the bare last path segment.** Searches restrict to import/require statements containing the normalized component-dir fragment, eliminating false positives (e.g. a comment mentioning "fpkit") and false negatives (imports that omit the segment).
- **`verify_integration.py` — suggested import path now uses `os.path.relpath` from the entrypoint's directory** to the artifact, so the fix-up snippet is correct for entrypoints that live outside `src/` (e.g. Next's `app/layout.tsx` now gets `../src/styles/token-bridge.css` instead of the previous broken `./styles/...` form).
- **`scripts/generate_palette.py` refactored** — its inline OKLCH conversion helpers moved into the new shared `scripts/_oklch.py` module. Public CLI behavior is byte-identical against five canonical seeds (`#2563eb`, `#7c3aed`, `#16a34a`, `#dc2626`, `#0f766e`).
- **Test harness simplified** — replaced the Vite + React + TypeScript demo sandbox (`tests/setup.sh`) with a minimal `package.json` + `tsconfig.json` fixture. No app framework, no `npm create`, no `npm run dev`. Replaced the Storybook + Playwright + axe-playwright deep check (`tests/storybook.sh`, `plugins/acss-kit/.harness/`, `scripts/generate_stories.mjs`) with a browserless `tests/e2e.sh` that runs `tsc --noEmit`, compiles SCSS, validates theme contrast, and runs jsdom + axe-core on rendered components. Faster install footprint, narrower a11y coverage (no real-pixel contrast or focus-indicator detection — see `tests/README.md` for the trade-off table). Plugin runtime behavior unchanged.
- **Marketplace repo renamed** from `shawn-sandy/acss-plugins` to `shawn-sandy/agentic-acss-plugins`. Install commands now use `@shawn-sandy-agentic-acss-plugins` (the marketplace alias is derived from `<owner>-<repo>`). The marketplace `name` field in `.claude-plugin/marketplace.json` also moved from `acss-plugins` to `agentic-acss-plugins` to match. No plugin behavior changed; this is metadata-only.

## [0.4.0] - 2026-04-26

### Added

- **`/setup` command** — first-run project bootstrap for acss-kit. Detects package manager via lockfile inspection, prints the exact `<pm> add -D sass` command (does not execute), writes `.acss-target.json`, copies `ui.tsx` verbatim, and optionally seeds `src/styles/theme/light.css` + `dark.css` via the OKLCH pipeline. Per-step idempotency: re-running `/setup` skips artifacts that already exist and tabulates `created` vs `kept` in the final summary.
- **`detect_package_manager.py`** — new detector script. Inspects lockfiles in priority order (`pnpm-lock.yaml` → `yarn.lock` → `bun.lock` → `bun.lockb` → `package-lock.json`) then falls back to `package.json#packageManager` field. Outputs `{ manager, lockfile, installCommand, projectRoot, reasons }`. Includes `--self-test` mode for `tests/run.sh` smoke check.
- **`skills/setup/SKILL.md`** — cross-domain setup skill. Deliberately not nested under `components` or `styles`; documents the placement rationale inline for future maintainers.

## [0.3.1] - 2026-04-26

### Fixed

- **Plugin README** — documented `/kit-list` command. The command file (`commands/kit-list.md`) and full reference (`docs/commands.md`) already shipped in 0.3.0, but the plugin-level README omitted it from both the Component commands section and the Plugin Structure file-tree diagram.
- **WCAG success-criterion citations** — corrected ambiguous and overstated SC references across reference docs and developer guides:
  - `docs/concepts.md` and `skills/components/SKILL.md` — softened the `aria-disabled` rationale. Previous "fails / violates WCAG 2.1.1" framing was stronger than WCAG actually states (a control being unfocusable when disabled is not automatically a 2.1.1 keyboard-operability failure). Replaced with concrete UX framing — unfocusable disabled controls can't be reached by keyboard or screen-reader users to discover state or read any explanation.
  - `skills/components/references/components/icon-button.md` (×4) and `catalog.md` — clarified the XOR type's accessible-name guarantee. The constraint genuinely covers two SCs simultaneously: WCAG 1.1.1 (text alternative for the non-text icon glyph) and WCAG 4.1.2 (programmatic accessible name for the interactive button). Previous wording cited only 1.1.1 (later 2.1.1, in the original incorrect form) and was inconsistent with the file's own "criteria addressed" section that already lists 4.1.2.
  - `skills/styles/references/role-catalogue.md` — `WCAG 2.1 AA` → `WCAG 2.2 AA` for plugin-wide consistency. Contrast ratio targets (4.5:1 normal, 3.0:1 large/UI) are identical across both spec versions; this is a wording fix only.

## [0.3.0] - 2026-04-26

### Added

- **`acss-kit` consolidated plugin.** Replaces four predecessor plugins (`acss-kit-builder`, `acss-theme-builder`, `acss-app-builder`, `acss-component-specs`) with a single plugin focused on accessible React components and CSS themes for fpkit/acss projects.
- **`components` skill** — accessible React component generation from markdown specs (rehomed from `acss-kit-builder`). 18 component reference docs with embedded TSX/SCSS/Accessibility sections.
- **`styles` skill** — CSS theme generation with OKLCH palette math and WCAG 2.2 AA contrast validation (rehomed from `acss-theme-builder`). Four slash commands: `/theme-create`, `/theme-brand`, `/theme-update`, `/theme-extract`.
- **`component-form` pilot skill** — natural-language form generation (rehomed from `acss-kit-builder`). Auto-triggers on phrases like "create a signup form".
- **`scripts/detect_target.py`** — replaces the previous `acss-app-builder/scripts/detect_component_source.py`. Manages `.acss-target.json` for component output directory resolution. Stripped of all `@fpkit/acss` npm-package detection logic; the script now only resolves locally-vendored sources.

### Removed

- **`acss-app-builder` plugin removed entirely.** Project init (`/app-init`), layouts (`/app-layout`), pages (`/app-page`), forms slash command (`/app-form`), patterns (`/app-pattern`), and compose (`/app-compose`) are no longer included. Users wanting these features can rebuild them on top of `acss-kit`'s components.
- **`acss-component-specs` plugin removed entirely.** Framework-agnostic spec generation (`/spec-add`, `/spec-render`, `/spec-validate`, `/spec-list`, `/spec-promote`, `/spec-diff`) is out of scope for the React-only focus.
- **`@fpkit/acss` npm package detection** — `detect_target.py` no longer detects or warns about npm-installed `@fpkit/acss`. The npm path is gone; components are vendored locally only.
- **Spec-bridge probe** — the previous `Step B0 — Probe acss-component-specs` workflow in the components skill is removed. No more cross-plugin spec lookups.
- **Cross-plugin `/app-form` delegation** — `component-form` skill no longer documents the cross-plugin invocation contract. The skill is invoked directly via auto-trigger.
- **Legacy reference banners** — every component reference doc previously carried a "Legacy reference" banner pointing to `acss-component-specs`. All banners removed.

### Changed

- **Plugin name** from `acss-kit-builder` → `acss-kit`.
- **Skill naming** — top-level skills are now `components` and `styles` (was `acss-kit-builder` and `acss-theme-builder`).
- **Path references** updated throughout: `${CLAUDE_PLUGIN_ROOT}/skills/components/...` and `${CLAUDE_PLUGIN_ROOT}/skills/styles/...`.
- **Theme schema deprecation** — `assets/theme.schema.json` retains `"deprecated": true` to discourage user authoring; the previous `"x-sunset-version": "0.3.0"` removed (we are at 0.3.0). The schema remains as an internal contract for the round-trip scripts.

### Migration notes

Users on any of the predecessor plugins should:

1. Uninstall the old plugins:

   ```shell
   /plugin uninstall acss-kit-builder
   /plugin uninstall acss-theme-builder
   /plugin uninstall acss-app-builder
   /plugin uninstall acss-component-specs
   ```

2. Install `acss-kit`:

   ```shell
   /plugin install acss-kit@shawn-sandy-agentic-acss-plugins
   ```

3. Existing `.acss-target.json` files at project roots remain compatible — the schema (`{ "componentsDir": "..." }`) is unchanged.

4. Existing generated component files in your project are not affected — the rename is purely on the plugin side.

5. If you used `/app-init`, `/app-layout`, `/app-page`, `/app-form`, `/app-pattern`, `/app-compose`, `/spec-add`, or any other deleted slash command — those features no longer exist. The form auto-trigger ("create a signup form") still works via the `component-form` skill.
