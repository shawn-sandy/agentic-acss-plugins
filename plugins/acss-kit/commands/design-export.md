---
description: Export the project's acss-kit theme to a DESIGN.md (or DTCG/Tailwind via the upstream CLI)
argument-hint: [--format=design-md|dtcg|tailwind] [--dir=<dir>] [--name=<Brand>]
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion
---

Publish the project's theme tokens (`light.css` + `space-radius.css` +
`typography.css`) as a [DESIGN.md](https://github.com/google-labs-code/design.md)
— the import-*into*-DESIGN.md direction the upstream CLI lacks — or, with
`--format=dtcg|tailwind`, hand off to `npx @google/design.md export`.

Follow the **`/design-export`** flow in
`${CLAUDE_PLUGIN_ROOT}/skills/styles/SKILL.md`.

`--format=design-md` (default) is **pure Python — no Node required**.
`--format=dtcg|tailwind` shells the upstream CLI and **requires Node/`npx`**. The
round-trip is **semantic, not lossless**: the 18 `--color-*` roles are emitted
under DESIGN.md token names; M3 ladder tokens we do not model are not reproduced.
All mapping and emission logic lives in the skill file above.
