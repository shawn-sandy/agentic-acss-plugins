---
name: component-table
description: Use when the user asks to generate, create, or scaffold a Table — accessible data table with caption, scope headers, responsive scroll wrapper, and sortable column support.
disable-model-invocation: true
hint: >-
  Invoke explicitly via `/kit-add table`, `/kit-create` (then ask for a
  table), or call the `component-table` skill by name. Describe the
  caption, the column headers (with scope), the row shape, whether any
  columns are sortable, and if a responsive scroll wrapper is needed.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion
---

# SKILL: component-table

Generate an fpkit-style accessible Table component directly into a developer's project.

## Workflow

1. **Read the source doc.** Prefer the neutral **`table.component.md`** in this skill directory (the spec-driven source of truth). Read its `## Target: react` adapter (Generation Contract on its `generation:` line, `## Props Interface`, `## TSX Template`), its `## Styles` section, plus `## Accessibility` and `## Examples`. If `table.component.md` is absent, fall back to `reference.md` (canonical templates, Generation Contract, Props Interface, CSS Variables, Accessibility, Usage Examples). Both yield byte-identical output (golden-guarded).
2. **Init check** — run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/detect_target.py <cwd>`. If foundation (`ui.tsx`) is missing, run Step A of `${CLAUDE_PLUGIN_ROOT}/skills/kit-core/SKILL.md` to initialize it before generating this component.
3. **Dependencies** — Table has no upstream dependencies (it is a leaf component). Skip dep resolution.
4. **Generate** — apply the Generation Contract to produce:
   - `<targetDir>/table.tsx` from the `## TSX Template` (under `## Target: react` in `table.component.md`, or top-level in `reference.md`)
   - `<targetDir>/table.module.scss` from the `## Styles` section (`table.component.md`) or the `## SCSS Template` section (`reference.md`)
   Substitute `{{IMPORT_SOURCE:...}}`, `{{NAME}}`, `{{FIELDS}}` placeholders if present.
5. **Verify** — run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/verify_integration.py <projectRoot>` and print the summary to the developer.

## Reference

Templates and documentation live in `table.component.md` (the neutral spec-driven source) alongside this SKILL.md, with `reference.md` kept as the byte-identical fallback. The shared generation contract, accessibility patterns, SCSS conventions, and CSS variable strategy are documented in `${CLAUDE_PLUGIN_ROOT}/skills/kit-core/references/`.
