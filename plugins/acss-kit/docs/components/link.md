# Link — Usage Guide

A semantic anchor wrapper with automatic security defaults for external links. When `target="_blank"` is set, the component merges `rel="noopener noreferrer"` with any user-provided rel tokens, blocking `window.opener` exploitation and referrer leakage. Supports an optional `prefetch` hint and button-style rendering.

## Add it to your project

1. **One-time setup** (run once per project): `/setup` — installs `sass`, writes `.acss-target.json`, and creates the `ui.tsx` foundation every component imports.
2. **Add this component:** `/kit-add Link` — copies `link.tsx` + `link.scss` into your components directory (default `src/components/fpkit/`).
   - Or run `/kit-sync` once to install **all** components, the foundation, and a starter theme together.

The generated component is self-contained — no `@fpkit/acss` install required.

## Import

```tsx
import Link from './fpkit/link/link'
import './fpkit/link/link.scss'
```

Adjust the path to match the `componentsDir` in your `.acss-target.json`.

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `href` | `string` | — (required) | Link destination. |
| `target` | `string` | — | Link target (e.g. `"_blank"`). |
| `rel` | `string` | — | rel tokens; merged with security defaults when `target="_blank"`. |
| `prefetch` | `boolean` | `false` | Adds a prefetch hint. |
| `btnStyle` | `string` | — | Maps to `data-btn` for button-style links. |
| `styles` | `React.CSSProperties` | — | Inline styles. |
| `children` | `React.ReactNode` | — | Link content. |

Plus any native `<a>` attribute except the overridden `href`, `target`, `rel`.

## Examples

```tsx
// Internal
<Link href="/about">About us</Link>

// External — automatic security defaults
<Link href="https://example.com" target="_blank">
  Visit example.com
</Link>

// External + user-provided rel (merged with security defaults)
<Link href="https://partner.com" target="_blank" rel="sponsored">
  Sponsored: partner site
</Link>

// Icon-only link (accessible name required)
<Link href="/settings" aria-label="Settings">
  <Icon name="info" aria-hidden size={20} />
</Link>

// Skip-link pattern (combined with CSS visually-hidden-until-focus)
<Link href="#main" className="skip-link">Skip to main content</Link>

// Button-style link (visually a button; semantically still an anchor)
<Link href="/signup" btnStyle="block">
  Get started
</Link>

// Analytics tracking — works for keyboard activation too
<Link
  href="/products"
  onClick={() => trackEvent('link_click', { href: '/products' })}
>
  Browse products
</Link>
```

## Theming

Override these CSS custom properties in your theme to restyle every link. Each has a fallback, so overriding is optional.

| Variable | Purpose |
|----------|---------|
| `--link-color` | Default link color. |
| `--link-hover-color` | Hover color. |
| `--link-visited-color` | Visited color (default `#551a8b`). |
| `--link-text-decoration` / `--link-hover-text-decoration` | Underline default and on hover. |
| `--link-focus-outline` / `--link-focus-outline-offset` | Focus ring. |
| `--link-subtle-color` | Subtle-link variant color. |

```css
:root {
  --link-color: #6d28d9;
  --link-hover-color: #5b21b6;
}
```

Generate a full matching theme with `/theme-create` (see [styles.md](../styles.md)).

## Accessibility

- Use descriptive link text ("Read installation guide", not "Click here"); for icon-only links pass `aria-label` (WCAG 2.4.4).
- `target="_blank"` automatically adds `rel="noopener noreferrer"` — `noopener` blocks tabnabbing, `noreferrer` strips the `Referer` header. User rel tokens are merged and deduplicated.
- Native `<a>` gives full keyboard support (Tab + Enter); don't intercept clicks unless a SPA router handles the route, and still allow Cmd/Ctrl-click.
- `:focus-visible` renders a 2 px outline at `currentColor` that adapts to light/dark themes; verify 3:1 contrast in dark themes.
- The default underline is the non-color link indicator (WCAG 1.4.1). Button-style links (`btnStyle`) are still anchors — Enter activates, not Space; use [Button](button.md) if you need true button behavior.

## Related

- [Component index](README.md)
- [Icon](icon.md) — pair with an external-link glyph to mark links that leave the site
- [Button](button.md) — use instead of `btnStyle` when you need real button semantics
- Full maintainer reference: [`skills/component-link/reference.md`](../../skills/component-link/reference.md)
