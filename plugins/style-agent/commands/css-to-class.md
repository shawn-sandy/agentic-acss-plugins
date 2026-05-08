---
description: Extract a list of CSS utility classes from an HTML element or class string into a single named CSS class
argument-hint: [name]
allowed-tools: Read, Glob, Grep, Bash, AskUserQuestion
---

Convert a multi-class HTML element or class string into a single, semantically named CSS class definition and emit the refactored HTML.

Follow `${CLAUDE_PLUGIN_ROOT}/skills/css-to-class/SKILL.md`.

**Arguments:**

- `name` — optional desired class name. Must be kebab-case; auto-coerced and truncated to 20 chars if needed.

**Quick steps:**

1. Extract the class list from the pasted HTML snippet or plain class string. Deduplicate (preserve order).
2. Determine the class name: use `name` if provided (validate → coerce to kebab-case → truncate to 20 chars, warn if changed). Otherwise auto-generate from the most semantic tokens; ask via `AskUserQuestion` with the suggestion if the list is all-utility and ambiguous.
3. Grep all `.css` files in the project (excluding `node_modules`, `.git`, `dist`, `build`) for each class token. Collect declarations. Tokens not found are unresolved.
4. Emit a single CSS class block: resolved declarations inlined, unresolved tokens as `/* <token>: add declarations manually */` placeholder comments.
5. Emit the refactored HTML with the new single class replacing all extracted classes; preserve all other attributes including `data-*`.
6. Print a summary: class count before → 1, name chosen, resolved declaration count, list of unresolved tokens, any name coercion warnings.
