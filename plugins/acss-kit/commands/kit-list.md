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

When this command is invoked, follow the **`/kit-list` workflow** documented in the `kit-core` skill at `${CLAUDE_PLUGIN_ROOT}/skills/kit-core/SKILL.md` (section *"`/kit-list` workflow — read-only inspection"*).

Component inventory comes from two sources (transitional — PR 1):
- Per-component skills: `${CLAUDE_PLUGIN_ROOT}/skills/component-*/SKILL.md` (read `name:` + `description:` from frontmatter)
- kit-core reference docs: `${CLAUDE_PLUGIN_ROOT}/skills/kit-core/references/components/*.md` (excluding `catalog.md`)

Lowercase the argument before lookup to handle casing variants (e.g. `/kit-list Button` → look for `button`).

### Quick reference

1. **No arguments** — Categorized listing of all components, with `[HTML]` markers on Verified entries.
2. **With component name** — Per-component detail (Generation Contract, Dependencies, HTML output, Props, CSS Variables, Usage Example).

See `SKILL.md` for the full output format, status-resolution rules, and unknown-name handling.
