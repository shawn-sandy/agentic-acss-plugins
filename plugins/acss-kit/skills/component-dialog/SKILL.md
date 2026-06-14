---
name: component-dialog
description: Use when the user asks to generate, create, or scaffold a Dialog — accessible modal dialog with focus trap, aria-modal, return-focus on close, and Button dependency.
disable-model-invocation: true
hint: >-
  Invoke explicitly via `/kit-add dialog`, `/kit-create` (then ask for a
  dialog), or call the `component-dialog` skill by name. Describe the
  title, modal vs non-modal, the trigger element, the body content, and
  any footer action buttons (confirm/cancel).
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion
---

# SKILL: component-dialog

Generate an fpkit-style accessible Dialog component directly into a developer's project.

## Workflow

1. **Read the source doc.** Prefer the neutral **`dialog.component.md`** in this skill directory (the spec-driven source of truth). Read its `## Target: react` adapter (Generation Contract on its `generation:` line, `## Props Interface(s)`, `## Key Pattern:` blocks, `## TSX Template`), its `## Styles` section, plus `## Behavior`, `## Accessibility` and `## Examples`. If `dialog.component.md` is absent, fall back to `reference.md` (canonical templates, Generation Contract, Props Interface, CSS Variables, Accessibility, Usage Examples). Both yield byte-identical output (golden-guarded).
2. **Init check** — run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/detect_target.py <cwd>`. If foundation (`ui.tsx`) is missing, run Step A of `${CLAUDE_PLUGIN_ROOT}/skills/kit-core/SKILL.md` to initialize it before generating this component.
3. **Dependencies** — Dialog depends on `[button]`. Before generating Dialog, check whether `<targetDir>/button.tsx` already exists. If missing, invoke `component-button` skill first (or generate Button inline following `component-button/reference.md`), then continue.
4. **Generate** — apply the Generation Contract to produce:
   - `<targetDir>/dialog.tsx` from the `## TSX Template` (under `## Target: react` in `dialog.component.md`, or top-level in `reference.md`)
   - `<targetDir>/dialog.module.scss` from the `## Styles` section (`dialog.component.md`) or the `## SCSS Template` section (`reference.md`)
   Substitute `{{IMPORT_SOURCE:...}}`, `{{NAME}}`, `{{FIELDS}}` placeholders if present.
5. **Verify** — run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/verify_integration.py <projectRoot>` and print the summary to the developer.

## Reference

Templates and documentation live in `dialog.component.md` (the neutral spec-driven source) alongside this SKILL.md, with `reference.md` kept as the byte-identical fallback. The shared generation contract, accessibility patterns, SCSS conventions, and CSS variable strategy are documented in `${CLAUDE_PLUGIN_ROOT}/skills/kit-core/references/`.
