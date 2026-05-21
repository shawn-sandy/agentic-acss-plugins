---
name: kit-core
description: Internal orchestrator for /kit-create, /kit-list, /kit-sync, /kit-update and Form/HTML/Style-Tune modes. Per-component generation lives in component-<name> skills; do not auto-trigger for component requests.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion
metadata:
  version: "0.4.0"
---

# SKILL: kit-core

Generate fpkit-style React components directly into a developer's project. No `@fpkit/acss` npm package required. Only React + sass needed.

## Purpose

This skill generates self-contained, production-quality React components from markdown specs that embed the actual TSX/SCSS code as fenced code blocks alongside accessibility documentation. The developer owns the generated code and can freely modify it. Components use local imports — never `@fpkit/acss`.

## Prerequisites

- React + TypeScript project
- `sass` or `sass-embedded` in `devDependencies`

---

## Step 0 — Exit plan mode

If the session is in plan mode, call `ExitPlanMode` before doing anything else. Every subsequent step writes files (`ui.tsx`, component TSX/SCSS), edits `.acss-target.json`, or runs Python scripts via Bash — plan mode would block all of it.

Stay in plan mode only when it is absolutely necessary — i.e. the user explicitly asked for a dry-run / preview ("show me the plan first", "what would `/kit-add` do", "don't generate yet"). In that case, narrate the dependency tree and file list from Step B4 without invoking Write/Edit/Bash, and wait for approval before re-entering this skill.

---

## Step A — First-Run Initialization

Run this check at the start of every `/kit-add` invocation.

### A1. Detect project type

Read `tsconfig.json` and `package.json` to confirm React + TypeScript is present.

### A2. Check sass

Read `package.json`. Look for `sass` or `sass-embedded` in `devDependencies`.

If neither is found, output:

```
sass or sass-embedded not found in devDependencies.
Run: npm install -D sass
Then re-run: /kit-add <component>
```

Stop. Do not generate any files.

### A3. Determine target directory

Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/detect_target.py <project_root>` to read or initialize `.acss-target.json`.

1. If the script returns `"source": "generated"`, use the reported `componentsDir`. Skip the prompt.
2. If the script returns `"source": "none"`, ask:

   ```
   Where should components be generated? (default: src/components/fpkit/)
   ```

3. After the developer answers (or accepts the default), write `.acss-target.json` at the project root:

   ```json
   { "componentsDir": "src/components/fpkit" }
   ```

   Commit this file — `/kit-add` reads it on subsequent runs as the source of truth for import paths.

Remember the answer for the current session as well, so subsequent `/kit-add` calls don't re-read the file unnecessarily.

### A3.1. Detect the build stack

Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/detect_stack.py <project_root>` to classify framework, bundler, CSS pipeline, and entrypoint. Capture the JSON.

1. If `source: "detected"`, merge the result into `.acss-target.json` under a `stack` key (preserve existing `componentsDir`/`utilitiesDir`):

   ```json
   {
     "componentsDir": "src/components/fpkit",
     "stack": {
       "framework": "vite",
       "bundler": "vite",
       "cssPipeline": ["sass"],
       "tsconfig": true,
       "entrypointFile": "src/main.tsx",
       "detectedAt": "2026-05-01T00:00:00Z"
     }
   }
   ```

   Skip re-detection on later runs unless `package.json`'s mtime is newer than `stack.detectedAt`.

2. If `source: "unknown"`, surface the `reasons` array verbatim and ask the developer to confirm framework + entrypoint by hand. Record their answer under `stack` so subsequent runs skip the prompt.

3. If `source: "none"` (no React project root), halt — `/kit-add` cannot proceed.

Use `stack.cssPipeline` to tailor advice: when it contains `"tailwind"`, note that fpkit components and Tailwind utilities coexist but the user should not migrate component SCSS into `@apply`. When it omits `"sass"`, fall through to Step A2's install instruction.

### A4. Copy UI foundation

Check whether `ui.tsx` and `foundation.css` exist in the target directory.
Three cases:

**First-run** (neither `ui.tsx` nor `foundation.css` present):
- Copy `${CLAUDE_PLUGIN_ROOT}/assets/foundation/ui.tsx` into `<target>/ui.tsx`
- Copy `${CLAUDE_PLUGIN_ROOT}/assets/foundation/foundation.css` into `<target>/foundation.css`
- Copy `${CLAUDE_PLUGIN_ROOT}/assets/foundation/sass/` tree into `<target>/foundation/sass/`
- Print:
  ```
  Created ui.tsx (foundation component — do not delete)
  Created foundation.css + foundation/sass/ (fpkit base layer — import once in your app entry)

  Add to your app entry:
    import './components/fpkit/foundation.css'
  ```

**Existing install** (`ui.tsx` present but `foundation.css` absent):
- Ask via AskUserQuestion:
  ```
  foundation.css (CSS reset, base typography, spacing tokens, @layer ordering)
  was not found in this project. Adding it will:
    - Apply a CSS reset and base element styles
    - Set @layer foundation, components, utilities, theme ordering
    - Add --spacing-*, --shadow-*, and font-scale tokens

  To revert: delete foundation.css and remove its import.
  Add foundation.css now?
  ```
- Options: "Yes, copy foundation.css" / "No, skip for now"
- If confirmed: copy `foundation.css` and `sass/` tree; print the import hint above.

**Already installed** (both `ui.tsx` and `foundation.css` present):
- Skip silently (idempotent).

#### CSS layer ordering (all flows)

The canonical layer order for consumer projects is:

```css
@layer foundation, components, utilities, theme;
```

`foundation.css` emits this declaration at the top. Components generated by
`/kit-add` wrap their SCSS in `@layer components { }`. Theme files
(`light.css` / `dark.css`) must declare into `@layer theme`. The
utility-class bridge and utility files (`utilities.css`, `token-bridge.css`,
per-family partials) must declare into `@layer utilities`.

Cascade outcome: **theme > utilities > components > foundation**.

---

## Step B — Component Generation Workflow

### B1. Lookup the component

Read the component's reference doc:
- Detailed refs: `references/components/{name}.md`
- Catalog: `references/components/catalog.md`

If the component is not in either, inform the developer. Run `/kit-list` to show available components.

### B2. Read the Generation Contract

Every reference doc has a **Generation Contract** section:

```
## Generation Contract
export_name: ComponentName
file: component-name.tsx
scss: component-name.scss
imports: UI from '../ui'
dependencies: [dep1, dep2]
```

This tells Claude exactly what files to create and what dependencies to resolve.

### B2.1. Read the canonical sections

Reference docs follow the canonical embedded-markdown shape with three required sections beyond the Generation Contract — read them all before writing any files:

- **`## TSX Template`** — fenced ```tsx``` block with the full component implementation. Copy this verbatim into the generated `.tsx` file. Substitute `{{IMPORT_SOURCE:...}}` / `{{NAME}}` / `{{FIELDS}}` placeholders at write time when present.
- **`## SCSS Template`** — fenced ```scss``` block with the canonical styles. Copy verbatim into the generated `.scss` file.
- **`## Accessibility`** — WCAG 2.2 AA criteria the component addresses (keyboard, ARIA, focus, contrast, target size). Don't strip a11y patterns out of the TSX/SCSS during generation; they're load-bearing.

If a reference doc is missing any of these three sections, fall back to the older "Key Pattern" / "Full Implementation Reference" / "SCSS Pattern" shape. The catalog.md "Verification Status" table records which components have been migrated to the canonical shape; treat any others as legacy and synthesize from the available pieces.

### B3. Resolve the dependency tree

Walk dependencies recursively using each dependency's own Generation Contract. Build the full list of files that will be created.

Example for Dialog:
```
dialog.tsx + dialog.scss
  → button.tsx + button.scss
  → icon-button.tsx + icon-button.scss
    → icon.tsx (no scss)
```

### B4. Show the dependency tree

Before generating any files, display:

```
Generating the following files in src/components/fpkit/:

  New:
    ui.tsx              (foundation — React only)
    icon.tsx
    button.tsx + button.scss
    icon-button.tsx + icon-button.scss
    dialog.tsx + dialog.scss

  Skipped (already exist):
    (none)

Proceed? [Enter to continue, Ctrl+C to cancel]
```

Wait for confirmation before proceeding.

### B5. Generate files bottom-up

Generate leaf dependencies first, then composite components.

Order example:
1. `icon.tsx` (no deps)
2. `button.tsx` + `button.scss`
3. `icon-button.tsx` + `icon-button.scss`
4. `dialog.tsx` + `dialog.scss`

For each file:
- **If it already exists:** Skip generation. Note it in the summary. Wire import from existing file.
- **If it does not exist:** Generate it following the patterns in Step C.

---

## Step C — Generated Code Characteristics

### C1. TypeScript file (`.tsx`)

**Imports:**
```tsx
// Always import UI from local path
import UI from '../ui'
import React from 'react'
// Other local deps
import Button from '../button/button'
```

**Types:**
```tsx
// Inline all types in the component file
// Never import types from other generated components
export type ButtonProps = {
  children?: React.ReactNode
  disabled?: boolean
  // ...
} & React.ComponentPropsWithoutRef<'button'>
```

**No external imports** other than React and local project files.

**Condensed utilities:**
- `useDisabledState` — Inline the condensed ~50-line version from `references/accessibility.md`
- `resolveDisabledState` — Inline as a one-liner: `const resolveDisabledState = (d?: boolean, id?: boolean) => d ?? id ?? false`

### C2. SCSS file (`.scss`)

**Always use CSS custom properties with hardcoded fallbacks:**
```scss
.btn {
  font-size: var(--btn-fs, 0.9375rem);
  padding-block: var(--btn-padding-block, calc(var(--btn-fs, 0.9375rem) * 0.5));
  padding-inline: var(--btn-padding-inline, calc(var(--btn-fs, 0.9375rem) * 1.5));
  border-radius: var(--btn-radius, 0.375rem);
  background: var(--btn-bg, transparent);
  color: var(--btn-color, var(--color-text, currentColor));
  // Global token references MUST have fallbacks:
  background: var(--btn-primary-bg, var(--color-primary, #0066cc));
}
```

**Rules:**
- All values in **rem units** (never px). Conversion: px ÷ 16 = rem.
- CSS variable naming: `--{component}-{element?}-{variant?}-{property}`
- Global token refs (like `--color-primary`) always get hardcoded fallbacks
- See `references/css-variables.md` for full naming conventions

---

## Step D — Accessibility Patterns

### D1. aria-disabled pattern (interactive components)

**Always use `aria-disabled` instead of the native `disabled` attribute for buttons and interactive elements.**

Why: Native `disabled` removes the element from keyboard tab order — keyboard and screen-reader users can't reach the control to discover it's disabled or access any explanation. `aria-disabled` keeps it focusable so screen readers can announce the disabled state.

**Condensed useDisabledState** (inline in button.tsx and any interactive component):

```tsx
// Condensed useDisabledState — WCAG 2.1.1 compliant disabled pattern
// Uses aria-disabled instead of native disabled to maintain keyboard access
function useDisabledState(
  disabled: boolean | undefined,
  handlers: { onClick?: React.MouseEventHandler<HTMLButtonElement>; onKeyDown?: React.KeyboardEventHandler<HTMLButtonElement> } = {}
) {
  const isDisabled = Boolean(disabled)

  const disabledProps = {
    'aria-disabled': isDisabled,
    className: isDisabled ? 'is-disabled' : '',
  }

  const wrappedHandlers = {
    onClick: handlers.onClick
      ? (e: React.MouseEvent<HTMLButtonElement>) => {
          if (isDisabled) { e.preventDefault(); e.stopPropagation(); return }
          handlers.onClick!(e)
        }
      : undefined,
    onKeyDown: handlers.onKeyDown
      ? (e: React.KeyboardEvent<HTMLButtonElement>) => {
          if (isDisabled) { e.preventDefault(); e.stopPropagation(); return }
          handlers.onKeyDown!(e)
        }
      : undefined,
  }

  return { disabledProps, handlers: wrappedHandlers }
}
```

**SCSS disabled styling:**
```scss
.btn {
  &[aria-disabled="true"],
  &.is-disabled {
    opacity: var(--btn-disabled-opacity, 0.6);
    cursor: var(--btn-disabled-cursor, not-allowed);
    pointer-events: none;
  }
}
```

### D2. Focus management

Always include visible focus indicators:
```scss
.btn:focus-visible {
  outline: var(--btn-focus-outline, 2px solid currentColor);
  outline-offset: var(--btn-focus-outline-offset, 2px);
}
```

### D3. Semantic HTML

Prefer semantic elements over roles:
- `<button>` not `<div role="button">`
- `<nav>` not `<div role="navigation">`
- `<dialog>` not `<div role="dialog">`

---

## Step E — Style Generation

### E1. SCSS structure template

```scss
// {Component} component
// CSS variables with fallback defaults — override in :root or scoped selectors

.{component} {
  // Layout
  display: var(--{component}-display, block);

  // Spacing
  padding-block: var(--{component}-padding-block, 1rem);
  padding-inline: var(--{component}-padding-inline, 1rem);

  // Typography
  font-size: var(--{component}-fs, 1rem);
  font-weight: var(--{component}-fw, 400);

  // Visual
  background: var(--{component}-bg, transparent);
  color: var(--{component}-color, currentColor);
  border: var(--{component}-border, none);
  border-radius: var(--{component}-radius, 0);
}
```

### E2. Data attribute selectors

fpkit uses `data-*` attributes for variants (not BEM modifiers):

```scss
// Size variants via data-btn attribute
.btn[data-btn~="sm"] { font-size: var(--btn-size-sm, 0.8125rem); }
.btn[data-btn~="lg"] { font-size: var(--btn-size-lg, 1.125rem); }
.btn[data-btn~="block"] { width: 100%; }

// Style variants via data-style attribute
.btn[data-style="outline"] {
  background: var(--btn-outline-bg, transparent);
  border: var(--btn-outline-border, 1px solid currentColor);
}

// Color variants via data-color attribute
.btn[data-color="primary"] {
  background: var(--btn-primary-bg, var(--color-primary, #0066cc));
  color: var(--btn-primary-color, var(--color-text-inverse, #fff));
}
```

The `[data-btn~="value"]` selector matches space-separated words — `data-btn="sm block"` matches both `[data-btn~="sm"]` and `[data-btn~="block"]`.

---

## Step F — Post-Generation Summary

After all files are generated, show:

```
Generated components in src/components/fpkit/:

  Created:
    button/button.tsx
    button/button.scss

  Skipped (already existed):
    (none)

Import and usage:

  import Button from './components/fpkit/button/button'
  import './components/fpkit/button/button.scss'

  <Button type="button" onClick={handleClick}>Click me</Button>
  <Button type="button" disabled>Disabled (stays focusable)</Button>
  <Button type="button" data-color="primary" data-btn="lg">Primary Large</Button>
```

---

## Step G — Verify Integration

After Step F, run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/verify_integration.py <project_root>` to check that the user's entrypoint actually imports the artifacts that were just written.

- Exit 0 → everything is wired up. No further action.
- Exit 1 → the script returns a `reasons` array. Print each reason as a numbered fix-up list. Do **not** auto-edit the entrypoint — the developer must add imports themselves so they retain ownership of the wiring.

The verifier reads `stack.entrypointFile` from `.acss-target.json`, so Step A3.1 must have run successfully. If `stack.entrypointFile` is missing or stale, the verifier exits 1 with a reason pointing back to `detect_stack.py`.

---

## `/kit-list` workflow — read-only inspection

This is a separate command flow from `/kit-add` (Steps A–G above). `/kit-list` never writes files. It reads `references/components/catalog.md` and individual reference docs and prints a formatted summary.

### L1. No arguments — categorized listing

Read `references/components/catalog.md` — both the per-component listing and the `## HTML Output Status` table — and display every available component organized by category. Append `[HTML]` to any component whose row in the HTML Output Status table is marked **Verified**; these are the components `/kit-add --target=html` can generate today. Components without the marker exist as React only and `/kit-add --target=html` will warn.

Output format:

```text
Available Components (acss-kit)

Simple (no dependencies):
  badge       — Status indicator with count or text
  tag         — Categorical label with optional removal
  heading     — Semantic heading (h1-h6) with styles
  text        — Inline/block text with variants

Interactive (useDisabledState pattern):
  button      — Primary interactive element (all variants)              [HTML]
  link        — Accessible anchor with hover/visited states

Layout:
  card        — Compound component (Card.Title, Card.Content, Card.Footer)  [HTML]
  nav         — Navigation landmark with compound Nav.List, Nav.Item

Complex (multiple dependencies):
  alert       — Severity-aware notification (needs icon)                 [HTML]
  dialog      — Modal dialog with focus trap (needs button, icon)        [HTML]
  form        — Form controls (input, textarea, select, checkbox, toggle)

Run /kit-add <component> to generate React components, or /kit-add --target=html <component> for static HTML versions of the [HTML]-marked entries.
```

### L2. With a component name — per-component detail

Read the component's reference doc (or its entry in `catalog.md`) and display:

1. **Generation Contract** — files that would be created, imports used
2. **Dependencies** — other components that would be co-generated
3. **HTML output** — read the `## HTML Output Status` table in `catalog.md`; print `Verified` if the component appears as Verified there (i.e. `/kit-add --target=html` can generate it), otherwise `Not yet — React only`
4. **Props** — TypeScript interface with descriptions
5. **CSS Variables** — customizable properties with defaults
6. **Usage Example** — import + JSX snippet

Example output for `/kit-list badge`:

```text
Component: Badge
File: badge.tsx + badge.scss
Dependencies: none (simple component)
HTML output: Not yet — React only (/kit-add --target=html will warn)

Props:
  children?   ReactNode   — Content (typically numbers or short text)
  variant?    'rounded'   — Visual variant
  ...UI props             — All standard <sup>-element HTML props

CSS Variables:
  --badge-bg              Background color (default: #e9ecef)
  --badge-color           Text color (default: #212529)
  --badge-fs              Font size (default: 0.75rem)
  --badge-fw              Font weight (default: 600)
  --badge-padding-inline  Horizontal padding (default: 0.375rem)
  --badge-padding-block   Vertical padding (default: 0.125rem)
  --badge-radius          Border radius (default: 0.25rem)

Usage:
  import Badge from './badge/badge'
  import './badge/badge.scss'

  <Badge aria-label="3 unread messages">3</Badge>
  <Badge variant="rounded" aria-label="99+ notifications">99+</Badge>

Run /kit-add badge to generate this component.
```

If the component name is unknown, print "Component '<name>' not found. Run `/kit-list` (no args) to see the full catalog." and stop.

---

## Reference Documents

Read these before generating components:

| Document | Purpose |
|----------|---------|
| `references/architecture.md` | UI base component, polymorphic pattern, `as` prop |
| `references/css-variables.md` | CSS variable naming conventions, fallback strategy |
| `references/accessibility.md` | WCAG patterns, aria-disabled, condensed useDisabledState |
| `references/composition.md` | Compound components, generation decision tree |
| `references/components/catalog.md` | Verification status table + remaining inline components (Badge, Tag, Heading, Text, Details, Progress) |
| `references/components/button.md` | Button — canonical shape ✓ |
| `references/components/icon-button.md` | IconButton (wraps Button + XOR aria-label/aria-labelledby) — canonical shape ✓ |
| `references/components/alert.md` | Alert with severity levels, auto-dismiss — canonical shape ✓ |
| `references/components/card.md` | Card compound component (Title, Content, Footer) — canonical shape ✓ |
| `references/components/dialog.md` | Dialog with native `<dialog>` — canonical shape ✓ |
| `references/components/popover.md` | Popover via native HTML Popover API — canonical shape ✓ |
| `references/components/table.md` | Table compound (Caption, Head, Body, Row, HeaderCell, Cell) — canonical shape ✓ |
| `references/components/img.md` | Img with lazy loading + SVG-gradient placeholder — canonical shape ✓ |
| `references/components/icon.md` | Icon with built-in 9-icon SVG dispatch — canonical shape ✓ |
| `references/components/link.md` | Link with auto security defaults — canonical shape ✓ |
| `references/components/list.md` | List + List.ListItem (ul/ol/dl) — canonical shape ✓ |
| `references/components/field.md` | Field (label + control wrapper) — canonical shape ✓ |
| `references/components/input.md` | Input with validation states — canonical shape ✓ |
| `references/components/checkbox.md` | Checkbox (wraps Input) — canonical shape ✓ |
| `references/components/form.md` | Form composition (legacy bundled reference; superseded by Form Mode in this skill) |
| `references/components/nav.md` | Nav compound component (List, Item) — legacy shape |

---

## Key Rules Summary

1. **No `@fpkit/acss` imports** — all imports are local
2. **Types inline** — never import types from another generated file
3. **rem units only** — all sizes and spacing in rem
4. **CSS var fallbacks** — every `var(--token)` has a hardcoded fallback
5. **aria-disabled** — never native `disabled` for interactive components
6. **Skip existing** — if a file exists, import from it, don't overwrite
7. **Bottom-up order** — generate leaf dependencies before composites
8. **Condensed utilities** — inline useDisabledState as ~50 lines, not 247

---

## Authoring New Components (for contributors)

When adding or updating a component reference doc, follow the canonical embedded-markdown shape.

### Required sections

Every component reference doc must contain (in order):

1. **Verification banner** — top of file, blockquote starting with `**Verified against fpkit source:**`. Records the upstream ref (e.g. `@fpkit/acss@6.5.0`) and any intentional divergences from upstream (inlined hooks, simplified compound APIs, dropped subcomponents). Future maintainers read this to understand *why* the vendored version diverges.
2. **`## Overview`** — one-paragraph summary of the component's purpose.
3. **`## Generation Contract`** — `export_name`, `file`, `scss`, `imports`, `dependencies`. The `/kit-add` workflow reads these fields verbatim.
4. **`## Props Interface`** — TypeScript interface or type alias the component accepts.
5. **`## TSX Template`** — fenced ```tsx``` block containing the full component code. Self-contained: imports only `UI from '../ui'`, React, and other vendored components via relative paths. Never `@fpkit/acss`.
6. **`## CSS Variables`** — fenced ```scss``` block listing the component's CSS custom properties with default values.
7. **`## SCSS Template`** — fenced ```scss``` block containing the actual SCSS rules.
8. **`## Accessibility`** — required. Document keyboard interaction, ARIA, focus management, target size, color contrast, and the WCAG 2.2 AA criteria addressed. The Accessibility section is load-bearing — don't strip a11y patterns out of the TSX/SCSS during generation.
9. **`## Usage Examples`** — fenced ```tsx``` block showing common usage patterns.

### Reference vs Skill (hybrid packaging)

Most components live as reference docs at `references/components/<name>.md`. Composable, complex, or high-iteration components can be promoted to their own skill at `skills/component-<name>/SKILL.md` with discovery-friendly trigger phrases in the frontmatter `description`.

Form generation and natural-language component creation are handled by the **Form Mode** and **Creator Mode** sections of this skill — see below.

### Verification log

Every new or migrated component gets an entry in `references/components/catalog.md` under "Verification Status":

```
| Component | Reference | Verified against | Status |
|-----------|-----------|------------------|--------|
| Foo | [`foo.md`](foo.md) | `@fpkit/acss@<version>` | New / Verified — <intentional divergences if any> |
```

This table is the single source of truth for which components have been migrated to the canonical shape.

### fpkit verification workflow

Before authoring or backfilling a reference doc:

1. Resolve the captured `@fpkit/acss` ceiling version to the matching git tag/SHA in the `shawn-sandy/acss` repo. If no matching tag exists for that npm version, use the closest tag and document the gap in the verification banner.
2. Fetch the canonical fpkit source from `https://github.com/shawn-sandy/acss/blob/<tag-or-sha>/packages/fpkit/src/<component>/...` (full GitHub URL per repo policy — never `blob/main`).
3. Compare the upstream behavior to what the existing reference doc describes. Note any intentional divergence (inlined hooks, simplified compound APIs, dropped subcomponents) in the verification banner.
4. Author the canonical sections to match fpkit semantics with relative-path imports — never `@fpkit/acss`.

---

## Creator Mode — Natural-Language Description

Generate a paste-ready TSX snippet (or standalone component file) from a plain-English description. Resolves the user's words against the matched component's Props Interface — never invents props or variants that aren't in the reference doc.

> Delegates to whichever component reference doc matches the description. Each reference doc carries its own `@fpkit/acss@6.5.0` verification line.

**Supported components:** Button, IconButton, Alert, Card, Dialog, Popover, Link, Img, Icon, List, Table, Field, Input, Checkbox, Nav — any component with a dedicated `references/components/<name>.md` file. Components that exist only as inline catalog entries (Badge, Tag, Heading, Text/Paragraph, Details, Progress) are not supported; promote them to a dedicated reference doc first.

**Form-shaped requests** ("signup form", "contact form with email and password") are handled by the **Form Mode** section below — not creator mode.

**Examples:**
- "Create a primary pill button that says 'Add to cart'."
- "Make me a soft warning alert titled 'Heads up' with body 'Your card expires next month'."
- "Build a card with a heading 'Plan' and a primary button labelled Upgrade."
- "Design a small outline icon-button with `aria-label` 'Close'."

### CM-0. Exit plan mode

Call `ExitPlanMode` before parsing. Step CM-B may delegate to `/kit-add` (writes TSX/SCSS) and Step CM-E (file mode) writes a standalone component file — plan mode blocks both.

Stay in plan mode only when the user explicitly asked for a parse-only preview. In that case, narrate the resolved spec (component, props, content) from CM-A1–CM-A5 without writing files, and wait for approval.

---

### CM-A. Parse the description

#### CM-A1. Component dispatch

Match the description's component noun against `references/components/*.md`. Every `<name>.md` (except `catalog.md`, `foundation.md`, and the legacy `form.md`) is a candidate.

| Phrase contains | Resolves to | Reference doc |
|-----------------|-------------|---------------|
| `button`, `btn`, `cta`, `call to action` | Button | `references/components/button.md` |
| `icon button`, `icon-button` | IconButton | `references/components/icon-button.md` |
| `alert`, `banner`, `notification` | Alert | `references/components/alert.md` |
| `card`, `panel`, `tile` | Card | `references/components/card.md` |
| `dialog`, `modal` | Dialog | `references/components/dialog.md` |
| `popover`, `floating card` | Popover | `references/components/popover.md` |
| `link`, `anchor`, `hyperlink` | Link | `references/components/link.md` |
| `image`, `img`, `picture` | Img | `references/components/img.md` |
| `icon` (standalone, not "icon button") | Icon | `references/components/icon.md` |
| `list`, `bullet list`, `ordered list` | List | `references/components/list.md` |
| `table`, `data table`, `grid` (tabular) | Table | `references/components/table.md` |
| `field`, `form field`, `labelled control` | Field | `references/components/field.md` |
| `input`, `text field`, `email field` | Input | `references/components/input.md` |
| `checkbox`, `tickbox` | Checkbox | `references/components/checkbox.md` |
| `nav`, `navigation`, `menu bar` | Nav | `references/components/nav.md` |

When no mapping is found, halt: "No `acss-kit` component matches '<phrase>'. Run `/kit-list` to see the catalog."

For **multi-component compositions** ("a card with a button inside"), match the outer component first; the inner component is a refinement turn (CM-G).

#### CM-A2. Load the matched reference doc

Read the matched reference doc and parse:

1. **`## Generation Contract`** — yields `export_name`, `file`, `dependencies`.
2. **`## Props Interface`** — yields the prop set, types, and JSDoc. Union-literal types are the canonical vocabulary.
3. **`## Usage Examples`** — used to detect compound API (e.g. `Card.Title`, `Table.Body`).

#### CM-A3. Resolve user phrases against the prop set

First match wins. The only silent defaults are the state-control carve-outs (CM-A3.5) and component-declared safe defaults (CM-A3.6).

**Colour family** (applies to props named `color`, `severity`, `kind`, `tone`, `palette`, or with a colour-like union):

| Synonym | Maps to |
|---------|---------|
| `primary`, `main`, `cta` | `primary` |
| `secondary` | `secondary` |
| `tertiary`, `accent` | `tertiary` |
| `info`, `informational` | `info` |
| `success`, `confirm` | `success` |
| `warning`, `caution` | `warning` |
| `danger`, `destructive`, `delete`, `error` | `danger` (or `error` if that's the prop's literal) |
| `neutral`, `default`, `muted` | `default` (or `neutral`) |

Halt if the resolved synonym is not in the prop's union literal. Never silently substitute the closest one.

**Size family** (applies to props named `size`, `scale`, `density`, or with a size-like union):

| Synonym | Maps to |
|---------|---------|
| `extra small`, `xs`, `tiny` | `xs` |
| `small`, `sm`, `compact` | `sm` |
| `medium`, `md`, `regular` | `md` |
| `large`, `lg`, `big` | `lg` |
| `extra large`, `xl` | `xl` |
| `huge`, `2xl` | `2xl` |

Halt if the resolved size is not in the prop's union. Some components accept only a subset — the union literal is authoritative.

**Per-component union literals** — common adjective synonyms:

| Synonym group | Canonical target |
|---------------|------------------|
| `pill`, `rounded`, `round`, `capsule` | `pill` |
| `outline`, `outlined`, `bordered`, `ghost` | `outline` or `outlined` — literal match wins |
| `filled`, `solid` | `filled` |
| `soft`, `subtle`, `tonal` | `soft` |
| `text`, `link-style`, `flat` | `text` |
| `dismissible`, `closable`, `with close button` | `dismissible: true` |

Resolution rule: (1) Literal match wins. (2) If not literal but one canonical spelling exists, use it. (3) If both spellings exist and the user gave a non-literal synonym, halt via `AskUserQuestion`. (4) If the synonym maps to nothing on this component, halt listing the actual union members.

**Boolean props** — set to `true` when the description contains an affirmative phrase for the prop name (`disabled`, `block`, `dismissible`, `external`, etc.). Booleans not mentioned are omitted.

**Slot / content props** (`children`, `title`, `body`, `aria-label`) — extract from: (1) quoted strings in order; (2) `that says <X>` / `labelled <X>` / `with text <X>` → `children`; (3) imperative verb-phrase fallback. Never write a component with placeholder content — halt via `AskUserQuestion` if a slot is unresolvable.

#### CM-A3.5. State-control props (demo defaults)

Some required props represent state bindings. Emit an explicit demo default and document in the summary as a wire-up TODO.

| Prop | Demo default | Summary note |
|------|--------------|--------------|
| `open` | `true` | Wire to caller state (e.g. `useState`) |
| `expanded` | `true` | (same) |
| `visible` | `true` | (same) |
| `checked` | `false` | Wire to caller state |

Pair each with a no-op `() => {}` callback when a matching `on*` callback exists in the Props Interface.

#### CM-A3.6. Component-declared safe defaults

Button's `type` prop always defaults to `"button"` — detected by reading the Props Interface JSDoc for `Required — ...` paired with a default in the TSX Template signature. Any other required prop follows the halt-on-unresolved rule from CM-A5.

#### CM-A5. Ambiguity check

Halt via `AskUserQuestion` when: a required prop is unresolved (excluding CM-A3.5/CM-A3.6 carve-outs); a colour-family prop is unresolved; a synonym maps to two different prop axes; two synonyms conflict on the same axis; a resolved value is not in the prop's union.

---

### CM-B. Resolve the target

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/detect_target.py <project_root>
```

- `source: "generated"` → probe `componentsDir` for the matched component's files and all dependencies from its Generation Contract. Run `/kit-add <component> [...dependencies]` if any are missing.
- `source: "none"` → run `/kit-add <component> [...dependencies]` to bootstrap.

After `/kit-add` completes, re-run `detect_target.py` to confirm `source` is `"generated"`, then continue.

---

### CM-C. Output mode

Ask once via `AskUserQuestion` (skip if the user already specified):

- **Snippet mode** *(default)* — print a TSX block for pasting. No file written.
- **File mode** — write `src/components/<Name>.tsx` where `<Name>` is derived from the resolved content (e.g. `"Add to cart"` button → `AddToCartButton`).

---

### CM-D. Validate

Run the CM-H validation matrix before generating. Any halt rule means: stop, print the offending combination, do not write. Any confirm rule means: round-trip through `AskUserQuestion`, only continue once the user accepts.

---

### CM-E. Generate output

**Single-element components** (Button, IconButton, Alert, Link, Img, Icon, Input, Checkbox, Field, Popover):

```tsx
// Children present:
<{{COMPONENT}} {{PROPS}}>
  {{CHILDREN}}
</{{COMPONENT}}>

// No children (Img, Icon, Input, Checkbox when children absent):
<{{COMPONENT}} {{PROPS}} />
```

Branch selection: (1) No `children` slot in Props Interface → always self-closing. (2) `children` present and resolved → open/close. (3) `children` optional and empty → self-closing. (4) `children` required and empty → CM-A5 already halted.

**Compound components** (Card, Table, List) — emit root + slots the description named, in document order per the reference doc's Usage Examples. Skip empty slots — never emit a placeholder.

**Snippet mode imports** — resolve path from `stack.entrypointFile` (in `.acss-target.json`) to `componentsDir`. Fallback: project-root-relative path with a comment to adjust import to the paste destination.

**File mode** — emit import lines + typed function wrapper + JSX at `src/components/<Name>.tsx`. `{{HANDLER_SIGNATURE}}` is the typed callback prop forwarded when the component declares one (e.g. `onClick` for Button, `onDismiss` for Alert).

**Atomic generation** — build entire output in memory; write to disk only on success.

---

### CM-F. Accessibility

The generated component is WCAG 2.2 AA by construction (delegates to the vendored component). Enforce during generation:
- Required-prop halts (CM-A5) prevent missing `aria-label` on icon-only controls, `alt` on Img, `labelFor` on Field.
- Pass `disabled` through the component's typed `disabled` prop — not raw HTML `disabled` — to preserve the `aria-disabled` + tab-order pattern via `useDisabledState` (WCAG 2.1.1).
- Compound slot omission keeps aria-labelledby chains intact.

---

### CM-G. Refinement turns

After a successful generation, the next user turn is a **refinement** (not a fresh CM-A) when both: (1) it doesn't name a different component, and (2) it reads as a delta on the existing spec.

| Phrase | Effect |
|--------|--------|
| `make it larger` / `bigger` | size-family prop → next step up (halt at ceiling) |
| `make it smaller` | size-family prop → next step down (halt at floor) |
| `swap to <colour>` / `make it <X>` | colour-family prop → resolved from CM-A3 colour table |
| `make it <variant>` | variant prop → resolved from synonym table |
| `add full width` / `stretch it` | `block: true` |
| `disable it` | `disabled: true` |
| `change the text to "<X>"` | primary content slot → `<X>` |
| `start over` / `reset` / `forget that` | clear in-memory spec; treat next turn as fresh CM-A |

A refinement re-runs CM-A5 → CM-D → CM-E. Steps B and C are skipped. In file mode, rewrite the same file. In snippet mode, print the full new JSX.

---

### CM-H. Validation matrix

| Combination | Action |
|-------------|--------|
| Required prop unresolved (excluding CM-A3.5/CM-A3.6) | Halt |
| Resolved value not in prop's union literal | Halt — list supported values |
| Two same-axis synonyms in one description | Halt — reject as conflicting |
| Slot content empty or whitespace-only | Halt |
| Slot content > 80 chars | Confirm — long inline labels usually mean a different component |
| `## Generation Notes — Creator Mode` block in matched reference doc | Apply its halt/confirm entries verbatim |

---

### CM-I. Worked examples

**Button:**
> "Create a primary pill button that says 'Add to cart'."
```tsx
import Button from './fpkit/button/button'
import './fpkit/button/button.scss'

<Button type="button" color="primary" variant="pill">
  Add to cart
</Button>
```

**Alert:**
> "Make me a soft warning alert titled 'Heads up' with body 'Your card expires next month' that's dismissible."
```tsx
import Alert from './fpkit/alert/alert'
import './fpkit/alert/alert.scss'

<Alert open={true} severity="warning" variant="soft" title="Heads up" dismissible onDismiss={() => {}}>
  Your card expires next month
</Alert>
```
(`open` and `onDismiss` are demo defaults — wire to caller state.)

**Card (compound):**
> "Build a card with a heading 'Plan' and content 'Premium tier with all features.'"
```tsx
import Card from './fpkit/card/card'
import './fpkit/card/card.scss'

<Card>
  <Card.Title>Plan</Card.Title>
  <Card.Content>Premium tier with all features.</Card.Content>
</Card>
```

**Anti-patterns** — creator mode must never: silently default a colour-family prop; substitute a literal the component doesn't declare; bake the description into a code comment; carry a spec the user dropped; write to disk on an un-confirmed confirm; hard-code the components path (always run `detect_target.py`); emit compound slots the user didn't name.

---

## Form Mode — Accessible Form Scaffolding

Generate a self-contained, accessible React form composed from the `Field`, `Input`, `Button`, and (when needed) `Checkbox` reference components. If any of those don't yet exist in the target directory, this mode walks through `/kit-add field input checkbox button` first.

> **Verified against fpkit source:** `@fpkit/acss@6.5.0`. Follows upstream `components/form/form.tsx` composition pattern, targeting a single self-contained generated file.

**Examples:**
- "Create a signup form with email, password, and a role dropdown."
- "Build a contact form with name, email, message, and a newsletter checkbox."
- "Scaffold a login form."

---

### FM-0. Exit plan mode

Call `ExitPlanMode` before resolving the field list. Step FM-B may delegate to `/kit-add`, and Step FM-C writes the form file — plan mode blocks both.

Stay in plan mode only when the user explicitly asked for a preview. In that case, narrate the resolved field list and the file that would be generated, then wait for approval.

---

### FM-A. Resolve the field list

#### FM-A1. Ambiguity check

If the description is vague (e.g. "a contact form" with no specified fields), pause with `AskUserQuestion`. Safe defaults by form type:

| Form type | Default fields |
|-----------|----------------|
| Signup | email (required, autoComplete=email), password (required, minLength=8, autoComplete=new-password) |
| Login | email (required, autoComplete=email), password (required, autoComplete=current-password) |
| Contact | name, email (required), message (textarea, rows=4) |
| Newsletter | email (required, autoComplete=email) |

Confirm with the user before proceeding.

#### FM-A2. Field shape

```
{
  name: string,           // form field name
  label: string,          // visible label
  type: 'text' | 'email' | 'password' | 'tel' | 'url'
      | 'number' | 'date'
      | 'textarea' | 'select' | 'checkbox' | 'radio',
  required?: boolean,     // adds aria-required + visible *
  autoComplete?: string,
  options?: { value, label }[],  // required for select and radio
  rows?: number,          // textarea default 4
  minLength?: number,
}
```

For unsupported types (`file`, `color`, `range`), note in the summary and generate a plain `<input>` directly.

#### FM-A3. Form name

Derive PascalCase from description: "signup form" → `SignupForm`, "contact us" → `ContactForm`. Confirm only if ambiguous.

---

### FM-B. Verify dependencies

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/detect_target.py <project_root>
```

- `source: "generated"` → probe `componentsDir` for `field/field.tsx`, `input/input.tsx`, `button/button.tsx`, `checkbox/checkbox.tsx` (only if any field has `type: 'checkbox'`), and `ui.tsx`.
- `source: "none"` → skip probe, proceed to bootstrap.

Run `/kit-add field input button` (and `checkbox` if needed) when source is `"none"` or any file is missing. Re-run `detect_target.py` to confirm `source` is `"generated"`, then continue.

---

### FM-C. Generate the form file

Write to `src/forms/<FormName>.tsx` by default (or wherever the user specifies).

#### TSX Template

```tsx
// {{NAME}}.tsx — generated by kit-core skill (form mode)
import { useState, type FormEvent } from 'react'
{{IMPORT_SOURCE:Field,Input,Checkbox,Button}}

export type {{NAME}}Values = {
{{FIELD_TYPES}}
}

export type {{NAME}}Errors = Partial<Record<keyof {{NAME}}Values, string>>

export default function {{NAME}}({
  onSubmit,
}: {
  onSubmit?: (values: {{NAME}}Values) => void | Promise<void>
}) {
  const [errors, setErrors] = useState<{{NAME}}Errors & { _form?: string }>({})
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    if (submitting) return
    setSubmitting(true)
    setErrors({})
    try {
      const formData = new FormData(e.currentTarget)
      const raw = Object.fromEntries(formData.entries()) as Record<string, FormDataEntryValue>
      const values = {
        ...raw,
{{CHECKBOX_COERCION}}
{{RADIO_COERCION}}
      } as unknown as {{NAME}}Values
      await onSubmit?.(values)
    } catch (err) {
      setErrors({ _form: (err as Error).message })
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      noValidate
      aria-labelledby="{{NAME_KEBAB}}-heading"
      className="form"
    >
      <h2 id="{{NAME_KEBAB}}-heading">{{HEADING}}</h2>

      {errors._form && (
        <div role="alert" className="form-error">{errors._form}</div>
      )}

{{FIELDS}}

      <Button
        type="submit"
        disabled={submitting}
        data-color="primary"
      >
        {submitting ? 'Submitting…' : '{{SUBMIT_LABEL}}'}
      </Button>
    </form>
  )
}
```

The submit Button uses `useDisabledState` internally — `aria-disabled` gates pointer/keyboard while `submitting` is true, combined with the `if (submitting) return` guard in `handleSubmit` to prevent double-submits.

#### Placeholder substitution

| Placeholder | Substitute with |
|-------------|-----------------|
| `{{NAME}}` | PascalCase form name (e.g. `SignupForm`) |
| `{{NAME_KEBAB}}` | kebab-case form name (e.g. `signup-form`); prefix for all control ids |
| `{{HEADING}}` | Visible form heading (e.g. `Create your account`) |
| `{{SUBMIT_LABEL}}` | Submit button label (e.g. `Create account`) |
| `{{FIELD_TYPES}}` | One TS line per field: `  fieldName: string` (or `boolean` for checkbox) |
| `{{FIELDS}}` | Rendered field elements — see FM-D below |
| `{{IMPORT_SOURCE:Field,Input,Checkbox,Button}}` | Resolved local import block from `componentsDir`; drop `Checkbox` when absent |
| `{{CHECKBOX_COERCION}}` | Per checkbox: `        <name>: formData.get('<name>') === 'on',` |
| `{{RADIO_COERCION}}` | Per radio: `        <name>: String(formData.get('<name>') ?? ''),` |

#### Component-source imports

Compute the relative path from `src/forms/<FormName>.tsx` to `componentsDir`. Default `src/components/fpkit` gives `../components/fpkit`.

```tsx
import Field from '<relative>/field/field'
import Input from '<relative>/input/input'
import Checkbox from '<relative>/checkbox/checkbox'   // omit if no checkbox field
import Button from '<relative>/button/button'

import '<relative>/field/field.scss'
import '<relative>/input/input.scss'
import '<relative>/checkbox/checkbox.scss'            // omit if no checkbox field
import '<relative>/button/button.scss'
```

Build the entire form in memory; write to disk only on success.

---

### FM-D. Field renderers

Substitute into `{{FIELDS}}` with 6-space indentation. All renderers use `{{form_name_kebab}}-{{name}}` as the control's `id`.

**Text-like inputs (text, email, password, tel, url, number, date):**

```tsx
<Field labelFor="{{form_name_kebab}}-{{name}}" label="{{label}}">
  <Input
    id="{{form_name_kebab}}-{{name}}"
    name="{{name}}"
    type="{{type}}"
    {{REQUIRED_PROP}}
    {{AUTOCOMPLETE_PROP}}
    {{MINLENGTH_PROP}}
  />
</Field>
```

**Textarea:**

```tsx
<Field labelFor="{{form_name_kebab}}-{{name}}" label="{{label}}">
  <textarea
    id="{{form_name_kebab}}-{{name}}"
    name="{{name}}"
    {{ROWS_ATTR}}
    {{REQUIRED_ATTR}}
    {{ARIA_REQUIRED_ATTR}}
  />
</Field>
```

**Select:**

```tsx
<Field labelFor="{{form_name_kebab}}-{{name}}" label="{{label}}">
  <select
    id="{{form_name_kebab}}-{{name}}"
    name="{{name}}"
    {{REQUIRED_ATTR}}
    {{ARIA_REQUIRED_ATTR}}
  >
    <option value="">Select…</option>
    {{OPTIONS}}
  </select>
</Field>
```

**Checkbox:**

```tsx
<Checkbox
  id="{{form_name_kebab}}-{{name}}"
  name="{{name}}"
  label="{{label}}"
  {{REQUIRED_PROP}}
/>
```

(Checkbox renders its own label — do not wrap in `Field`.)

**Radio (group):**

```tsx
<fieldset>
  <legend>{{label}}</legend>
  {{OPTIONS_AS_RADIOS}}
</fieldset>
```

Each radio option:

```tsx
    <label>
      <input
        type="radio"
        id="{{form_name_kebab}}-{{name}}-{{value}}"
        name="{{name}}"
        value="{{value}}"
        {{REQUIRED_ATTR}}
      />
      {{option_label}}
    </label>
```

Halt before writing if `select` or `radio` has no options.

**Conditional attributes:**

| Property | Expansion |
|----------|-----------|
| `required: true` | `required`, `aria-required={true}` |
| `autoComplete: "email"` | `autoComplete="email"` |
| `minLength: 8` | `minLength={8}` |
| `rows: 6` | `rows={6}` (textarea; omit → `rows={4}`) |

**Field-types map for `{{FIELD_TYPES}}`:**

| Field `type` | TypeScript type |
|--------------|-----------------|
| text, email, password, tel, url, textarea, select, radio | `string` |
| number, date | `string` (FormData serialises both as strings; cast at validation time) |
| checkbox | `boolean` |

---

### FM-E. Accessibility

The generated form is WCAG 2.2 AA by construction:
- `<form noValidate>` — disables native validation; error truth lives in `aria-describedby` / `errorMessage`.
- `aria-labelledby` on the form references the `<h2>` so screen readers announce the form's purpose on entry.
- `<div role="alert">` — form-level submission failure announced immediately.
- `Field` provides `<label htmlFor>` association for every Input, Textarea, and Select.
- Submit Button uses `useDisabledState` — `aria-disabled` keeps it focusable while submitting (WCAG 2.1.1).

WCAG 2.2 AA criteria: 1.3.1, 2.1.1, 2.4.3, 2.4.7, 3.3.1, 3.3.2, 4.1.2, 4.1.3.

---

### FM-F. Post-generation summary

```text
Generated src/forms/<FormName>.tsx

Imports: Field, Input, Button [, Checkbox]

Field summary:
  email    (email, required, autoComplete=email)
  password (password, required, minLength=8)

Next steps:
  - Wire onSubmit handler in your route/page
  - Add per-field validation (structure is scaffolded; logic is application-specific)
  - Style overrides via CSS variables — see field.scss / input.scss
```

---

## Style-Tune Mode — Component Token Adjustment

Invoked by `/style-tune` when the subject resolves to a component. See `style-tune/SKILL.md` Step A for intent parsing and dispatch.

### STc-B. Locate the component SCSS

Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/detect_target.py <project_root>`. Require `source: "generated"`.

Probe `<componentsDir>/<component>/<component>.scss`. If missing, halt: "Component `<name>` isn't vendored yet. Run `/kit-add <name>` first — this is a styling task, not a scaffolding task."

Supported components: `button`, `card`, `alert`, `dialog`, `input`, `nav`. For others, halt: "Component `<name>` doesn't have a token mapping yet."

### STc-C. Compute component token deltas

For each `(component, family, delta)` from `style-tune/SKILL.md` Step A:

1. `Grep` the component SCSS for the targeted token name(s) and read the current value(s).
2. **Scalar values** (rem, unitless, hex): apply the canonical delta from intent-vocabulary. Respect clamp ranges (radius `[0.125rem, 1rem]`; padding multipliers, etc.).
3. **Var-only references** (`--alert-bg: var(--color-surface, …)`): do NOT edit this declaration. Route the edit to the underlying theme role via `styles/SKILL.md` Style-Tune Mode, and note in Step F that tuning the component token requires changing the theme role.
4. **Shadow tokens:** use the explicit preset values from intent-vocabulary (no procedural arithmetic on multi-stop shadows).
5. **Compound presets** (rows flagged `preset: true` in vocabulary): expand into the listed multi-family deltas and apply each independently.
6. Preserve `var(--x, fallback)` wrappers — only the declaration's RHS may change.

### STc-D. Apply component edits

Build the entire updated SCSS file in memory; `Edit` atomically. When one modifier touches multiple tokens, batch into one `Edit` pass per file.

Safety rules:
- Never strip a `var()` wrapper — only the RHS may change.
- Never rename a token.
- Never inline a hex literal where a `var(--color-*, …)` reference exists.
- Never edit lines outside the targeted `--{c}-*` declarations.

### STc-E. Validate and revert

**Structural check after each Edit:**
1. Re-`Grep` for `var(` occurrences — count must be unchanged before and after.
2. Re-`Grep` for each edited token name — must appear exactly once on a declaration LHS.

On failure, restore from the in-memory pre-edit copy and halt.

**Idempotency:** if the computed value equals the current value within tolerance (hex equality, or rem within 0.0001), skip the write and report "already at target" in Step F. Note that cumulative drift is still possible across iteration passes — `× 0.75` then `× 1.25` lands at `× 0.9375`, not the original. Document this when a chroma or scale modifier is applied.

---

## HTML Target

Generate static HTML versions of fpkit-style components for projects that don't use React — server-rendered apps, static sites, design-system docs, email templates, prototypes.

Triggers: user asks for `/kit-add --target=html`, "static HTML components", "HTML version of \<component\>", or mentions a non-React project.

Both this section and the React workflow above read the same reference docs at `references/components/<name>.md`. The React workflow extracts `## TSX Template`; this section extracts `## HTML Template` and (for stateful components) `## Vanilla JS`. The `## SCSS Template` block is identical for both.

### HT-A. Initialization

Run this check at the start of every HTML-target invocation.

**HT-A1. Determine target directory**

Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/detect_target.py --target=html <project_root>`.

1. `"source": "configured"` → use the reported `componentsHtmlDir`. Skip the prompt.
2. `"source": "none"` → ask:

   ```text
   Where should HTML components be generated? (default: components/html)
   ```

   After the developer answers, write `.acss-html-target.json` at the project root:

   ```json
   { "componentsHtmlDir": "components/html" }
   ```

   Commit this file — subsequent runs read it.

**HT-A2. Copy the foundation helper**

Check if `_stateful.js` exists in `<componentsHtmlDir>`. If not:

- Copy `${CLAUDE_PLUGIN_ROOT}/assets/html-foundation/_stateful.js` into `<componentsHtmlDir>/_stateful.js`.
- Inform the developer: `Created _stateful.js (foundation helper — required by stateful components)`.

---

### HT-B. Component generation

**HT-B1. Look up the component** — same catalog path as the React workflow: `references/components/catalog.md` → `references/components/<name>.md`.

**HT-B2. Read canonical sections** — a reference doc that supports HTML output contains:

- `## Generation Contract` — `export_name`, `file`, `scss`, `dependencies`. Reuse verbatim.
- `## HTML Template` — fenced `html` block. Copy verbatim into `<name>.html`.
- `## SCSS Template` — fenced `scss` block. Copy verbatim into `<name>.scss`.
- `## Vanilla JS` — fenced `js` block. Present on stateful components only. Copy verbatim into `<name>.js`.
- `## Accessibility` — read it. Do not strip ARIA attributes.

If `## HTML Template` is missing, warn the developer and offer to author markup from the TSX template by hand. Do not silently skip.

**HT-B3. Resolve dependencies** — same algorithm as React Step B3.

**HT-B4. Show dependency tree and wait for confirmation** — same format as React Step B4, using the `componentsHtmlDir` path.

**HT-B5. Generate files bottom-up** — leaf dependencies first. Skip existing files.

The HTML output is a **fragment** — no `<html>`/`<head>`/`<body>` wrapper. Slot placeholders use HTML comments: `<!-- slot: children -->`.

---

### HT-C. Output characteristics

**HTML (`.html`):** Fragment. Same class names, `data-*` attributes, and ARIA as the TSX output. Slot placeholders as HTML comments. Multiple variants separated by `<!-- variant: <name> -->`.

**SCSS (`.scss`):** Byte-identical to the React generator output. Rules: rem only, `--{component}-{element?}-{variant?}-{property}` naming, hardcoded fallbacks on global tokens, `[aria-disabled="true"]` on every interactive component.

**JS (`.js`) — stateful components only:** Emitted for Button, Card (interactive variant), Alert, Dialog, Popover, Checkbox, Input, IconButton. Plain ES module, no bundler required. Imports `wireDisabled` from `./_stateful.js` where applicable. Exports an idempotent `init()` function.

---

### HT-D. Post-generation summary

```text
Generated HTML components in components/html/:

  Created:
    button.html  button.scss  button.js

  Skipped (already existed):
    _stateful.js

How to wire it up:
  1. Compile SCSS: npx sass components/html/button.scss components/html/button.css
     Then: <link rel="stylesheet" href="components/html/button.css">
     (Or @import the .scss from your existing Sass entrypoint.)
  2. <script type="module" src="components/html/button.js"></script>
  3. Paste the markup from button.html into your page or template.
```

---

### HT-E. Verify integration

Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/verify_integration.py --target=html <project_root>`.

- Exit 0 → every `.scss`/`.js` artifact is referenced by at least one page. No action.
- Exit 1 → print each `reasons` entry as a numbered fix-up list. Do not auto-edit user pages.

`*.html` snippets are listed but not checked — they're copy-paste fragments.

---

### HT-F. Key rules

1. **Fragments only** — no `<html>`/`<body>` wrappers.
2. **Same classes, data attributes, ARIA** as TSX — SCSS reused unchanged.
3. **Vanilla JS for stateful components** — no React, no bundler.
4. **`_stateful.js` is the disabled-state helper** — copied once per project.
5. **Skip existing** — never overwrite; the user owns generated code.
6. **Bottom-up dependency order** — leaf components first.
7. **No auto-edits to user pages** — HT-E reports missing references only.
