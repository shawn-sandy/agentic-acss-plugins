# Img — Usage Guide

A semantic image component with accessibility and performance defaults. Wraps the native `<img>` with lazy loading, an automatic SVG-gradient placeholder on load error, `srcSet` / `sizes` responsive support, and `fetchpriority` / `decoding` performance hints. The `alt` prop is required by the type.

## Add it to your project

1. **One-time setup** (run once per project): `/setup` — installs `sass`, writes `.acss-target.json`, and creates the `ui.tsx` foundation every component imports.
2. **Add this component:** `/kit-add Img` — copies `img.tsx` + `img.scss` into your components directory (default `src/components/fpkit/`).
   - Or run `/kit-sync` once to install **all** components, the foundation, and a starter theme together.

The generated component is self-contained — no `@fpkit/acss` install required.

## Import

```tsx
import Img from './fpkit/img/img'
import './fpkit/img/img.scss'
```

Adjust the path to match the `componentsDir` in your `.acss-target.json`.

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `alt` | `string` | — (required) | Alt text; empty string for decorative images. |
| `src` | `string` | `'//'` | Image source URL. |
| `width` | `number \| string` | `480` | Image width (number = px). |
| `height` | `number \| string` | `'auto'` | Image height (number = px). |
| `loading` | `'lazy' \| 'eager'` | `lazy` | Loading strategy for below/above-the-fold images. |
| `placeholder` | `string` | generated SVG | Custom fallback URL when `src` fails to load. |
| `fetchpriority` | `'high' \| 'low' \| 'auto'` | `low` | Fetch priority hint. |
| `decoding` | `'sync' \| 'async' \| 'auto'` | `auto` | Decoding strategy. |
| `srcSet` | `string` | — | Responsive image candidates. |
| `sizes` | `string` | — | Responsive sizes hint. |
| `styles` | `React.CSSProperties` | — | Inline styles. |
| `onError` | `(e) => void` | — | Runs before the placeholder swap; call `e.preventDefault()` to skip it. |
| `onLoad` | `(e) => void` | — | Native load handler. |

Plus any native `<img>` attribute except the overridden `src`, `alt`, `onError`, `onLoad`.

## Examples

```tsx
// Decorative
<Img src="/decorative-border.svg" alt="" />

// Informative
<Img
  src="/sales-chart.png"
  alt="Sales chart showing 30% revenue growth in Q4 2024"
  width={800}
  height={400}
/>

// Hero (above the fold)
<Img
  src="/hero.jpg"
  alt="Two engineers reviewing code on a laptop"
  width={1200}
  height={600}
  loading="eager"
  fetchpriority="high"
/>

// Responsive
<Img
  src="/photo.jpg"
  srcSet="/photo-320w.jpg 320w, /photo-640w.jpg 640w, /photo-1024w.jpg 1024w"
  sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 800px"
  alt="Mountain range at sunset"
  width={1024}
  height={768}
/>

// Custom fallback + error logging
<Img
  src="/avatar.jpg"
  placeholder="/default-avatar.svg"
  alt="User profile photo"
  onError={(e) => analytics('image_error', { src: e.currentTarget.src })}
/>
```

## Theming

Override these CSS custom properties in your theme to restyle every image. Each has a fallback, so overriding is optional.

| Variable | Purpose |
|----------|---------|
| `--img-display` | Display mode (default `block`). |
| `--img-max-width` | Max width (default `100%`). |
| `--img-height` | Height (default `auto`). |
| `--img-object-fit` | Object-fit behavior (default `cover`). |
| `--img-radius` | Corner radius (default `var(--radius-none, 0)`). |

```css
:root {
  --img-radius: 0.75rem;
  --img-object-fit: contain;
}
```

Generate a full matching theme with `/theme-create` (see [styles.md](../styles.md)).

## Accessibility

- `alt` is required by the type — pass `alt=""` for purely decorative images, or a descriptive `alt` that conveys purpose and content for informative ones.
- Always pass explicit `width` and `height` so the browser reserves layout space and avoids Cumulative Layout Shift.
- Pair `loading="eager"` with `fetchpriority="high"` for the LCP (hero) image; defaults are `lazy` + `low` for off-screen images.
- On load error the component swaps in a generated SVG-gradient data-URI placeholder (no network request), guarding against an infinite error loop.
- `max-width: 100%` via SCSS prevents horizontal scroll on small viewports (WCAG 1.4.10 Reflow).

## Related

- [Component index](README.md)
- Full maintainer reference: [`skills/component-img/reference.md`](../../skills/component-img/reference.md)
