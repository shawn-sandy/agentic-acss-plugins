---
name: component-icon-button
description: Use when the user asks to generate, create, or scaffold an IconButton — accessible icon-only button with required aria-label, tooltip fallback, and Button dependency.
disable-model-invocation: true
hint: >-
  Invoke explicitly via `/kit-add icon-button`, `/kit-create` (then ask
  for an icon button), or call the `component-icon-button` skill by name.
  Describe the icon, the required aria-label (always required for icon-
  only buttons), the variant/size, and any tooltip text.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion
---

# SKILL: component-icon-button

Generate an fpkit-style accessible IconButton component directly into a developer's project.

## Workflow

1. **Read the source doc.** Prefer the neutral **`icon-button.component.md`** in this skill directory (the spec-driven source of truth). Read its `## Target: react` adapter (Generation Contract on its `generation:` line, `## Props Interface`, `## TSX Template`), its `## Styles` section, plus `## Accessibility` and `## Examples`. If `icon-button.component.md` is absent, fall back to `reference.md` (canonical templates, Generation Contract, Props Interface, CSS Variables, Accessibility, Usage Examples). Both yield byte-identical output (golden-guarded).
2. **Init check** — run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/detect_target.py <cwd>`. If foundation (`ui.tsx`) is missing, run Step A of `${CLAUDE_PLUGIN_ROOT}/skills/kit-core/SKILL.md` to initialize it before generating this component.
3. **Dependencies** — IconButton depends on `[button]`. Before generating IconButton, check whether `<targetDir>/button.tsx` already exists. If missing, invoke `component-button` skill first (or generate Button inline following `component-button/reference.md`), then continue.
4. **Generate** — apply the Generation Contract to produce:
   - `<targetDir>/icon-button.tsx` from the `## TSX Template` (under `## Target: react` in `icon-button.component.md`, or top-level in `reference.md`)
   - `<targetDir>/icon-button.module.scss` from the `## Styles` section (`icon-button.component.md`) or the `## SCSS Template` section (`reference.md`)
   Substitute `{{IMPORT_SOURCE:...}}`, `{{NAME}}`, `{{FIELDS}}` placeholders if present.
5. **Verify** — run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/verify_integration.py <projectRoot>` and print the summary to the developer.

## Reference

Templates and documentation live in `icon-button.component.md` (the neutral spec-driven source) alongside this SKILL.md, with `reference.md` kept as the byte-identical fallback. The shared generation contract, accessibility patterns, SCSS conventions, and CSS variable strategy are documented in `${CLAUDE_PLUGIN_ROOT}/skills/kit-core/references/`.
