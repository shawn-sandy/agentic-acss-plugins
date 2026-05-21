---
name: component-field
description: Use when the user asks to generate, create, or scaffold a Field — accessible form field wrapper with label, hint, and error message association via aria-describedby.
disable-model-invocation: true
hint: >-
  Invoke explicitly via `/kit-add field`, `/kit-create` (then ask for a
  field), or call the `component-field` skill by name. Describe the
  label, hint text, error message, required flag, and which child input
  control (input/checkbox/select) the field wraps.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion
---

# SKILL: component-field

Generate an fpkit-style accessible Field component directly into a developer's project.

## Workflow

1. **Read** `reference.md` in this skill directory for the canonical templates, Generation Contract, Props Interface, CSS Variables, Accessibility requirements, and Usage Examples.
2. **Init check** — run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/detect_target.py <cwd>`. If foundation (`ui.tsx`) is missing, run Step A of `${CLAUDE_PLUGIN_ROOT}/skills/kit-core/SKILL.md` to initialize it before generating this component.
3. **Dependencies** — Field has no upstream dependencies (it is a leaf component). Skip dep resolution.
4. **Generate** — apply the Generation Contract from `reference.md` to produce:
   - `<targetDir>/field.tsx` from the `## TSX Template` section
   - `<targetDir>/field.module.scss` from the `## SCSS Template` section
   Substitute `{{IMPORT_SOURCE:...}}`, `{{NAME}}`, `{{FIELDS}}` placeholders if present.
5. **Verify** — run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/verify_integration.py <projectRoot>` and print the summary to the developer.

## Reference

All templates and documentation live in `reference.md` alongside this SKILL.md. The shared generation contract, accessibility patterns, SCSS conventions, and CSS variable strategy are documented in `${CLAUDE_PLUGIN_ROOT}/skills/kit-core/references/`.
