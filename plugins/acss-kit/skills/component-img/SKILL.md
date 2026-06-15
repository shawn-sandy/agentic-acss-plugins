---
name: component-img
description: Use when the user asks to generate, create, or scaffold an Img — accessible image component with required alt, lazy-loading, aspect-ratio containment, and decorative mode.
disable-model-invocation: true
hint: >-
  Invoke explicitly via `/kit-add img`, `/kit-create` (then ask for an
  image), or call the `component-img` skill by name. Describe the src,
  the alt text (or mark decorative), the aspect ratio, lazy vs eager
  loading, and any srcset/sizes for responsive variants.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion
---

# SKILL: component-img

Generate an fpkit-style accessible Img component directly into a developer's project.

## Workflow

1. **Read the source doc.** Prefer the neutral **`img.component.md`** in this skill directory (the spec-driven source of truth). Read its `## Target: react` adapter (Generation Contract on its `generation:` line, `## Props Interface(s)`, `## Key Pattern:` blocks, `## TSX Template`), its `## Styles` section, plus `## Accessibility` and `## Examples`. If `img.component.md` is absent, fall back to `reference.md` (canonical templates, Generation Contract, Props Interface, CSS Variables, Accessibility, Usage Examples). Both yield byte-identical output (golden-guarded).
2. **Init check** — run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/detect_target.py <cwd>`. If foundation (`ui.tsx`) is missing, run Step A of `${CLAUDE_PLUGIN_ROOT}/skills/kit-core/SKILL.md` to initialize it before generating this component.
3. **Dependencies** — Img has no upstream dependencies (it is a leaf component). Skip dep resolution.
4. **Generate** — apply the Generation Contract to produce:
   - `<targetDir>/img.tsx` from the `## TSX Template` (under `## Target: react` in `img.component.md`, or top-level in `reference.md`)
   - `<targetDir>/img.module.scss` from the `## Styles` section (`img.component.md`) or the `## SCSS Template` section (`reference.md`)
   Substitute `{{IMPORT_SOURCE:...}}`, `{{NAME}}`, `{{FIELDS}}` placeholders if present.
5. **Verify** — run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/verify_integration.py <projectRoot>` and print the summary to the developer.

## Reference

Templates and documentation live in `img.component.md` (the neutral spec-driven source) alongside this SKILL.md, with `reference.md` kept as the byte-identical fallback. The shared generation contract, accessibility patterns, SCSS conventions, and CSS variable strategy are documented in `${CLAUDE_PLUGIN_ROOT}/skills/kit-core/references/`.
