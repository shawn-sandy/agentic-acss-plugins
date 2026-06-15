---
name: component-nav
description: Use when the user asks to generate, create, or scaffold a Nav — accessible navigation landmark with aria-label, current-page link marking, and horizontal/vertical layout.
disable-model-invocation: true
hint: >-
  Invoke explicitly via `/kit-add nav`, `/kit-create` (then ask for a
  nav), or call the `component-nav` skill by name. Describe the
  aria-label for the landmark, the link items (label + href), the
  current-page link, and horizontal vs vertical orientation.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion
---

# SKILL: component-nav

Generate an fpkit-style accessible Nav component directly into a developer's project.

## Workflow

1. **Read the source doc.** Prefer the neutral **`nav.component.md`** in this skill directory (the spec-driven source of truth). Read its `## Target: react` adapter (Generation Contract on its `generation:` line, `## Props Interface`, `## Key Pattern:` blocks), its `## Styles` section, plus `## Accessibility` and `## Examples`. nav is **legacy-shape** — it has no `## TSX Template` block; the generated `nav.tsx` is assembled from the Props Interface and the `## Key Pattern: Compound Component Assembly`. If `nav.component.md` is absent, fall back to `reference.md` (canonical templates, Generation Contract, Props Interface, CSS Variables, Accessibility, Usage Examples). Both yield byte-identical output.
2. **Init check** — run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/detect_target.py <cwd>`. If foundation (`ui.tsx`) is missing, run Step A of `${CLAUDE_PLUGIN_ROOT}/skills/kit-core/SKILL.md` to initialize it before generating this component.
3. **Dependencies** — Nav has no upstream dependencies (it is a leaf component). Skip dep resolution.
4. **Generate** — apply the Generation Contract to produce:
   - `<targetDir>/nav.tsx` from the `## Key Pattern: Compound Component Assembly` (under `## Target: react` in `nav.component.md`, or top-level in `reference.md`) — there is no `## TSX Template` block
   - `<targetDir>/nav.module.scss` from the `## Styles` section (`nav.component.md`) or the `## SCSS Pattern` section (`reference.md`)
   Substitute `{{IMPORT_SOURCE:...}}`, `{{NAME}}`, `{{FIELDS}}` placeholders if present.
5. **Verify** — run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/verify_integration.py <projectRoot>` and print the summary to the developer.

## Reference

Templates and documentation live in `nav.component.md` (the neutral spec-driven source) alongside this SKILL.md, with `reference.md` kept as the byte-identical fallback. The shared generation contract, accessibility patterns, SCSS conventions, and CSS variable strategy are documented in `${CLAUDE_PLUGIN_ROOT}/skills/kit-core/references/`.
