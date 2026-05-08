---
description: List available fpkit/acss components or inspect a specific one
argument-hint: [component]
allowed-tools: Read, Glob, Grep
---

# /kit-list

List available components or show detailed information about a specific component.

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

### `/kit-list` (no arguments)

Read `references/components/catalog.md` — both the per-component listing and the `## HTML Output Status` table — and display every available component organized by category. Append `[HTML]` to any component whose row in the HTML Output Status table is marked **Verified**; these are the components `/kit-add-html` can generate today. Components without the marker exist as React only and `/kit-add-html` will warn.

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

Run /kit-add <component> to generate React components, or /kit-add-html <component> for static HTML versions of the [HTML]-marked entries.
```

### `/kit-list <component>` (specific component)

Read the component's reference doc (or its entry in `catalog.md`) and display:

1. **Generation Contract** — What files will be created, what imports are used
2. **Dependencies** — What other components will be co-generated
3. **HTML output** — Read the `## HTML Output Status` table in `catalog.md`. Print `Verified` if the component has it (i.e. `/kit-add-html` can generate it), otherwise `Not yet — React only`.
4. **Props** — TypeScript interface with descriptions
5. **CSS Variables** — Customizable properties with defaults
6. **Usage Example** — Import + JSX snippet

**Example output for `/kit-list badge`:**

```text
Component: Badge
File: badge.tsx + badge.scss
Dependencies: none (simple component)
HTML output: Not yet — React only (/kit-add-html will warn)

Props:
  children?   ReactNode   — Content (typically numbers or short text)
  variant?    'rounded'   — Visual variant
  ...UI props             — All HTML <sup> props

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
