---
name: component-card
description: Use when the user asks to generate, create, or scaffold a Card — accessible content container with header/body/footer slots and interactive variant support.
disable-model-invocation: true
hint: >-
  Invoke explicitly via `/kit-add card`, `/kit-create` (then ask for a
  card), or call the `component-card` skill by name. Describe which slots
  you need (header/body/footer/media), whether the card is interactive
  (link or button wrapper), and any elevation/border styling.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion
---

# SKILL: component-card

Generate an fpkit-style accessible Card component directly into a developer's project.

## Workflow

1. **Read the source doc.** Prefer the neutral **`card.component.md`** in this skill directory (the spec-driven source of truth). Read its `## Target: react` adapter (Generation Contract on its `generation:` line, `## Props Interface`, `## Key Pattern:` blocks, `## TSX Template`), its `## Styles` section, plus `## Behavior`, `## Accessibility`, and `## Examples`. If `card.component.md` is absent, fall back to `reference.md` (canonical templates, Generation Contract, Props Interface, CSS Variables, Accessibility, Usage Examples). Both yield byte-identical output (golden-guarded).
2. **Init check** — run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/detect_target.py <cwd>`. If foundation (`ui.tsx`) is missing, run Step A of `${CLAUDE_PLUGIN_ROOT}/skills/kit-core/SKILL.md` to initialize it before generating this component.
3. **Dependencies** — Card has no upstream dependencies (it is a leaf component). Skip dep resolution.
4. **Generate** — apply the Generation Contract to produce:
   - `<targetDir>/card.tsx` from the `## TSX Template` (under `## Target: react` in `card.component.md`, or top-level in `reference.md`)
   - `<targetDir>/card.module.scss` from the `## Styles` section (`card.component.md`) or the `## SCSS Template` section (`reference.md`)
   Substitute `{{IMPORT_SOURCE:...}}`, `{{NAME}}`, `{{FIELDS}}` placeholders if present.
5. **Verify** — run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/verify_integration.py <projectRoot>` and print the summary to the developer.

## Reference

Templates and documentation live in `card.component.md` (the neutral spec-driven source) alongside this SKILL.md, with `reference.md` kept as the byte-identical fallback. The shared generation contract, accessibility patterns, SCSS conventions, and CSS variable strategy are documented in `${CLAUDE_PLUGIN_ROOT}/skills/kit-core/references/`.
