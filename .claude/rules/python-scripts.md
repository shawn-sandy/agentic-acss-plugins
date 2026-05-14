---
paths:
  - "plugins/*/scripts/**"
---

# Python Script Contracts

All scripts in `plugins/*/scripts/` use **Python 3 stdlib only** — no external dependencies.

Two contract families coexist. Choose based on who calls the script:

## Detector contract (machine-callable, structured)

For scripts whose output is parsed by slash commands or skills.

- Output JSON to stdout
- Exit 0 on success, 1 on logical failure (e.g. nothing detected)
- Always include a `"reasons"` array in the JSON — empty `[]` on success, populated on failure

## Generator / validator contract (pipeline-friendly, human-readable)

For scripts that emit data or human-readable validation results.

- Data on stdout (JSON for palette/token scripts; CSS for CSS-emitting scripts; text for validators)
- Errors on stderr
- Exit 0 on success, 1 on logical failure, 2 on usage / IO errors

## Internal module contract

Files prefixed with `_` (e.g. `_oklch.py`) are private modules — not callable from a slash command or shell. No exit codes, no stdout, no JSON. Test by importing into a sibling script.

## Adding a new script

Use the **detector** contract if a slash command parses the output. Use the **generator/validator** contract if it is a pipeline transformer or human-readable validator. Update `.claude/rules/python-scripts.md` only if the contract family itself changes — the per-script inventory lives in code, not here.
