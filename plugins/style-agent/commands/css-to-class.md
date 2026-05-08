---
description: Extract a list of CSS utility classes from an HTML element or class string into a single named CSS class
argument-hint: [name]
allowed-tools: Read, Glob, Grep, Bash, AskUserQuestion
---

Convert a multi-class HTML element or class string into a single, semantically named CSS class definition and emit the refactored HTML.

Follow `${CLAUDE_PLUGIN_ROOT}/skills/css-to-class/SKILL.md`.

All behavior — argument handling, naming rules, CSS discovery, declaration resolution, HTML refactoring, and summary output — is defined in the skill file above.
