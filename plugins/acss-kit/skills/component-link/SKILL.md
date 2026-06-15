---
name: component-link
description: Use when the user asks to generate, create, or scaffold a Link — accessible anchor with external/new-tab detection, aria-label injection, and current-page indication.
disable-model-invocation: true
hint: >-
  Invoke explicitly via `/kit-add link`, `/kit-create` (then ask for a
  link), or call the `component-link` skill by name. Describe the href,
  the link text, whether it opens in a new tab/external (so rel and
  aria-label can be set), and any current-page state.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion
---

# SKILL: component-link

Generate an fpkit-style accessible Link component directly into a developer's project.

## Workflow

1. **Read the source doc.** Prefer the neutral **`link.component.md`** in this skill directory (the spec-driven source of truth). Read its `## Target: react` adapter (Generation Contract on its `generation:` line, `## Props Interface`, `## TSX Template`), its `## Styles` section, plus `## Accessibility` and `## Examples`. If `link.component.md` is absent, fall back to `reference.md` (canonical templates, Generation Contract, Props Interface, CSS Variables, Accessibility, Usage Examples). Both yield byte-identical output (golden-guarded).
2. **Init check** — run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/detect_target.py <cwd>`. If foundation (`ui.tsx`) is missing, run Step A of `${CLAUDE_PLUGIN_ROOT}/skills/kit-core/SKILL.md` to initialize it before generating this component.
3. **Dependencies** — Link has no upstream dependencies (it is a leaf component). Skip dep resolution.
4. **Generate** — apply the Generation Contract to produce:
   - `<targetDir>/link.tsx` from the `## TSX Template` (under `## Target: react` in `link.component.md`, or top-level in `reference.md`)
   - `<targetDir>/link.module.scss` from the `## Styles` section (`link.component.md`) or the `## SCSS Template` section (`reference.md`)
   Substitute `{{IMPORT_SOURCE:...}}`, `{{NAME}}`, `{{FIELDS}}` placeholders if present.
5. **Verify** — run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/verify_integration.py <projectRoot>` and print the summary to the developer.

## Reference

Templates and documentation live in `link.component.md` (the neutral spec-driven source) alongside this SKILL.md, with `reference.md` kept as the byte-identical fallback. The shared generation contract, accessibility patterns, SCSS conventions, and CSS variable strategy are documented in `${CLAUDE_PLUGIN_ROOT}/skills/kit-core/references/`.
