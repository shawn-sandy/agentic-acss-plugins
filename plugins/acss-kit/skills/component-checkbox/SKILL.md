---
name: component-checkbox
description: Use when the user asks to generate, create, or scaffold a Checkbox — accessible checkbox with indeterminate state, aria-checked, custom indicator, and Input dependency.
disable-model-invocation: true
hint: >-
  Invoke explicitly via `/kit-add checkbox`, `/kit-create` (then ask for a
  checkbox), or call the `component-checkbox` skill by name. Describe the
  label, the initial state (checked/unchecked/indeterminate),
  controlled vs uncontrolled, and any error/required state.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion
---

# SKILL: component-checkbox

Generate an fpkit-style accessible Checkbox component directly into a developer's project.

## Workflow

1. **Read the source doc.** Prefer the neutral **`checkbox.component.md`** in this skill directory (the spec-driven source of truth). Read its `## Target: react` adapter (Generation Contract on its `generation:` line, `## Props Interface`, `## TSX Template`), its `## Styles` section, plus `## Accessibility` and `## Examples`. If `checkbox.component.md` is absent, fall back to `reference.md` (canonical templates, Generation Contract, Props Interface, CSS Variables, Accessibility, Usage Examples). Both yield byte-identical output (golden-guarded).
2. **Init check** — run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/detect_target.py <cwd>`. If foundation (`ui.tsx`) is missing, run Step A of `${CLAUDE_PLUGIN_ROOT}/skills/kit-core/SKILL.md` to initialize it before generating this component.
3. **Dependencies** — Checkbox depends on `[input]`. Before generating Checkbox, check whether `<targetDir>/input.tsx` already exists. If missing, invoke `component-input` skill first (or generate Input inline following `component-input/reference.md`), then continue.
4. **Generate** — apply the Generation Contract to produce:
   - `<targetDir>/checkbox.tsx` from the `## TSX Template` (under `## Target: react` in `checkbox.component.md`, or top-level in `reference.md`)
   - `<targetDir>/checkbox.module.scss` from the `## Styles` section (`checkbox.component.md`) or the `## SCSS Template` section (`reference.md`)
   Substitute `{{IMPORT_SOURCE:...}}`, `{{NAME}}`, `{{FIELDS}}` placeholders if present.
5. **Verify** — run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/verify_integration.py <projectRoot>` and print the summary to the developer.

## Reference

Templates and documentation live in `checkbox.component.md` (the neutral spec-driven source) alongside this SKILL.md, with `reference.md` kept as the byte-identical fallback. The shared generation contract, accessibility patterns, SCSS conventions, and CSS variable strategy are documented in `${CLAUDE_PLUGIN_ROOT}/skills/kit-core/references/`.
