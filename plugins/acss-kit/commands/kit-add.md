---
description: Generate fpkit-style accessible React components without installing @fpkit/acss
argument-hint: <component> [component2 ...]
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion
---

# /kit-add

Generate fpkit-style React components without installing `@fpkit/acss`. Components are generated directly into your project with local imports.

## Usage

```
/kit-add <component> [component2 ...]
```

**Examples:**
```
/kit-add badge
/kit-add button
/kit-add card
/kit-add dialog
/kit-add button card alert
```

## Workflow

When this command is invoked, use the following routing logic:

1. **Per-component skill** — if `${CLAUDE_PLUGIN_ROOT}/skills/component-<name>/SKILL.md` exists for the requested component, follow the workflow in that skill file. It reads its own `reference.md` for templates and delegates to `${CLAUDE_PLUGIN_ROOT}/skills/kit-core/SKILL.md` for shared generation steps (Steps C–G) and `verify_integration.py`.
2. **kit-core fallback** — if no per-component skill exists yet, follow the full generation workflow in `${CLAUDE_PLUGIN_ROOT}/skills/kit-core/SKILL.md` (looks up `references/components/<name>.md` directly).

Currently, `component-button` is the only component with a dedicated skill. All other components route through kit-core.

### Quick Reference

1. **Init check** — Verify sass is in devDependencies and `ui.tsx` exists in target dir
2. **Lookup** — Find the component in `references/components/catalog.md` or its dedicated reference doc
3. **Dependency tree** — Read the Generation Contract to identify all dependencies
4. **Show tree** — Display what will be generated before proceeding
5. **Generate bottom-up** — Generate leaf dependencies first, then the requested component
6. **Skip existing** — If a file already exists, skip it and import from it instead
7. **Summary** — Show grouped file list + import/usage snippet

### First-Run Setup

If this is the first time running `/kit-add` in a project:

1. Ask the developer for the target directory (default: `src/components/fpkit/`)
2. Verify `sass` or `sass-embedded` is in `devDependencies`. If missing, output:

```
sass or sass-embedded not found.
Run: npm install -D sass
Then re-run: /kit-add <component>
```

3. Copy `${CLAUDE_PLUGIN_ROOT}/assets/foundation/ui.tsx` into the target directory as `ui.tsx`
4. Foundation CSS install matrix (see `SKILL.md` Step A4 for full details):
   - **First-run** (no `ui.tsx` + no `foundation.css`): copy both + `sass/` tree; print import hint
   - **Existing install** (`ui.tsx` present, `foundation.css` absent): prompt before copying
   - **Already installed** (both present): skip silently

### Full Workflow

See `SKILL.md` for the complete step-by-step generation workflow including:
- Generated code characteristics (local imports, inlined types, rem units)
- CSS variable conventions and fallback strategy
- Accessibility patterns (aria-disabled, useDisabledState)
- Handling of compound components
- Conflict resolution for existing files
