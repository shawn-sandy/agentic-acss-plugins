---
spec: component.md
version: alpha
name: button
element: button
role: button
tokens:
  background: "{colors.primary}"
  textColor: "{colors.on-primary}"
  rounded: "{rounded.md}"
  paddingBlock: "{spacing.sm}"
  paddingInline: "{spacing.md}"
  typography: "{typography.label-md}"
props:
  type:
    values: [button, submit, reset]
    required: true
  disabled:
    type: boolean
    maps-to: "aria-disabled"
    a11y: "stays in tab order; blocks activation (WCAG 2.1.1)"
  isDisabled:
    type: boolean
    a11y: "legacy compat; `disabled` takes precedence"
  size:
    values: [xs, sm, md, lg, xl, 2xl]
    maps-to: "data-btn"
  color:
    values: [primary, secondary, danger, success, warning]
    maps-to: "data-color"
  block:
    type: boolean
    maps-to: "data-btn=block"
slots: [children]
variants:
  outline: { maps-to: "data-style=outline" }
  text:    { maps-to: "data-style=text" }
  pill:    { maps-to: "data-style=pill" }
  icon:    { maps-to: "data-style=icon" }
behavior: disabled-activation-guard
a11y: [1.4.11, 2.1.1, 2.4.7, 2.5.8, 4.1.2]
targets: [react, html, astro, angular, vue, svelte, web-component]
---

# Component: Button

> **Neutral COMPONENT.md** for the acss-kit `button`. The framework-agnostic
> source of truth lives in the `##` body below; the canonical React projection is
> the `## Target: react` adapter at the end (byte-aligned with the legacy
> `reference.md`). `/kit-add button` reads this file: `## Styles` → `button.scss`,
> `## Target: react` → `button.tsx`.
>
> **Verified against fpkit source:** [`@fpkit/acss@6.5.0`](https://github.com/shawn-sandy/acss/tree/9063512fa822963d8151c972bed9f5b0e531df0f). Intentional divergences:
> `useDisabledState` / `resolveDisabledState` are inlined into the generated
> `button.tsx` rather than imported, and `ButtonProps` is an explicit shape with
> `Omit<...,'disabled'>` — so `/kit-add` emits a self-contained component.

## Overview

The primary interactive element. Supports size, style, and color variants via
data attributes. Uses `aria-disabled` instead of the native `disabled` attribute
so the element stays in the tab order and remains reachable by keyboard users
(WCAG 2.1.1).

## Semantic Structure

```html
<!-- variant: default -->
<button type="button" class="btn">
  <!-- slot: children -->
</button>

<!-- variant: primary -->
<button type="button" class="btn" data-color="primary">
  <!-- slot: children -->
</button>

<!-- variant: large outline -->
<button type="button" class="btn" data-btn="lg" data-style="outline">
  <!-- slot: children -->
</button>

<!-- variant: full-width primary (data-btn="block") -->
<button type="button" class="btn" data-color="primary" data-btn="block">
  <!-- slot: children -->
</button>

<!-- variant: disabled (stays focusable; aria-disabled, not the native attribute) -->
<button
  type="button"
  class="btn is-disabled"
  data-color="primary"
  aria-disabled="true"
>
  <!-- slot: children -->
</button>

<!-- variant: icon-only (always include an aria-label) -->
<button type="button" class="btn" data-style="icon" aria-label="Close">
  <!-- slot: icon -->
</button>
```

The host element is `<button>`. Variants surface as `data-*` attributes; disabled
state surfaces as `aria-disabled="true"` paired with an `is-disabled` class so
visual and assistive states stay in sync (WCAG 2.1.1).

## Props

| Prop | Values | Required | Surfaces as |
|---|---|---|---|
| `type` | `button` \| `submit` \| `reset` | yes | `type` attribute |
| `disabled` | boolean | no | `aria-disabled` + `is-disabled` class |
| `isDisabled` | boolean | no | legacy compat (`disabled` wins) |
| `size` | `xs`…`2xl` | no | `data-btn` token |
| `color` | `primary` \| `secondary` \| `danger` \| `success` \| `warning` | no | `data-color` |
| `block` | boolean | no | `data-btn="block"` |
| variant | `outline` \| `text` \| `pill` \| `icon` | no | `data-style` |

## Tokens & CSS Variables

Themeable properties reference DESIGN.md primitives via `var(--token, <fallback>)`;
each keeps a hardcoded fallback so the component renders with no design system.

```scss
// Size tokens
--btn-size-xs: 0.6875rem;
--btn-size-sm: 0.8125rem;
--btn-size-md: 0.9375rem;   // default
--btn-size-lg: 1.125rem;
--btn-size-xl: 1.25rem;

// Base
--btn-display: inline-flex;
--btn-align: center;
--btn-justify: center;
--btn-gap: var(--space-sm, 0.5rem);
--btn-fs: var(--btn-size-md, 0.9375rem);
--btn-fw: var(--font-label-md-weight, 500);
--btn-radius: var(--radius-md, 0.375rem);
--btn-padding-block: calc(var(--btn-fs, 0.9375rem) * 0.5);
--btn-padding-inline: calc(var(--btn-fs, 0.9375rem) * 1.5);
--btn-bg: transparent;
--btn-color: currentColor;
--btn-border: 1px solid currentColor;
--btn-cursor: pointer;
--btn-transition: all 0.2s ease-in-out;
--btn-text-decoration: none;
--btn-white-space: nowrap;

// Color: primary
--btn-primary-bg: var(--color-primary, #0066cc);
--btn-primary-color: var(--color-text-inverse, #fff);
--btn-primary-border: none;
--btn-primary-hover-bg: var(--color-primary-hover, #0052a3);

// Color: danger
--btn-danger-bg: var(--color-danger, #dc3545);
--btn-danger-color: #fff;
--btn-danger-border: none;

// States
--btn-hover-transform: translateY(-1px);
--btn-hover-filter: brightness(1.05);
--btn-focus-outline: 2px solid currentColor;
--btn-focus-outline-offset: 2px;
--btn-active-transform: translateY(0);

// Disabled
--btn-disabled-opacity: 0.6;
--btn-disabled-cursor: not-allowed;
```

## Styles

```scss
// button.scss
.btn {
  display: var(--btn-display, inline-flex);
  align-items: var(--btn-align, center);
  justify-content: var(--btn-justify, center);
  gap: var(--btn-gap, var(--space-sm, 0.5rem));
  font-size: var(--btn-fs, 0.9375rem);
  font-weight: var(--btn-fw, var(--font-label-md-weight, 500));
  border-radius: var(--btn-radius, var(--radius-md, 0.375rem));
  padding-block: var(--btn-padding-block, 0.46875rem);
  padding-inline: var(--btn-padding-inline, 1.40625rem);
  background: var(--btn-bg, transparent);
  color: var(--btn-color, currentColor);
  border: var(--btn-border, 1px solid currentColor);
  cursor: var(--btn-cursor, pointer);
  transition: var(--btn-transition, all 0.2s ease-in-out);
  text-decoration: none;
  white-space: nowrap;
  line-height: 1;

  &:hover {
    transform: var(--btn-hover-transform, translateY(-1px));
    filter: var(--btn-hover-filter, brightness(1.05));
  }

  &:focus-visible {
    outline: var(--btn-focus-outline, 2px solid currentColor);
    outline-offset: var(--btn-focus-outline-offset, 2px);
  }

  &:active {
    transform: var(--btn-active-transform, translateY(0));
  }

  &[aria-disabled="true"],
  &.is-disabled {
    opacity: var(--btn-disabled-opacity, 0.6);
    cursor: var(--btn-disabled-cursor, not-allowed);
    pointer-events: none;
  }

  // Size variants (data-btn attribute)
  &[data-btn~="xs"] { font-size: var(--btn-size-xs, 0.6875rem); }
  &[data-btn~="sm"] { font-size: var(--btn-size-sm, 0.8125rem); }
  &[data-btn~="lg"] { font-size: var(--btn-size-lg, 1.125rem); }
  &[data-btn~="xl"] { font-size: var(--btn-size-xl, 1.25rem); }
  &[data-btn~="block"] { width: 100%; display: flex; }

  // Style variants (data-style attribute)
  &[data-style="outline"] {
    background: transparent;
    border: 1px solid currentColor;
    color: currentColor;
  }

  &[data-style="text"] {
    background: transparent;
    border: none;
    &:hover { text-decoration: underline; }
  }

  &[data-style="pill"] {
    border-radius: 999px;
  }

  &[data-style="icon"] {
    padding: var(--btn-icon-padding, 0.5rem);
    border-radius: var(--btn-icon-radius, 50%);
    border: none;
    background: transparent;
  }

  // Color variants (data-color attribute)
  &[data-color="primary"] {
    background: var(--btn-primary-bg, var(--color-primary, #0066cc));
    color: var(--btn-primary-color, var(--color-text-inverse, #fff));
    border: var(--btn-primary-border, none);
    &:hover { background: var(--btn-primary-hover-bg, var(--color-primary-hover, #0052a3)); }
  }

  &[data-color="danger"] {
    background: var(--btn-danger-bg, var(--color-danger, #dc3545));
    color: var(--btn-danger-color, #fff);
    border: none;
  }

  &[data-color="success"] {
    background: var(--btn-success-bg, var(--color-success, #28a745));
    color: var(--btn-success-color, #fff);
    border: none;
  }
}
```

## Behavior

**`disabled-activation-guard`** — when `disabled` is set, the button stays
focusable (in tab order) but blocks activation: click and `Enter`/`Space`
handlers are no-ops, and `aria-disabled="true"` announces the state. The visual
`is-disabled` class is kept in sync with the ARIA state. Re-enabling restores
handler behavior.

Neutral reference implementation (static HTML / vanilla JS):

```js
// Idempotent: calling init() twice on the same root does not double-bind.
const SENTINEL = 'data-acss-btn-init';

export function init(root = document, opts = {}) {
  const buttons = root.querySelectorAll('.btn');
  for (const el of buttons) {
    if (el.getAttribute(SENTINEL) === 'true') continue;
    el.setAttribute(SENTINEL, 'true');
    const guard = (e) => {
      if (el.getAttribute('aria-disabled') === 'true') {
        e.preventDefault();
        e.stopPropagation();
        return;
      }
      opts.onActivate?.(e);
    };
    el.addEventListener('click', guard);
    el.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') guard(e);
    });
  }
}
```

A generator realizes this spec idiomatically per target (React hook, Vue
composable, Svelte action, Angular directive); the `react` adapter below ships
the canonical `useDisabledState` hook.

## Accessibility

WCAG 2.2 AA compliance for the generated `Button` component.

**Keyboard interaction**
- `Enter` and `Space` activate the button (native `<button>` behavior; preserved by not overriding the element type).
- The button stays in tab order when disabled — see "Disabled state" below.

**ARIA & screen reader**
- Native `<button>` provides an implicit `role="button"`; do not add an explicit `role` attribute.
- Disabled state uses `aria-disabled="true"` instead of the native `disabled` attribute. Screen readers announce as "dimmed" / "unavailable" while the element remains keyboard-discoverable (WCAG 2.1.1 Keyboard).
- The `is-disabled` class is paired with `aria-disabled` so visual and assistive-tech states stay in sync.
- For icon-only buttons (`variant="icon"`), always pass an `aria-label` — the icon glyph is not an accessible name on its own.

**Focus management**
- `:focus-visible` outline at `var(--btn-focus-outline, 2px solid currentColor)` with `var(--btn-focus-outline-offset, 2px)`. The outline color is `currentColor` so it inherits a visible value across light and dark themes.
- Focus styling is distinct from disabled styling so a focused-disabled button is still visible.
- Pointer and keyboard handlers are gated by `useDisabledState`'s wrappers — the handlers no-op while disabled but the focus state itself is preserved.

**Target size**
- Default size (`md`) with `--btn-padding-block` / `--btn-padding-inline` produces a touch target ≥ 44×44 px, meeting WCAG 2.5.8 Target Size Minimum (Level AA).
- Smaller sizes (`xs`, `sm`) may fall below 44 px. Use them only in dense UI where surrounding spacing or input precision compensates.

**Color contrast**
- Disabled opacity `0.6` reduces the effective contrast of the button against its background. Confirm the disabled appearance still meets WCAG 1.4.11 Non-text Contrast (3:1) for UI components in both light and dark theme modes.
- Color variants (`primary`, `danger`, `success`, `warning`) rely on the project's `--color-*` tokens — see the `styles` skill's CSS Token Convention for required contrast pairings between button surface and label text.

**Disabled state**
- Always pass the typed `disabled?: boolean` prop, never the raw HTML `disabled`. The component renders `aria-disabled="true"` and keeps the element focusable.
- `pointer-events: none` on `[aria-disabled="true"]` blocks click activation; keyboard activation is short-circuited inside `useDisabledState`'s wrappers. The element remains in the tab order so users discovering it via keyboard learn the action exists but is currently unavailable.

**WCAG 2.2 AA criteria addressed**
- 1.4.11 Non-text Contrast (UI states stay legible)
- 2.1.1 Keyboard (full keyboard operability, including disabled state)
- 2.4.7 Focus Visible (`:focus-visible` outline)
- 2.5.8 Target Size Minimum (default size meets 44 px)
- 4.1.2 Name, Role, Value (native button + accessible name when icon-only)

## Examples

```html
<button type="button" class="btn" data-color="primary">Save changes</button>
<button type="button" class="btn" data-style="outline" data-btn="lg">Learn more</button>
<button type="button" class="btn is-disabled" data-color="primary" aria-disabled="true">Unavailable</button>
```

## Target: react

`generation: { export: Button, file: button.tsx, scss: button.scss, imports: "UI from '../ui'", dependencies: [] }`

The React adapter is the canonical TSX projection — `useDisabledState` and
`resolveDisabledState` are inlined into `button.tsx` (no shared hook/util tree).
`/kit-add button --target=react` emits the assembled file: the Props Interface,
the inlined Key Patterns, and the TSX Template below.

## Props Interface

```tsx
/**
 * Props for the Button component.
 *
 * Uses `aria-disabled` instead of the native `disabled` attribute so the
 * element stays in the tab order and remains reachable by keyboard users
 * (WCAG 2.1.1 — Keyboard). Style, size, and color variants are applied via
 * HTML data attributes; see the SCSS template for the corresponding selectors.
 *
 * @see Button
 */
export type ButtonProps = {
  /** Required — prevents implicit submit in forms */
  type: 'button' | 'submit' | 'reset'

  /** Button content */
  children?: React.ReactNode

  /** Accessible disabled — keeps element in tab order (WCAG 2.1.1) */
  disabled?: boolean

  /** Legacy compat. `disabled` takes precedence. */
  isDisabled?: boolean

  /** Maps to data-btn attribute: xs | sm | md | lg | xl | 2xl */
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl'

  /** Maps to data-style attribute: outline | pill | text | icon */
  variant?: 'text' | 'pill' | 'icon' | 'outline'

  /** Maps to data-color attribute: primary | secondary | danger | success | warning */
  color?: 'primary' | 'secondary' | 'danger' | 'success' | 'warning'

  /** Stretches button to 100% width (adds 'block' to data-btn) */
  block?: boolean

  /** CSS class name via classes prop (takes precedence over className) */
  classes?: string

  /** Inline styles (passed to UI) */
  styles?: React.CSSProperties

  /** Raw data-btn tokens merged with size/block */
  'data-btn'?: string

  onClick?: React.MouseEventHandler<HTMLButtonElement>
  onKeyDown?: React.KeyboardEventHandler<HTMLButtonElement>
  onPointerDown?: React.PointerEventHandler<HTMLButtonElement>
  onPointerOver?: React.PointerEventHandler<HTMLButtonElement>
  onPointerLeave?: React.PointerEventHandler<HTMLButtonElement>
} & Omit<React.ComponentPropsWithoutRef<'button'>, 'disabled'>
```

Note: `Omit<..., 'disabled'>` removes the native disabled from button props since we handle it ourselves.

## Key Pattern: Condensed useDisabledState

Inline this condensed version (read `references/accessibility.md` for the full ~50-line version):

```tsx
/**
 * Manages accessible disabled state for interactive elements.
 *
 * Blocks click/keydown/pointerdown handlers when `disabled` is true while
 * keeping the element focusable and announcing its state via `aria-disabled`.
 * Do not use native `disabled` on elements where keyboard reach matters.
 *
 * @internal - inlined into button.tsx; do not extract to a shared module.
 */
// Inline in button.tsx — do not create a separate file
function useDisabledState<T extends HTMLElement = HTMLButtonElement>(
  disabled: boolean | undefined,
  handlers: {
    onClick?: (e: React.MouseEvent<T>) => void
    onKeyDown?: (e: React.KeyboardEvent<T>) => void
    onPointerDown?: (e: React.PointerEvent<T>) => void
  } = {},
  className?: string
) {
  const isDisabled = Boolean(disabled)
  const mergedClassName = [isDisabled ? 'is-disabled' : '', className]
    .filter(Boolean).join(' ')

  const wrap = <E,>(fn?: (e: E) => void) => fn
    ? (e: any) => { if (isDisabled) { e.preventDefault(); e.stopPropagation(); return } fn(e) }
    : undefined

  return {
    disabledProps: { 'aria-disabled': isDisabled, className: mergedClassName },
    handlers: {
      onClick: wrap(handlers.onClick),
      onKeyDown: wrap(handlers.onKeyDown),
      onPointerDown: wrap(handlers.onPointerDown),
    },
  }
}
```

## Key Pattern: resolveDisabledState

```tsx
/**
 * Resolves the active disabled state from `disabled` and legacy `isDisabled`
 * props. `disabled` takes precedence; both default to `false` if absent.
 *
 * @internal - inlined into button.tsx; do not extract to a shared module.
 */
// One-liner helper — inline in button.tsx
const resolveDisabledState = (d?: boolean, id?: boolean) => d ?? id ?? false
```

## Key Pattern: data-btn Merging

```tsx
// Merge size, block, and explicit data-btn into one space-separated string
const { 'data-btn': dataBtnProp, ...restProps } = props
const dataBtnValue = [size, block ? 'block' : undefined, dataBtnProp]
  .filter(Boolean).join(' ') || undefined
```

## TSX Template

```tsx
import UI from '../ui'
import React from 'react'

// [inline resolveDisabledState and useDisabledState here]

/**
 * Accessible button with size, style, and color variants.
 *
 * Replaces the native `disabled` attribute with `aria-disabled` so the button
 * stays keyboard-reachable even when functionally inactive (WCAG 2.1.1).
 * Variants are driven by data attributes (`data-btn`, `data-style`,
 * `data-color`) and styled entirely via CSS custom properties — no inline
 * styles required for theming.
 *
 * @param props - {@link ButtonProps}
 *
 * @example
 * // Primary submit button
 * <Button type="submit" color="primary">Save changes</Button>
 *
 * @example
 * // Large outline button, accessible disabled
 * <Button type="button" variant="outline" size="lg" disabled>
 *   Unavailable
 * </Button>
 */
export const Button = ({
  type = 'button',
  children,
  styles,
  disabled,
  isDisabled,
  classes,
  size,
  variant,
  color,
  block,
  onPointerDown,
  onPointerOver,
  onPointerLeave,
  onClick,
  onKeyDown,
  ...props
}: ButtonProps) => {
  const isActuallyDisabled = resolveDisabledState(disabled, isDisabled)
  const { disabledProps, handlers } = useDisabledState(
    isActuallyDisabled,
    { onClick, onPointerDown, onKeyDown },
    classes,
  )

  const { 'data-btn': dataBtnProp, ...restProps } = props
  const dataBtnValue = [size, block ? 'block' : undefined, dataBtnProp]
    .filter(Boolean).join(' ') || undefined

  return (
    <UI
      as="button"
      type={type}
      data-btn={dataBtnValue}
      data-style={variant}
      data-color={color}
      aria-disabled={disabledProps['aria-disabled']}
      onPointerOver={onPointerOver}
      onPointerLeave={onPointerLeave}
      style={styles}
      className={disabledProps.className}
      {...restProps}
      {...handlers}
    >
      {children}
    </UI>
  )
}

export default Button
Button.displayName = 'Button'
```
