---
spec: component.md
version: alpha
name: icon-button
element: button
role: button
tokens:
  size: "{spacing.xl}"
  rounded: "{rounded.full}"
  gap: "{spacing.sm}"
  labelTypography: "{typography.label-md}"
props:
  icon:
    required: true
    a11y: "decorative glyph; accessible name comes from aria-label/aria-labelledby"
  label:
    type: string
    a11y: "stays in a11y tree at all viewports; visually hidden below --icon-label-bp"
  type:
    values: [button, submit, reset]
    required: true
  aria-label:
    type: string
    a11y: "XOR with aria-labelledby — exactly one required (WCAG 1.1.1, 4.1.2)"
  aria-labelledby:
    type: string
    a11y: "XOR with aria-label — exactly one required (WCAG 1.1.1, 4.1.2)"
slots: [icon]
variants:
  icon:        { maps-to: "data-icon-btn=icon" }
  has-label:   { maps-to: "data-icon-btn=has-label" }
a11y: [1.1.1, 1.4.11, 2.1.1, 2.4.7, 2.5.5, 2.5.8, 4.1.2]
targets: [react, html, astro, angular, vue, svelte, web-component]
---

# Component: IconButton

> **Neutral COMPONENT.md** for the acss-kit `icon-button`. The framework-agnostic
> source of truth lives in the `##` body below; the canonical React projection is
> the `## Target: react` adapter at the end (byte-aligned with the legacy
> `reference.md`). `/kit-add icon-button` reads this file: `## Styles` →
> `icon-button.scss`, `## Target: react` → `icon-button.tsx`. Depends on `button`.
>
> **Verified against fpkit source:** `@fpkit/acss@6.5.0` (closest tagged ref to npm `6.6.0`). The vendored IconButton imports the kit-builder `Button` and applies `variant="icon"` plus the XOR-typed accessible-name constraint from upstream. The optional `label` text uses a media-query reveal for desktop widths so the label is always in the accessibility tree but visually hidden on mobile.

## Overview

An accessible icon-only (or icon + label) button. Built on top of `Button` from the same generated component set. A TypeScript XOR type requires exactly one of `aria-label` or `aria-labelledby` at compile time, providing both the icon's text alternative (WCAG 1.1.1 Non-text Content) and the button's accessible name (WCAG 4.1.2 Name, Role, Value).

## Semantic Structure

```html
<!-- variant: icon-only (always include an aria-label or aria-labelledby) -->
<button type="button" class="btn" data-icon-btn="icon" aria-label="Close menu">
  <!-- slot: icon -->
</button>

<!-- variant: icon + responsive label (label hidden below 48rem; always in a11y tree) -->
<button type="button" class="btn" data-icon-btn="has-label" aria-label="Settings">
  <!-- slot: icon -->
  <span data-icon-label>Settings</span>
</button>

<!-- variant: labelled by external element -->
<span id="del-label">Delete item</span>
<button type="button" class="btn" data-icon-btn="icon" aria-labelledby="del-label">
  <!-- slot: icon -->
</button>
```

The host element is `<button>` (projected through the `Button` component). The icon
slot holds the glyph; an optional `[data-icon-label]` span carries the responsive
label. The `data-icon-btn` attribute distinguishes icon-only (`icon`) from
label-bearing (`has-label`) geometry.

## Props

| Prop | Values | Required | Surfaces as |
|---|---|---|---|
| `icon` | `ReactNode` | yes | icon slot content |
| `label` | string | no | `[data-icon-label]` span + `data-icon-btn="has-label"` |
| `type` | `button` \| `submit` \| `reset` | yes | `type` attribute |
| `aria-label` | string | XOR | accessible name (exactly one of `aria-label` / `aria-labelledby`) |
| `aria-labelledby` | string | XOR | accessible name (exactly one of `aria-label` / `aria-labelledby`) |

The XOR constraint means passing both `aria-label` AND `aria-labelledby` (or neither) is a TypeScript compile-time error. This guarantees the icon glyph has a programmatic text alternative (WCAG 1.1.1) and the button has an accessible name (WCAG 4.1.2) at the type level — the icon alone is never sufficient.

## Tokens & CSS Variables

```scss
--icon-btn-size: 3rem;             // 48px tap target (WCAG 2.5.5 AAA)
--icon-btn-padding: 0;
--icon-btn-radius: 50%;
--icon-btn-gap: var(--space-sm, 0.5rem);
--icon-label-bp: 48rem;            // Breakpoint above which label appears
--icon-label-fs: 0.9375rem;
```

## Styles

```scss
// icon-button.scss
.btn[data-icon-btn] {
  width: var(--icon-btn-size, 3rem);
  height: var(--icon-btn-size, 3rem);
  padding: var(--icon-btn-padding, 0);
  border-radius: var(--icon-btn-radius, 50%);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--icon-btn-gap, var(--space-sm, 0.5rem));
  border: none;
  background: transparent;
}

.btn[data-icon-btn="has-label"] {
  // Restore button-like geometry when a label is present
  width: auto;
  border-radius: var(--btn-radius, 0.375rem);
  padding-inline: var(--btn-padding-inline, 1.40625rem);
}

[data-icon-label] {
  // Visually hidden below the breakpoint; in accessibility tree at all sizes
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;

  @media (min-width: 48rem) {
    position: static;
    width: auto;
    height: auto;
    overflow: visible;
    clip: auto;
    white-space: normal;
    font-size: var(--icon-label-fs, 0.9375rem);
  }
}
```

## Accessibility

WCAG 2.2 AA compliance for the generated `IconButton` component.

**Accessible name (required)**
- The `IconButtonProps` XOR type requires exactly one of `aria-label` or `aria-labelledby` at compile time. Passing both — or neither — is a TypeScript error. This makes both the icon's text alternative (WCAG 1.1.1) and the button's accessible name (WCAG 4.1.2) build-time guarantees.
- The icon glyph is decorative as far as assistive tech is concerned; the accessible name comes entirely from `aria-label` / `aria-labelledby`.
- When the optional `label` is also passed, it stays in the accessibility tree at every viewport size. If `label` and `aria-label` say different things, screen readers may announce both — keep them consistent or omit `label` for icon-only.

**Keyboard interaction**
- Inherits all keyboard behavior from `Button`: native `<button>` semantics, Enter/Space activation, `aria-disabled` for disabled state (stays in tab order).
- `:focus-visible` outline inherits from `button.scss`.

**Target size**
- Default `--icon-btn-size: 3rem` (48 px at root font size 16) exceeds WCAG 2.5.5 Target Size (AAA, 44 px). When `label` mode is active, the button widens further; target size is satisfied at all viewports.
- If overriding `--icon-btn-size` to something smaller than 44 px, ensure surrounding spacing or pointer accuracy compensates (WCAG 2.5.8 Target Size Minimum, AA).

**Color contrast**
- IconButton inherits color tokens from `Button`. The icon color is `currentColor`, so contrast against the button background is the same as button label text — must meet 4.5:1 for text-equivalent glyphs, or 3:1 for purely-graphical icons per WCAG 1.4.11 Non-text Contrast.

**Responsive label**
- The optional `label` is hidden visually below `48rem` via a media query, but stays in the accessibility tree (positioned off-screen with `clip`, not `display: none`). Screen readers announce it at every viewport size.

**WCAG 2.2 AA criteria addressed**
- 1.1.1 Non-text Content (XOR-enforced text alternative for icon glyph)
- 1.4.11 Non-text Contrast (icon glyph at 3:1)
- 2.1.1 Keyboard (inherited from Button)
- 2.4.7 Focus Visible (inherited from Button)
- 2.5.5 / 2.5.8 Target Size (3rem default exceeds both AA and AAA thresholds)
- 4.1.2 Name, Role, Value (native button + required accessible name)

## Examples

```html
<!-- Icon-only -->
<button type="button" class="btn" data-icon-btn="icon" aria-label="Close menu">
  <svg aria-hidden="true"><!-- close icon --></svg>
</button>

<!-- Icon + responsive label -->
<button type="button" class="btn" data-icon-btn="has-label" aria-label="Settings">
  <svg aria-hidden="true"><!-- settings icon --></svg>
  <span data-icon-label>Settings</span>
</button>

<!-- Labelled by external element -->
<span id="del-label">Delete item</span>
<button type="button" class="btn" data-icon-btn="icon" aria-labelledby="del-label">
  <svg aria-hidden="true"><!-- trash icon --></svg>
</button>
```

## Target: react

`generation: { export: IconButton, file: icon-button.tsx, scss: icon-button.scss, imports: "Button from '../button/button', type ButtonProps", dependencies: [button] }`

The React adapter is the canonical TSX projection — `IconButton` wraps the
generated `Button` and adds the XOR-typed accessible-name constraint.
`/kit-add icon-button --target=react` emits the Props Interface and the TSX
Template below; Button must already exist in the target directory (dependency).

## Props Interface

```tsx
type WithAriaLabel = { 'aria-label': string; 'aria-labelledby'?: never }
type WithAriaLabelledBy = { 'aria-labelledby': string; 'aria-label'?: never }

export type IconButtonProps = Omit<ButtonProps, 'children'> &
  (WithAriaLabel | WithAriaLabelledBy) & {
    /** The icon element rendered inside the button */
    icon: React.ReactNode
    /**
     * Optional text shown alongside the icon at desktop widths.
     * Visually hidden below the icon-label breakpoint via a media query
     * on `[data-icon-label]`, but always present in the accessibility
     * tree — screen readers announce it at every viewport size.
     */
    label?: string
    /** Required to prevent implicit submit in forms */
    type: 'button' | 'submit' | 'reset'
  }
```

The XOR constraint means passing both `aria-label` AND `aria-labelledby` (or neither) is a TypeScript compile-time error. This guarantees the icon glyph has a programmatic text alternative (WCAG 1.1.1) and the button has an accessible name (WCAG 4.1.2) at the type level — the icon alone is never sufficient.

## TSX Template

```tsx
import React from 'react'
import Button, { type ButtonProps } from '../button/button'

type WithAriaLabel = { 'aria-label': string; 'aria-labelledby'?: never }
type WithAriaLabelledBy = { 'aria-labelledby': string; 'aria-label'?: never }

export type IconButtonProps = Omit<ButtonProps, 'children'> &
  (WithAriaLabel | WithAriaLabelledBy) & {
    icon: React.ReactNode
    label?: string
    type: 'button' | 'submit' | 'reset'
  }

export const IconButton = ({
  icon,
  label,
  variant = 'icon',
  type = 'button',
  ...props
}: IconButtonProps) => (
  <Button
    variant={variant}
    data-icon-btn={label ? 'has-label' : 'icon'}
    {...props}
    type={type}
  >
    {icon}
    {label && <span data-icon-label>{label}</span>}
  </Button>
)

IconButton.displayName = 'IconButton'
export default IconButton
```
