---
description: Generate a utility class string from a plain-language visual description
argument-hint: [description]
allowed-tools: Read, Glob, Grep, Bash, AskUserQuestion
---

Generate a utility class string from a plain-language description of visual intent — detecting the project's utility framework and mapping the description to specific class names.

Follow `${CLAUDE_PLUGIN_ROOT}/skills/create-utilities/SKILL.md`.

All behavior — input parsing, vague-description handling, framework detection, class mapping, accessibility defaults, output emission, and summary — is defined in the skill file above.
