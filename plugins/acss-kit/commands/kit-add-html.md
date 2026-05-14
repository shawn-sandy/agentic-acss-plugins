---
description: Deprecated alias — use /kit-add --target=html instead
argument-hint: <component> [component2 ...]
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion
---

# /kit-add-html (deprecated)

This command is a compatibility alias. Use `/kit-add --target=html` instead.

When invoked, inform the user:

```text
/kit-add-html is deprecated. Use /kit-add --target=html <component> instead.
```

Then forward the request to the HTML Target workflow in
`${CLAUDE_PLUGIN_ROOT}/skills/components/SKILL.md` — the `## HTML Target` section
(steps HT-A through HT-F).
