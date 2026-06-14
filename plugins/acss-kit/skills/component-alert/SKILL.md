---
name: component-alert
description: Use when the user asks to generate, create, or scaffold an Alert — accessible status/error/info/warning notification with ARIA live regions and icon support.
disable-model-invocation: true
hint: >-
  Invoke explicitly via `/kit-add alert`, `/kit-create` (then ask for an
  alert), or call the `component-alert` skill by name. Describe the
  severity (info/success/warning/error), whether it is dismissible, the
  ARIA live politeness (polite/assertive), and any leading icon.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion
---

# SKILL: component-alert

Generate an fpkit-style accessible Alert component directly into a developer's project.

## Workflow

1. **Read the source doc.** Prefer the neutral **`alert.component.md`** in this skill directory (the spec-driven source of truth). Read its `## Target: react` adapter (Generation Contract on its `generation:` line, `## Props Interface`, `## Key Pattern:` blocks, `## TSX Template`), its `## Styles` section, plus `## Accessibility` and `## Examples`. If `alert.component.md` is absent, fall back to `reference.md` (canonical templates, Generation Contract, Props Interface, CSS Variables, Accessibility, Usage Examples). Both yield byte-identical output (golden-guarded).
2. **Init check** — run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/detect_target.py <cwd>`. If foundation (`ui.tsx`) is missing, run Step A of `${CLAUDE_PLUGIN_ROOT}/skills/kit-core/SKILL.md` to initialize it before generating this component.
3. **Dependencies** — Alert has no upstream dependencies (it is a leaf component). Skip dep resolution.
4. **Generate** — apply the Generation Contract to produce:
   - `<targetDir>/alert.tsx` from the `## TSX Template` (under `## Target: react` in `alert.component.md`, or top-level in `reference.md`)
   - `<targetDir>/alert.module.scss` from the `## Styles` section (`alert.component.md`) or the `## SCSS Template` section (`reference.md`)
   Substitute `{{IMPORT_SOURCE:...}}`, `{{NAME}}`, `{{FIELDS}}` placeholders if present.
5. **Verify** — run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/verify_integration.py <projectRoot>` and print the summary to the developer.

## Reference

Templates and documentation live in `alert.component.md` (the neutral spec-driven source) alongside this SKILL.md, with `reference.md` kept as the byte-identical fallback. The shared generation contract, accessibility patterns, SCSS conventions, and CSS variable strategy are documented in `${CLAUDE_PLUGIN_ROOT}/skills/kit-core/references/`.
