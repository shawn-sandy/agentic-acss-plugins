---
name: component-icon
description: Use when the user asks to generate, create, or scaffold an Icon — accessible SVG icon wrapper with aria-hidden/aria-label toggle, size variants, and decorative/semantic modes.
disable-model-invocation: true
hint: >-
  Invoke explicitly via `/kit-add icon`, `/kit-create` (then ask for an
  icon), or call the `component-icon` skill by name. Describe the icon
  source (name or SVG path), the size, whether it is decorative
  (aria-hidden) or semantic (aria-label), and any color or stroke override.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion
---

# SKILL: component-icon

Generate an fpkit-style accessible Icon component directly into a developer's project.

## Workflow

1. **Read the source doc.** Prefer the neutral **`icon.component.md`** in this skill directory (the spec-driven source of truth). Read its `## Target: react` adapter (Generation Contract on its `generation:` line, `## Props Interface(s)`, and `## TSX Template`), plus `## Accessibility` and `## Examples`. Icon is presentational — it has no `## Styles`/SCSS section and no `## Behavior` section. If `icon.component.md` is absent, fall back to `reference.md` (canonical templates, Generation Contract, Props Interface, CSS Variables, Accessibility, Usage Examples). Both yield byte-identical output (golden-guarded).
2. **Init check** — run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/detect_target.py <cwd>`. If foundation (`ui.tsx`) is missing, run Step A of `${CLAUDE_PLUGIN_ROOT}/skills/kit-core/SKILL.md` to initialize it before generating this component.
3. **Dependencies** — Icon has no upstream dependencies (it is a leaf component). Skip dep resolution.
4. **Generate** — apply the Generation Contract to produce:
   - `<targetDir>/icon.tsx` from the `## TSX Template` (under `## Target: react` in `icon.component.md`, or top-level in `reference.md`)
   Icon has no SCSS template (renders via props/`currentColor` on the host element).
   Substitute `{{IMPORT_SOURCE:...}}`, `{{NAME}}`, `{{FIELDS}}` placeholders if present.
5. **Verify** — run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/verify_integration.py <projectRoot>` and print the summary to the developer.

## Reference

Templates and documentation live in `icon.component.md` (the neutral spec-driven source) alongside this SKILL.md, with `reference.md` kept as the byte-identical fallback. The shared generation contract, accessibility patterns, SCSS conventions, and CSS variable strategy are documented in `${CLAUDE_PLUGIN_ROOT}/skills/kit-core/references/`.
