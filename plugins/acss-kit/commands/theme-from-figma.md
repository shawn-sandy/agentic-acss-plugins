---
description: Generate an acss-kit theme from a Figma file's variables via the Figma MCP server
argument-hint: <figma-url|fileKey> [--node=<nodeId>] [--out-dir=<dir>]
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion
---

Pull design tokens from a Figma file's **variables** (`get_variable_defs`, via
the Figma MCP server) and generate the project's theme — `light.css` / `dark.css`,
`space-radius.css`, `typography.css` — gated by WCAG contrast. The standards-based
evolution of the `/theme-extract` Figma path.

Follow the **`/theme-from-figma`** flow in
`${CLAUDE_PLUGIN_ROOT}/skills/styles/SKILL.md`.

Requires the **Figma MCP server** for the `get_variable_defs` call; everything
after it is **pure Python — no Node/`npx`**. Figma variable names are mapped
through the same Appendix A adapter as `/theme-from-design`
(`scripts/figma_to_tokens.py` → `design_md_to_tokens.build_tokens`). All mapping,
OKLCH gap synthesis, and validation logic is defined in the skill file above.
