---
description: Extract a list of CSS utility classes from an HTML element or class string into a single named CSS class
argument-hint: [name]
allowed-tools: Read, Glob, Grep, Write, Edit, AskUserQuestion
---

Convert a multi-class HTML element or class string into a single, semantically named CSS class definition and emit the refactored HTML.

Follow the `/utility-cls` section of `${CLAUDE_PLUGIN_ROOT}/skills/utilities/SKILL.md`.

**Arguments:**

- `name` — optional desired class name. Must be kebab-case; auto-coerced and truncated to 20 chars if needed.

**Quick steps:**

1. Extract the class list from the pasted HTML snippet or plain class string. Deduplicate (preserve order).
2. Determine the class name: use `name` if provided (validate → coerce to kebab-case → truncate to 20 chars, warn if changed). Otherwise auto-generate from the most semantic tokens; ask via `AskUserQuestion` with the suggestion if the list is all-utility and ambiguous.
3. For each class token, look it up in `${CLAUDE_PLUGIN_ROOT}/assets/utilities.css` (and per-family partials under `assets/utilities/`). Collect its CSS declarations. Tokens absent from both locations are unresolved — emit them as `/* <token>: add declarations manually */` placeholder comments.
4. Emit a single CSS class block: resolved declarations inlined in source order, placeholder comments for unresolved tokens.
5. Emit the refactored HTML with the new single class replacing all extracted classes; preserve all other attributes including `data-*`.
6. Print a summary: class count before → 1, name chosen, resolved declaration count, list of unresolved tokens, any name coercion warnings.
