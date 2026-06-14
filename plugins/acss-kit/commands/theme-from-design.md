---
description: Generate a full acss-kit theme (colors + spacing + rounded + typography) from a DESIGN.md file
argument-hint: <DESIGN.md> [--out-dir=<dir>]
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion
---

Consume a [DESIGN.md](https://github.com/google-labs-code/design.md) and generate
the project's theme token files — `light.css` / `dark.css` (colors),
`space-radius.css`, and `typography.css` — gated by WCAG contrast.

Follow the **`/theme-from-design`** flow in
`${CLAUDE_PLUGIN_ROOT}/skills/styles/SKILL.md`.

**Requires Node/`npx`** — the flow shells `npx @google/design.md export --format
css-tailwind` (and `lint`) to read the DESIGN.md. All mapping, OKLCH gap
synthesis, and validation logic is defined in the skill file above.
