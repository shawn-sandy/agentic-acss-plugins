---
name: component-dialog
description: Use when the user asks to generate, create, or scaffold a Dialog — accessible modal dialog with focus trap, aria-modal, return-focus on close, and Button dependency.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion
---

# SKILL: component-dialog

Generate an fpkit-style accessible Dialog component directly into a developer's project.

## Workflow

1. **Read** `reference.md` in this skill directory for the canonical templates, Generation Contract, Props Interface, CSS Variables, Accessibility requirements, and Usage Examples.
2. **Init check** — run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/detect_target.py <cwd>`. If foundation (`ui.tsx`) is missing, run Step A of `${CLAUDE_PLUGIN_ROOT}/skills/kit-core/SKILL.md` to initialize it before generating this component.
3. **Dependencies** — Dialog depends on `[button]`. Before generating Dialog, check whether `<targetDir>/button.tsx` already exists. If missing, invoke `component-button` skill first (or generate Button inline following `component-button/reference.md`), then continue.
4. **Generate** — apply the Generation Contract from `reference.md` to produce:
   - `<targetDir>/dialog.tsx` from the `## TSX Template` section
   - `<targetDir>/dialog.module.scss` from the `## SCSS Template` section
   Substitute `{{IMPORT_SOURCE:...}}`, `{{NAME}}`, `{{FIELDS}}` placeholders if present.
5. **Verify** — run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/verify_integration.py <projectRoot>` and print the summary to the developer.

## Reference

All templates and documentation live in `reference.md` alongside this SKILL.md. The shared generation contract, accessibility patterns, SCSS conventions, and CSS variable strategy are documented in `${CLAUDE_PLUGIN_ROOT}/skills/kit-core/references/`.
