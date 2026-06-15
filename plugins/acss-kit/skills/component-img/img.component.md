---
spec: component.md
version: alpha
name: img
element: img
tokens:
  rounded: "{rounded.none}"
props:
  src:
    type: string
  alt:
    type: string
    required: true
    a11y: "empty string for decorative; descriptive for informative (WCAG 1.1.1)"
  width:
    type: "number | string"
  height:
    type: "number | string"
  loading:
    values: [lazy, eager]
    default: lazy
    maps-to: "loading"
  placeholder:
    type: string
  fetchpriority:
    values: [high, low, auto]
    default: low
    maps-to: "fetchpriority"
  decoding:
    values: [sync, async, auto]
    default: auto
    maps-to: "decoding"
  srcSet:
    type: string
    maps-to: "srcset"
  sizes:
    type: string
    maps-to: "sizes"
slots: []
variants: {}
a11y: [1.1.1, 1.4.5, 1.4.10]
targets: [react, html, astro, angular, vue, svelte, web-component]
---

# Component: Img

> **Neutral COMPONENT.md** for the acss-kit `img`. The framework-agnostic
> source of truth lives in the `##` body below; the canonical React projection is
> the `## Target: react` adapter at the end (byte-aligned with the legacy
> `reference.md`). `/kit-add img` reads this file: `## Styles` → `img.scss`,
> `## Target: react` → `img.tsx`.
>
> **Verified against fpkit source:** [`@fpkit/acss@6.5.0`](https://github.com/shawn-sandy/acss/tree/9063512fa822963d8151c972bed9f5b0e531df0f) (closest tagged ref to
> npm `6.6.0`). The vendored Img keeps the upstream feature set: lazy loading
> default, error handling with a generated SVG-gradient placeholder, `srcSet` /
> `sizes` responsive support, `fetchpriority` / `decoding` performance hints. The
> placeholder is a memoized data URI so there are zero network requests when the
> fallback fires.

## Overview

A semantic image component with accessibility and performance defaults. Wraps the native `<img>` element with lazy loading, custom error handling, an automatic SVG-gradient placeholder, and full TypeScript prop support. The accessible-name behaviour follows WAI-ARIA: pass `alt=""` for decorative images, or a descriptive `alt` for informative ones.

## Semantic Structure

```html
<!-- variant: informative -->
<img
  src="/sales-chart.png"
  alt="Sales chart showing 30% revenue growth in Q4 2024"
  width="800"
  height="400"
  loading="lazy"
  decoding="auto"
/>

<!-- variant: decorative (empty alt — screen readers skip it) -->
<img src="/decorative-border.svg" alt="" loading="lazy" />

<!-- variant: hero / above-the-fold (eager + high priority) -->
<img
  src="/hero.jpg"
  alt="Two engineers reviewing code on a laptop"
  width="1200"
  height="600"
  loading="eager"
  fetchpriority="high"
/>

<!-- variant: responsive (srcset + sizes) -->
<img
  src="/photo.jpg"
  srcset="/photo-320w.jpg 320w, /photo-640w.jpg 640w, /photo-1024w.jpg 1024w"
  sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 800px"
  alt="Mountain range at sunset"
  width="1024"
  height="768"
/>
```

The host element is `<img>`. The `alt` attribute is always present (required) —
empty for decorative images, descriptive for informative ones. Performance hints
(`loading`, `fetchpriority`, `decoding`) and responsive attributes (`srcset`,
`sizes`) surface as native attributes. When `src` fails to load, the runtime swaps
in a generated SVG-gradient placeholder data URI (see the `react` adapter).

## Props

| Prop | Values | Required | Surfaces as |
|---|---|---|---|
| `src` | string | no | `src` attribute |
| `alt` | string | yes | `alt` attribute (empty for decorative) |
| `width` | number \| string | no | `width` attribute |
| `height` | number \| string | no | `height` attribute (defaults to `auto`) |
| `loading` | `lazy` \| `eager` | no | `loading` attribute |
| `placeholder` | string | no | fallback `src` on error |
| `fetchpriority` | `high` \| `low` \| `auto` | no | `fetchpriority` attribute |
| `decoding` | `sync` \| `async` \| `auto` | no | `decoding` attribute |
| `srcSet` | string | no | `srcset` attribute |
| `sizes` | string | no | `sizes` attribute |

## Tokens & CSS Variables

Themeable properties reference DESIGN.md primitives via `var(--token, <fallback>)`;
each keeps a hardcoded fallback so the component renders with no design system.

```scss
--img-display: block;
--img-max-width: 100%;
--img-height: auto;
--img-object-fit: cover;
--img-radius: var(--radius-none, 0);
```

## Styles

```scss
// img.scss
img {
  display: var(--img-display, block);
  max-width: var(--img-max-width, 100%);
  height: var(--img-height, auto);
  object-fit: var(--img-object-fit, cover);
  border-radius: var(--img-radius, var(--radius-none, 0));
}
```

## Accessibility

WCAG 2.2 AA compliance for the generated `Img` component.

**Alt text — required**
- The `alt` prop is required by the `ImgProps` type. TypeScript prevents accidentally rendering an `<img>` without `alt`.
- Pass `alt=""` for purely decorative images (borders, patterns, separators) — screen readers skip them entirely. This is correct, not a workaround.
- Pass a descriptive `alt` for informative images (charts, photos that convey content). Describe the *purpose* and *content*, not the file format ("Sales chart showing 30% Q4 revenue growth", not "JPG of a chart").
- Never duplicate adjacent text. If a caption is right next to the image saying "Bar chart of sales", the image's alt should be different ("Sales by quarter; Q4 dominant") or empty (caption already describes it).

**Layout shift prevention**
- Always pass explicit `width` and `height` so the browser reserves layout space before the image loads. Mitigates Cumulative Layout Shift (Core Web Vitals).
- The default `width={480}` exists so the placeholder SVG has a sensible default size; override it for real layouts.

**Loading & priority**
- Default `loading="lazy"` defers below-the-fold images. Pass `loading="eager"` for above-the-fold hero images.
- Pair `loading="eager"` with `fetchpriority="high"` for the LCP (Largest Contentful Paint) image. Defaults are `lazy` + `low` for off-screen images.

**Error handling**
- When the image fails to load, the component swaps in a generated SVG-gradient placeholder so the layout doesn't collapse. The placeholder is a data URI (no network), memoized by `(width, height)`.
- The `onError` callback runs first, so callers can log/analytics before the fallback applies. Calling `e.preventDefault()` skips the placeholder swap entirely.
- The implementation guards against an infinite error loop by not re-assigning `src` if it already equals the fallback.

**Color contrast (placeholder)**
- The SVG placeholder includes `WIDTH×HEIGHT` text in white at ~90% opacity over a vivid gradient. Contrast varies depending on viewport-mapped gradient stops; treat the placeholder as decorative (not informative). For environments where text contrast on the placeholder matters, override `placeholder` with a custom URL.

**Responsive images**
- Pass `srcSet` + `sizes` for responsive images. The browser picks the most appropriate candidate based on viewport width and DPR — both better performance and better visual quality.

**WCAG 2.2 AA criteria addressed**
- 1.1.1 Non-text Content (alt is required by type; empty alt for decorative)
- 1.4.5 Images of Text (use real text where possible; the type doesn't enforce this — it's an authoring concern)
- 1.4.10 Reflow (max-width: 100% via SCSS prevents horizontal scroll on small viewports)

## Examples

```html
<!-- Decorative -->
<img src="/decorative-border.svg" alt="" />

<!-- Informative -->
<img
  src="/sales-chart.png"
  alt="Sales chart showing 30% revenue growth in Q4 2024"
  width="800"
  height="400"
/>

<!-- Hero (above the fold) -->
<img
  src="/hero.jpg"
  alt="Two engineers reviewing code on a laptop"
  width="1200"
  height="600"
  loading="eager"
  fetchpriority="high"
/>

<!-- Responsive -->
<img
  src="/photo.jpg"
  srcset="/photo-320w.jpg 320w, /photo-640w.jpg 640w, /photo-1024w.jpg 1024w"
  sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 800px"
  alt="Mountain range at sunset"
  width="1024"
  height="768"
/>
```

## Target: react

`generation: { export: Img, file: img.tsx, scss: img.scss, imports: "UI from '../ui', React with useMemo", dependencies: [] }`

The React adapter is the canonical TSX projection. `/kit-add img --target=react`
emits the assembled file: the Props Interface(s), the SVG-gradient placeholder Key
Pattern, and the TSX Template below.

## Props Interface(s)

```tsx
export type ImgProps = {
  /** Image source URL */
  src?: string
  /** Required alt text — empty string for decorative images */
  alt: string
  /** Image width (number = px) */
  width?: number | string
  /** Image height (number = px). Defaults to "auto" if width is set. */
  height?: number | string
  /** Inline styles */
  styles?: React.CSSProperties
  /** Loading strategy — "lazy" by default for below-the-fold images */
  loading?: 'lazy' | 'eager'
  /** Custom fallback URL when src fails to load. Defaults to a generated SVG. */
  placeholder?: string
  /** Fetch priority hint */
  fetchpriority?: 'high' | 'low' | 'auto'
  /** Decoding strategy */
  decoding?: 'sync' | 'async' | 'auto'
  /** Responsive image candidates */
  srcSet?: string
  /** Responsive sizes hint */
  sizes?: string
  /** Custom error handler — call e.preventDefault() to skip the placeholder */
  onError?: (e: React.SyntheticEvent<HTMLImageElement, Event>) => void
  onLoad?: (e: React.SyntheticEvent<HTMLImageElement, Event>) => void
} & Omit<React.ImgHTMLAttributes<HTMLImageElement>, 'src' | 'alt' | 'onError' | 'onLoad'>
```

## Key Pattern: SVG-gradient placeholder

```tsx
// Generated SVG-gradient placeholder — memoized, zero network requests.
const defaultPlaceholder = useMemo(() => {
  const w = typeof width === 'number' ? width : 480
  const h = typeof height === 'number' ? height : Math.round(w * 0.75)
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${w} ${h}">
    <defs>
      <linearGradient id="grad-${w}-${h}" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" style="stop-color:#6366f1"/>
        <stop offset="50%" style="stop-color:#8b5cf6"/>
        <stop offset="100%" style="stop-color:#ec4899"/>
      </linearGradient>
    </defs>
    <rect width="${w}" height="${h}" fill="url(#grad-${w}-${h})"/>
    <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle"
          font-family="system-ui,-apple-system,sans-serif"
          font-size="${Math.max(16, Math.min(w, h) * 0.05)}"
          font-weight="500" fill="rgba(255,255,255,0.9)">${w}×${h}</text>
  </svg>`
  return `data:image/svg+xml,${encodeURIComponent(svg)}`
}, [width, height])
```

## TSX Template

```tsx
import UI from '../ui'
import React, { useMemo } from 'react'

export type ImgProps = {
  src?: string
  alt: string
  width?: number | string
  height?: number | string
  styles?: React.CSSProperties
  loading?: 'lazy' | 'eager'
  placeholder?: string
  fetchpriority?: 'high' | 'low' | 'auto'
  decoding?: 'sync' | 'async' | 'auto'
  srcSet?: string
  sizes?: string
  onError?: (e: React.SyntheticEvent<HTMLImageElement, Event>) => void
  onLoad?: (e: React.SyntheticEvent<HTMLImageElement, Event>) => void
} & Omit<React.ImgHTMLAttributes<HTMLImageElement>, 'src' | 'alt' | 'onError' | 'onLoad'>

export const Img = ({
  src = '//',
  alt,
  width = 480,
  height,
  styles,
  loading = 'lazy',
  placeholder,
  fetchpriority = 'low',
  decoding = 'auto',
  srcSet,
  sizes,
  onError,
  onLoad,
  ...props
}: ImgProps) => {
  // Generated SVG-gradient placeholder — memoized, zero network requests.
  const defaultPlaceholder = useMemo(() => {
    const w = typeof width === 'number' ? width : 480
    const h = typeof height === 'number' ? height : Math.round(w * 0.75)
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${w} ${h}">
      <defs>
        <linearGradient id="grad-${w}-${h}" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style="stop-color:#6366f1"/>
          <stop offset="50%" style="stop-color:#8b5cf6"/>
          <stop offset="100%" style="stop-color:#ec4899"/>
        </linearGradient>
      </defs>
      <rect width="${w}" height="${h}" fill="url(#grad-${w}-${h})"/>
      <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle"
            font-family="system-ui,-apple-system,sans-serif"
            font-size="${Math.max(16, Math.min(w, h) * 0.05)}"
            font-weight="500" fill="rgba(255,255,255,0.9)">${w}×${h}</text>
    </svg>`
    return `data:image/svg+xml,${encodeURIComponent(svg)}`
  }, [width, height])

  const fallbackPlaceholder = placeholder ?? defaultPlaceholder

  const handleImgError = (e: React.SyntheticEvent<HTMLImageElement, Event>): void => {
    onError?.(e)
    if (!e.defaultPrevented && e.currentTarget.src !== fallbackPlaceholder) {
      e.currentTarget.src = fallbackPlaceholder
    }
  }

  const handleImgLoad = (e: React.SyntheticEvent<HTMLImageElement, Event>): void => {
    onLoad?.(e)
  }

  return (
    <UI
      as="img"
      src={src}
      alt={alt}
      width={width}
      height={height || 'auto'}
      loading={loading}
      style={styles}
      srcSet={srcSet}
      sizes={sizes}
      onError={handleImgError}
      onLoad={handleImgLoad}
      decoding={decoding}
      {...props}
      {...(fetchpriority && { fetchpriority })}
    />
  )
}

Img.displayName = 'Img'
export default Img
```
