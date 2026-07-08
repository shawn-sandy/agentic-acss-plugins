# List — Usage Guide

A semantic list wrapper for unordered (`ul`), ordered (`ol`), and definition (`dl`) lists. It uses the compound API `List` + `List.ListItem`, keeping the parent-child relationship explicit at the call site, and supports the `role="list"` override that restores list semantics for Safari/VoiceOver when `list-style: none` would otherwise strip them.

## Add it to your project

1. **One-time setup** (run once per project): `/setup` — installs `sass`, writes `.acss-target.json`, and creates the `ui.tsx` foundation every component imports.
2. **Add this component:** `/kit-add List` — copies `list.tsx` + `list.scss` into your components directory (default `src/components/fpkit/`).
   - Or run `/kit-sync` once to install **all** components, the foundation, and a starter theme together.

The generated component is self-contained — no `@fpkit/acss` install required.

## Import

`List` is a compound component — the parent and its `List.ListItem` sub-part ship in one file.

```tsx
import List from './fpkit/list/list'
import './fpkit/list/list.scss'
```

Adjust the path to match the `componentsDir` in your `.acss-target.json`.

## Props

**`List`**

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `type` | `'ul' \| 'ol' \| 'dl'` | `ul` | List variant. |
| `variant` | `'inline' \| 'numbered' \| 'none' \| string` | — | Visual variant; drives `data-variant` for SCSS targeting. |
| `role` | `string` | — | Explicit role override. Pass `role="list"` with `variant="none"`/`"inline"` to restore semantics for VoiceOver/Safari. |
| `classes` | `string` | — | CSS class(es). |
| `styles` | `React.CSSProperties` | — | Inline styles / CSS variables. |
| `children` | `React.ReactNode` | — | `List.ListItem` children. |

Plus any native `<ul>` attribute (except `type`).

**`List.ListItem`**

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `type` | `'li' \| 'dt' \| 'dd'` | `li` | Item element — match the parent list type. |
| `id` | `string` | — | Element id. |
| `classes` | `string` | — | CSS class(es). |
| `styles` | `React.CSSProperties` | — | Inline styles. |
| `children` | `React.ReactNode` | — | Item content. |

Plus any native `<li>` attribute (except `type`).

## Examples

```tsx
// Basic unordered list
<List>
  <List.ListItem>Apples</List.ListItem>
  <List.ListItem>Bananas</List.ListItem>
  <List.ListItem>Cherries</List.ListItem>
</List>

// Ordered list with custom marker color
<List
  type="ol"
  styles={{ '--list-marker-color': '#0066cc' } as React.CSSProperties}
>
  <List.ListItem>Step one</List.ListItem>
  <List.ListItem>Step two</List.ListItem>
</List>

// Unstyled list with role restoration (Safari/VoiceOver fix)
<List variant="none" role="list">
  <List.ListItem><a href="/about">About</a></List.ListItem>
  <List.ListItem><a href="/contact">Contact</a></List.ListItem>
</List>

// Inline list — navigation menu
<nav aria-label="Primary">
  <List variant="inline" role="list">
    <List.ListItem><a href="/home">Home</a></List.ListItem>
    <List.ListItem><a href="/products">Products</a></List.ListItem>
    <List.ListItem><a href="/contact">Contact</a></List.ListItem>
  </List>
</nav>

// Definition list (glossary)
<List type="dl">
  <List.ListItem type="dt">React</List.ListItem>
  <List.ListItem type="dd">A JavaScript library for building user interfaces.</List.ListItem>
  <List.ListItem type="dt">TypeScript</List.ListItem>
  <List.ListItem type="dd">JavaScript with syntactic types.</List.ListItem>
</List>
```

## Theming

Override these CSS custom properties in your theme to restyle every list. Each has a fallback, so overriding is optional.

| Variable | Purpose |
|----------|---------|
| `--list-padding-inline-start` | Indent of the list from its container. |
| `--list-gap` | Space between items. |
| `--list-item-padding-block` | Vertical padding on each item. |
| `--list-marker-color` | Bullet/number (`::marker`) color. |
| `--list-inline-gap` | Gap between items in `variant="inline"`. |
| `--dl-term-fw` | Font weight of definition terms (`<dt>`). |
| `--dl-term-margin-block-start` | Space above each term. |
| `--dl-desc-margin-block-end` | Space below each description (`<dd>`). |

```css
:root {
  --list-gap: 0.75rem;
  --list-marker-color: #6d28d9;
}
```

Generate a full matching theme with `/theme-create` (see [styles.md](../styles.md)).

## Accessibility

- Renders native `<ul>`, `<ol>`, or `<dl>` — screen readers announce "list of N items" and definition-list term/description pairs automatically.
- Safari + VoiceOver drop the implicit `role="list"` when `list-style: none` is applied. The `variant="none"` and `variant="inline"` variants trigger this, so pass `role="list"` explicitly on those.
- Pass `type="dt"` / `type="dd"` on `List.ListItem` when `type="dl"` so term/description semantics are preserved.
- Custom `::marker` colors used as the only indicator must meet 3:1 against the page background (WCAG 1.4.11) — verify in dark themes.
- For inline lists used as navigation, wrap them in a `<nav aria-label="…">` landmark and keep adequate `--list-inline-gap` for target size (WCAG 2.5.8).

## Related

- [Component index](README.md)
- [Nav](nav.md) — navigation landmark for inline link lists
- Full maintainer reference: [`skills/component-list/reference.md`](../../skills/component-list/reference.md)
