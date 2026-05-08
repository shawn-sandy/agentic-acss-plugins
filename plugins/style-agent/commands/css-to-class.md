---
description: Extract a list of CSS utility classes from an HTML element or class string into a single named CSS class
argument-hint: [name]
allowed-tools: Read, Glob, Grep, Bash, AskUserQuestion
---

Convert a multi-class HTML element or class string into a single, semantically named CSS class definition and emit the refactored HTML.

Follow `${CLAUDE_PLUGIN_ROOT}/skills/css-to-class/SKILL.md`.

**Arguments:**

- `name` — optional desired class name. Must be kebab-case; auto-coerced and truncated to 20 chars if needed.

Extraction, naming (including `AskUserQuestion` for ambiguous cases), CSS file discovery, declaration resolution, HTML refactoring, and summary output are all defined in the skill file above.
