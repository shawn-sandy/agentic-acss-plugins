---
description: List available fpkit/acss components or inspect a specific one
argument-hint: [component]
allowed-tools: Read, Glob, Grep
---

# /kit-list

List available components or show detailed information about a specific component. Read-only — never writes files.

## Usage

```text
/kit-list
/kit-list <component>
```

**Examples:**

```text
/kit-list
/kit-list badge
/kit-list dialog
/kit-list button
```

## Workflow

When this command is invoked, follow the **`/kit-list` workflow** documented in the `components` skill at `${CLAUDE_PLUGIN_ROOT}/skills/components/SKILL.md` (section *"`/kit-list` workflow — read-only inspection"*).

### Quick reference

1. **No arguments → categorized listing** — read the catalog and the `## HTML Output Status` table, group components by category, append `[HTML]` to any component whose HTML row is marked **Verified**.
2. **With a component name → per-component detail** — read the component's reference doc and print Generation Contract, Dependencies, HTML output, Props, CSS Variables, and a Usage Example.

See `SKILL.md` for the full output format, status-resolution rules, and unknown-name handling.
