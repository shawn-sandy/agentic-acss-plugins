---
description: Author a raw CSS/SCSS rule or inline style from a plain-language description
argument-hint: [description]
allowed-tools: Read, Glob, Grep, Bash, Edit, Write, AskUserQuestion
---

Author a CSS or SCSS rule from a plain-language description of visual intent — reusing the project's existing custom properties when they match, and consulting bundled references for modern-CSS features with known footguns.

Follow `${CLAUDE_PLUGIN_ROOT}/skills/css/SKILL.md`.

All behavior — clarification gating, description parsing, output-mode branching, token resolution, focus-visible defaults, reference consultation, emission, and summary — is defined in the skill file above.
