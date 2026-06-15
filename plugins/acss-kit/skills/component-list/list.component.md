---
spec: component.md
version: alpha
name: list
element: ul
role: list
tokens:
  paddingInlineStart: "{spacing.lg}"
  gap: "{spacing.sm}"
  itemPaddingBlock: "{spacing.xs}"
  markerColor: "{colors.primary}"
  inlineGap: "{spacing.md}"
props:
  type:
    values: [ul, ol, dl]
    default: ul
    maps-to: "host element"
  variant:
    values: [inline, numbered, none]
    maps-to: "data-variant"
  role:
    type: string
    a11y: "pass role=\"list\" with variant=\"none\"/\"inline\" to restore VoiceOver/Safari list semantics (WCAG 4.1.2)"
  classes:
    type: string
  styles:
    type: object
slots: [children]
variants:
  inline:   { maps-to: "data-variant=inline" }
  numbered: { maps-to: "data-variant=numbered" }
  none:     { maps-to: "data-variant=none" }
a11y: [1.3.1, 1.4.11, 2.1.1, 2.5.8, 4.1.2]
targets: [react, html, astro, angular, vue, svelte, web-component]
---

# Component: List

> **Neutral COMPONENT.md** for the acss-kit `list`. The framework-agnostic
> source of truth lives in the `##` body below; the canonical React projection is
> the `## Target: react` adapter at the end (byte-aligned with the legacy
> `reference.md`). `/kit-add list` reads this file: `## Styles` → `list.scss`,
> `## Target: react` → `list.tsx`.
>
> **Verified against fpkit source:** [`@fpkit/acss@6.5.0`](https://github.com/shawn-sandy/acss/tree/9063512fa822963d8151c972bed9f5b0e531df0f) (closest tagged ref to
> npm `6.6.0`). Vendored List preserves the upstream compound API (`List` +
> `List.ListItem`) and the `role="list"` override pattern that restores list
> semantics for VoiceOver/Safari when CSS `list-style: none` would otherwise
> strip them. Supports `ul`, `ol`, and `dl` variants (with `dt` / `dd` items for
> definition lists).

## Overview

A semantic list wrapper supporting unordered (`ul`), ordered (`ol`), and
definition (`dl`) lists. The `ListItem` sub-component renders `<li>`, `<dt>`, or
`<dd>` based on its `type` prop. The compound API (`List.ListItem`) keeps the
parent-child relationship explicit at the call site. Pass `role="list"` on the
unstyled `none` / `inline` variants to restore list semantics that Safari +
VoiceOver strip when `list-style: none` is applied.

## Semantic Structure

```html
<!-- variant: default (unordered) -->
<ul>
  <li><!-- slot: children --></li>
</ul>

<!-- variant: ordered (type="ol") -->
<ol>
  <li><!-- slot: children --></li>
</ol>

<!-- variant: none — unstyled, role restored for Safari/VoiceOver -->
<ul data-variant="none" role="list">
  <li><!-- slot: children --></li>
</ul>

<!-- variant: inline — navigation menu (pair with a landmark + role="list") -->
<nav aria-label="Primary">
  <ul data-variant="inline" role="list">
    <li><!-- slot: children --></li>
  </ul>
</nav>

<!-- variant: definition list (type="dl") -->
<dl>
  <dt><!-- slot: term --></dt>
  <dd><!-- slot: description --></dd>
</dl>
```

The host element is `<ul>` (default), `<ol>`, or `<dl>`, chosen via the `type`
prop. Visual variants surface as the `data-variant` attribute. `ListItem`
renders `<li>` / `<dt>` / `<dd>` via its own `type` prop, matching the parent
list type.

## Props

| Prop | Values | Required | Surfaces as |
|---|---|---|---|
| `type` | `ul` \| `ol` \| `dl` | no (default `ul`) | host element |
| `variant` | `inline` \| `numbered` \| `none` \| string | no | `data-variant` |
| `role` | string | no | `role` attribute (`list` restores Safari/VoiceOver semantics) |
| `classes` | string | no | `className` |
| `styles` | object | no | inline `style` |
| `ListItem.type` | `li` \| `dt` \| `dd` | no (default `li`) | item element |

## Tokens & CSS Variables

Themeable properties reference DESIGN.md primitives via `var(--token, <fallback>)`;
each keeps a hardcoded fallback so the component renders with no design system.

```scss
--list-padding-inline-start: var(--space-lg, 1.25rem);
--list-gap: var(--space-sm, 0.5rem);
--list-item-padding-block: var(--space-xs, 0.25rem);
--list-marker-color: var(--color-primary, #0066cc);
--list-inline-gap: var(--space-md, 1rem);

// Definition list
--dl-term-fw: 600;
--dl-term-margin-block-start: var(--space-sm, 0.5rem);
--dl-desc-margin-inline-start: 0;
--dl-desc-margin-block-end: var(--space-sm, 0.5rem);
```

## Styles

```scss
// list.scss
ul, ol {
  padding-inline-start: var(--list-padding-inline-start, var(--space-lg, 1.25rem));
  display: flex;
  flex-direction: column;
  gap: var(--list-gap, var(--space-sm, 0.5rem));
  margin: 0;

  > li {
    padding-block: var(--list-item-padding-block, var(--space-xs, 0.25rem));

    &::marker {
      color: var(--list-marker-color, #0066cc);
    }
  }

  &[data-variant="inline"] {
    flex-direction: row;
    flex-wrap: wrap;
    gap: var(--list-inline-gap, var(--space-md, 1rem));
    list-style: none;
    padding-inline-start: 0;
  }

  &[data-variant="none"] {
    list-style: none;
    padding-inline-start: 0;
  }
}

dl {
  margin: 0;

  > dt {
    font-weight: var(--dl-term-fw, 600);
    margin-block-start: var(--dl-term-margin-block-start, var(--space-sm, 0.5rem));
  }

  > dd {
    margin-inline-start: var(--dl-desc-margin-inline-start, 0);
    margin-block-end: var(--dl-desc-margin-block-end, var(--space-sm, 0.5rem));
  }
}
```

## Accessibility

WCAG 2.2 AA compliance for the generated `List` component.

**Native semantics — preserved**
- Renders native `<ul>`, `<ol>`, or `<dl>` elements. Screen readers announce "list of N items" / "ordered list of N items" / "definition list" automatically. Definition list items announce "term" / "definition" appropriately.
- Don't add `role="listbox"` / `role="menu"` for plain content lists — those roles trigger keyboard interaction expectations that you'd then need to implement (arrow-key navigation, single selection, etc.). Use them only for actual interactive widgets.

**The `list-style: none` Safari/VoiceOver gotcha**
- Safari + VoiceOver strip the implicit `role="list"` from `<ul>` / `<ol>` when CSS `list-style: none` is applied. The list still renders, but VoiceOver no longer announces "list" or item counts.
- The vendored `variant="none"` and `variant="inline"` apply `list-style: none`, so they trigger this Safari behavior.
- **Fix**: pass `role="list"` explicitly when using these variants:
  ```tsx
  <List variant="none" role="list">
    <List.ListItem>Nav link</List.ListItem>
  </List>
  ```
- This is a real bug in Safari that will not be fixed; the workaround is permanent. Document it in code review for any unstyled list.

**Definition list pattern (`dl`)**
- `<dl>` pairs `<dt>` (term) with `<dd>` (description). Multiple `<dd>` per `<dt>` is allowed (multiple definitions for the same term).
- Don't pair `<dt>` and `<dd>` with non-list semantics — VoiceOver and NVDA rely on the `<dl>` parent for the "definition list" announcement.
- Pass `type="dt"` and `type="dd"` on `List.ListItem` when `List type="dl"`.

**Keyboard navigation**
- Plain content lists have no keyboard interaction. Tab moves through any interactive descendants (links, buttons) using their native order.
- For lists of links, the focus order follows DOM order. Sort lists meaningfully — alphabetical, by date, by importance — so keyboard users get a useful traversal.

**Color contrast — markers**
- `::marker` color (`--list-marker-color`) is the bullet/number color. Custom markers must meet 3:1 against the page background (WCAG 1.4.11 Non-text Contrast) since the marker is purely visual.
- The default `var(--color-primary)` is typically well above 3:1; verify in dark themes.

**Inline lists for navigation**
- The `variant="inline"` pattern is common for nav menus. Always pair with `role="list"` (Safari fix) and a parent landmark (`<nav aria-label="Primary">`) so the list is reachable via assistive-tech navigation.
- Inline lists must keep adequate spacing (`--list-inline-gap`) to satisfy WCAG 2.5.8 Target Size when the list items are interactive.

**WCAG 2.2 AA criteria addressed**
- 1.3.1 Info and Relationships (native list semantics)
- 1.4.11 Non-text Contrast (marker color when used as the only indicator)
- 2.1.1 Keyboard (interactive descendants follow native focus order)
- 2.5.8 Target Size Minimum (inline-list spacing for interactive items)
- 4.1.2 Name, Role, Value (native list elements; explicit `role="list"` on unstyled variants for VoiceOver)

## Examples

```html
<ul>
  <li>Apples</li>
  <li>Bananas</li>
  <li>Cherries</li>
</ul>

<ul data-variant="none" role="list">
  <li><a href="/about">About</a></li>
  <li><a href="/contact">Contact</a></li>
</ul>

<dl>
  <dt>React</dt>
  <dd>A JavaScript library for building user interfaces.</dd>
</dl>
```

## Target: react

`generation: { export: List (compound: List.ListItem), file: list.tsx, scss: list.scss, imports: "UI from '../ui'", dependencies: [] }`

The React adapter is the canonical TSX projection — `List` and its compound
`List.ListItem` are assembled via `Object.assign`, both wrapping the foundation
`UI` element with `forwardRef`. `/kit-add list --target=react` emits the
assembled file: the Props Interface(s) and the TSX Template below.

## Props Interface

```tsx
export type ListType = 'ul' | 'ol' | 'dl'

export type ListProps = {
  /** List variant: ul | ol | dl (default: ul) */
  type?: ListType
  /** Visual variant — drives data-variant for SCSS targeting */
  variant?: 'inline' | 'numbered' | 'none' | string
  /**
   * Explicit role override.
   * Pass `role="list"` when applying `variant="none"` (or any unstyled variant)
   * to restore list semantics for VoiceOver/Safari, which strip them when
   * `list-style: none` is applied via CSS.
   */
  role?: string
  classes?: string
  styles?: React.CSSProperties
  children?: React.ReactNode
} & Omit<React.ComponentPropsWithoutRef<'ul'>, 'type'>

export type ListItemType = 'li' | 'dt' | 'dd'

export type ListItemProps = {
  /** li (default), dt, or dd — match the parent list type */
  type?: ListItemType
  id?: string
  classes?: string
  styles?: React.CSSProperties
  children?: React.ReactNode
} & Omit<React.ComponentPropsWithoutRef<'li'>, 'type'>
```

## TSX Template

```tsx
import UI from '../ui'
import React from 'react'

export type ListType = 'ul' | 'ol' | 'dl'

export type ListProps = {
  type?: ListType
  variant?: 'inline' | 'numbered' | 'none' | string
  role?: string
  classes?: string
  styles?: React.CSSProperties
  children?: React.ReactNode
} & Omit<React.ComponentPropsWithoutRef<'ul'>, 'type'>

export type ListItemType = 'li' | 'dt' | 'dd'

export type ListItemProps = {
  type?: ListItemType
  id?: string
  classes?: string
  styles?: React.CSSProperties
  children?: React.ReactNode
} & Omit<React.ComponentPropsWithoutRef<'li'>, 'type'>

const ListItem = React.forwardRef<HTMLLIElement | HTMLElement, ListItemProps>(
  ({ type = 'li', id, styles, children, classes, ...props }, ref) => (
    <UI
      id={id}
      as={type}
      className={classes}
      style={styles}
      ref={ref}
      {...props}
    >
      {children}
    </UI>
  ),
)
ListItem.displayName = 'ListItem'

const ListRoot = React.forwardRef<
  HTMLUListElement | HTMLOListElement | HTMLDListElement,
  ListProps
>(({ children, classes, type = 'ul', variant, styles, role, ...props }, ref) => (
  <UI
    as={type}
    data-variant={variant}
    className={classes}
    style={styles}
    role={role}
    ref={ref}
    {...props}
  >
    {children}
  </UI>
))
ListRoot.displayName = 'List'

type ListComponent = typeof ListRoot & {
  ListItem: typeof ListItem
}

export const List = Object.assign(ListRoot, { ListItem }) as ListComponent

export default List
```
