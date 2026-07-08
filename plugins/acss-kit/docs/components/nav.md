# Nav — Usage Guide

A semantic navigation landmark using the compound pattern `Nav`, `Nav.List`, `Nav.Item`. It renders a `<nav>` wrapping a `<ul>` of `<li>` items, supports horizontal (default) and vertical layouts, and styles the links you place inside each item.

## Add it to your project

1. **One-time setup** (run once per project): `/setup` — installs `sass`, writes `.acss-target.json`, and creates the `ui.tsx` foundation every component imports.
2. **Add this component:** `/kit-add Nav` — copies `nav.tsx` + `nav.scss` into your components directory (default `src/components/fpkit/`).
   - Or run `/kit-sync` once to install **all** components, the foundation, and a starter theme together.

The generated component is self-contained — no `@fpkit/acss` install required.

## Import

`Nav` is a compound component — `Nav`, `Nav.List`, and `Nav.Item` all ship in one file.

```tsx
import Nav from './fpkit/nav/nav'
import './fpkit/nav/nav.scss'
```

Adjust the path to match the `componentsDir` in your `.acss-target.json`.

## Props

**`Nav`**

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `aria-label` | `string` | — | Accessible label; required when more than one `<nav>` exists on the page (WCAG 2.4.8). |
| `classes` | `string` | — | CSS class(es). |
| `styles` | `React.CSSProperties` | — | Inline styles. |
| `children` | `React.ReactNode` | — | Typically `Nav.List` (and an optional logo/link). |

Plus any native `<nav>` attribute (except `className`).

**`Nav.List`**

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `isBlock` | `boolean` | `false` | Vertical (block/column) layout instead of horizontal. |
| `aria-label` | `string` | — | Accessible label for this list. |
| `children` | `React.ReactNode` | — | `Nav.Item` children. |

Plus any native `<ul>` attribute (except `className`).

**`Nav.Item`**

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `id` | `string` | — | Element id. |
| `classes` | `string` | — | CSS class(es). |
| `styles` | `React.CSSProperties` | — | Inline styles. |
| `children` | `React.ReactNode` | — | Item content — usually an `<a>`. |

Plus any native `<li>` attribute (except `className`).

## Examples

```tsx
// Basic horizontal nav
<Nav aria-label="Main navigation">
  <Nav.List>
    <Nav.Item><a href="/" aria-current="page">Home</a></Nav.Item>
    <Nav.Item><a href="/about">About</a></Nav.Item>
    <Nav.Item><a href="/contact">Contact</a></Nav.Item>
  </Nav.List>
</Nav>

// Multiple nav regions (aria-label required — WCAG 2.4.8)
<Nav aria-label="Main navigation">
  <Nav.List>
    <Nav.Item><a href="/">Home</a></Nav.Item>
    <Nav.Item><a href="/products">Products</a></Nav.Item>
  </Nav.List>
</Nav>

<Nav aria-label="Footer navigation">
  <Nav.List>
    <Nav.Item><a href="/privacy">Privacy</a></Nav.Item>
    <Nav.Item><a href="/terms">Terms</a></Nav.Item>
  </Nav.List>
</Nav>

// Vertical sidebar navigation
<Nav aria-label="Sidebar navigation">
  <Nav.List isBlock>
    <Nav.Item><a href="/dashboard">Dashboard</a></Nav.Item>
    <Nav.Item><a href="/settings">Settings</a></Nav.Item>
    <Nav.Item><a href="/profile">Profile</a></Nav.Item>
  </Nav.List>
</Nav>

// Nav with logo and menu
<Nav aria-label="Site navigation">
  <a href="/" aria-label="Go to homepage">
    <img src="/logo.svg" alt="Company Logo" />
  </a>
  <Nav.List>
    <Nav.Item><a href="/products">Products</a></Nav.Item>
    <Nav.Item><a href="/pricing">Pricing</a></Nav.Item>
  </Nav.List>
  <Nav.List aria-label="User actions">
    <Nav.Item><a href="/login">Sign in</a></Nav.Item>
  </Nav.List>
</Nav>
```

## Theming

Override these CSS custom properties in your theme to restyle every nav. Each has a fallback, so overriding is optional.

| Variable | Purpose |
|----------|---------|
| `--nav-justify` | Alignment of nav contents (default `space-between`). |
| `--nav-gap` | Gap between top-level nav children. |
| `--nav-list-gap` | Gap between items in a horizontal list. |
| `--nav-list-block-gap` | Gap between items in a vertical (`isBlock`) list. |
| `--nav-link-color` / `--nav-link-hover-color` | Link text color and hover color. |
| `--nav-link-current-color` / `--nav-link-current-fw` | Color and weight of the `aria-current="page"` link. |
| `--nav-link-radius` | Corner radius on link hit areas. |
| `--nav-link-focus-outline` | Focus ring on links. |

```css
:root {
  --nav-link-hover-color: #6d28d9;
  --nav-link-current-color: #6d28d9;
}
```

Generate a full matching theme with `/theme-create` (see [styles.md](../styles.md)).

## Accessibility

- `<nav>` is a landmark — screen reader users can jump directly to it.
- `aria-label` is required when multiple `<nav>` elements exist on the page (WCAG 2.4.8).
- `aria-current="page"` on the active link announces "current page" to screen readers.
- The `<ul>` + `<li>` structure lets screen readers announce "list of N items".
- Links carry visible `:focus-visible` outlines meeting WCAG 2.4.7.

## Related

- [Component index](README.md)
- [Link component](link.md) — the anchor styling used inside `Nav.Item`
- [List](list.md) — for inline link lists outside a nav landmark
- Full maintainer reference: [`skills/component-nav/reference.md`](../../skills/component-nav/reference.md)
