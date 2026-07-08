# Icon — Usage Guide

A lightweight inline-SVG icon component with a small built-in icon set. Each icon renders as an `<svg>` sized via the `size` prop, colored via `color` (default `currentColor`), and named for assistive tech via `aria-hidden` (decorative) or `aria-label` (standalone).

## Add it to your project

1. **One-time setup** (run once per project): `/setup` — installs `sass`, writes `.acss-target.json`, and creates the `ui.tsx` foundation every component imports.
2. **Add this component:** `/kit-add Icon` — copies `icon.tsx` into your components directory (default `src/components/fpkit/`).
   - Or run `/kit-sync` once to install **all** components, the foundation, and a starter theme together.

Icon has no SCSS file — it styles entirely through props and `currentColor`. The generated component is self-contained — no `@fpkit/acss` install required.

## Import

```tsx
import Icon from './fpkit/icon/icon'
```

Adjust the path to match the `componentsDir` in your `.acss-target.json`. Icon ships no stylesheet, so there is nothing to import for CSS.

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `name` | `'info' \| 'success' \| 'warning' \| 'error' \| 'close' \| 'chevron-down' \| 'chevron-right' \| 'check' \| 'external-link'` | — (required) | Icon from the built-in set. |
| `size` | `number` | `16` | SVG width/height in pixels. |
| `color` | `string` | `currentColor` | Stroke / fill color. |
| `aria-hidden` | `boolean` | `true` | Decorative — screen readers skip it. |
| `aria-label` | `string` | — | Accessible name for standalone icons; swaps in `role="img"` and drops `aria-hidden`. |

Plus any native `<svg>` attribute except `aria-hidden` / `aria-label` (handled above).

## Examples

```tsx
// Decorative — screen readers skip
<Icon name="info" aria-hidden size={16} />

// Inside a label that already carries meaning
<button type="button">
  <Icon name="check" aria-hidden /> Save
</button>

// Standalone — needs accessible name
<button type="button" aria-label="Close dialog">
  <Icon name="close" aria-hidden size={20} />
</button>

// Or label the icon directly when there's no surrounding interactive element
<Icon name="warning" aria-label="Warning" size={24} color="var(--color-warning)" />

// Inline with custom color
<Icon name="external-link" aria-hidden size={12} color="var(--color-primary)" />
```

## Theming

Icon has no dedicated SCSS file, so there are no `--icon-*` custom properties to override. Control appearance directly through props:

| Lever | How |
|-------|-----|
| Color | `color` prop, or let it inherit the parent's text color via the default `currentColor`. |
| Size | `size` prop, in pixels. |
| Theme-driven color | Pass a theme token, e.g. `color="var(--color-primary)"`. |

```tsx
// Inherit surrounding text color (recommended)
<span style={{ color: 'var(--color-danger)' }}>
  <Icon name="error" aria-hidden /> Something went wrong
</span>
```

## Accessibility

- Decorative by default (`aria-hidden="true"`) — use for icons that sit next to text that already conveys the meaning.
- Pass `aria-label` for standalone icons that carry meaning alone; the component swaps `aria-hidden` for `role="img"` automatically. Never pass both.
- Color must not be the only indicator of state (WCAG 1.4.1) — pair state icons with text or shape.
- A 16 px icon is not a touch target. When the icon is the only clickable area, wrap it in [Icon Button](icon-button.md) or [Button](button.md) to meet the 44 px minimum (WCAG 2.5.8).

## Related

- [Component index](README.md)
- [Icon Button](icon-button.md) — accessible icon-only button that hosts an Icon
- Full maintainer reference: [`skills/component-icon/reference.md`](../../skills/component-icon/reference.md)
