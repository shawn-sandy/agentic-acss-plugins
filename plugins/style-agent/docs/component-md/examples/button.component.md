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

<!-- variant: disabled (stays focusable; aria-disabled, not the native attribute) -->
<button type="button" class="btn is-disabled" data-color="primary" aria-disabled="true">
  <!-- slot: children -->
</button>

<!-- variant: icon-only (always include an aria-label) -->
<button type="button" class="btn" data-style="icon" aria-label="Close">
  <!-- slot: icon -->
</button>
```

The host element is `<button>`. Variants surface as `data-*` attributes; disabled
state surfaces as `aria-disabled="true"` paired with an `is-disabled` class so
visual and assistive states stay in sync.

## Props

| Prop | Values | Required | Surfaces as |
|---|---|---|---|
| `type` | `button` \| `submit` \| `reset` | yes | `type` attribute |
| `disabled` | boolean | no | `aria-disabled` + `is-disabled` class |
| `size` | `xs`…`2xl` | no | `data-btn` token |
| `color` | `primary` \| `secondary` \| `danger` \| `success` \| `warning` | no | `data-color` |
| `block` | boolean | no | `data-btn="block"` |
| variant | `outline` \| `text` \| `pill` \| `icon` | no | `data-style` |

## Tokens & CSS Variables

Themeable properties reference DESIGN.md primitives; each keeps a hardcoded
fallback so the component renders with no design system present.

```scss
--btn-primary-bg: var(--color-primary, #0066cc);        /* {colors.primary} */
--btn-primary-color: var(--color-text-inverse, #fff);   /* {colors.on-primary} */
--btn-radius: 0.375rem;                                  /* {rounded.md} */
--btn-padding-block: calc(var(--btn-fs, 0.9375rem) * 0.5);   /* {spacing.sm} */
--btn-padding-inline: calc(var(--btn-fs, 0.9375rem) * 1.5);  /* {spacing.md} */
--btn-fs: var(--btn-size-md, 0.9375rem);                 /* {typography.label-md} */
--btn-fw: 500;
--btn-focus-outline: 2px solid currentColor;
--btn-disabled-opacity: 0.6;
```

## Styles

```scss
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--btn-gap, 0.5rem);
  font-size: var(--btn-fs, 0.9375rem);
  font-weight: var(--btn-fw, 500);
  border-radius: var(--btn-radius, 0.375rem);
  padding-block: var(--btn-padding-block, 0.46875rem);
  padding-inline: var(--btn-padding-inline, 1.40625rem);
  background: var(--btn-bg, transparent);
  color: var(--btn-color, currentColor);
  border: var(--btn-border, 1px solid currentColor);
  cursor: pointer;
  transition: var(--btn-transition, all 0.2s ease-in-out);
  line-height: 1;

  &:focus-visible {
    outline: var(--btn-focus-outline, 2px solid currentColor);
    outline-offset: var(--btn-focus-outline-offset, 2px);
  }

  &[aria-disabled="true"],
  &.is-disabled {
    opacity: var(--btn-disabled-opacity, 0.6);
    cursor: not-allowed;
    pointer-events: none;
  }

  &[data-btn~="lg"] { font-size: var(--btn-size-lg, 1.125rem); }
  &[data-style="outline"] { background: transparent; border: 1px solid currentColor; }
  &[data-style="pill"] { border-radius: 999px; }
  &[data-color="primary"] {
    background: var(--btn-primary-bg, var(--color-primary, #0066cc));
    color: var(--btn-primary-color, var(--color-text-inverse, #fff));
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
the canonical hook.

## Accessibility

- **Keyboard** — `Enter` and `Space` activate (native `<button>`); the button
  stays in tab order when disabled.
- **ARIA & screen reader** — native implicit `role="button"` (do not add an
  explicit role); disabled uses `aria-disabled="true"` (not the native
  attribute); icon-only buttons require an `aria-label`.
- **Focus** — `:focus-visible` outline at `currentColor`, distinct from disabled
  styling.
- **Target size** — default `md` meets WCAG 2.5.8 (≥ 44×44 px); `xs`/`sm` may
  not — use only in dense UI.
- **Contrast** — color variants rely on the project's `--color-*` tokens; confirm
  WCAG 1.4.3 / 1.4.11 for surface↔label pairings.
- **WCAG 2.2 AA addressed** — 1.4.11, 2.1.1, 2.4.7, 2.5.8, 4.1.2.

## Examples

```html
<button type="button" class="btn" data-color="primary">Save changes</button>
<button type="button" class="btn" data-style="outline" data-btn="lg">Learn more</button>
<button type="button" class="btn is-disabled" data-color="primary" aria-disabled="true">Unavailable</button>
```

## Target: react

`generation: { export: Button, file: button.tsx, scss: button.scss, imports: "UI from '../ui'", dependencies: [] }`

The React adapter is the canonical TSX projection — byte-aligned with
`plugins/acss-kit/skills/component-button/reference.md` (its Props Interface +
TSX Template + the inlined `resolveDisabledState` / `useDisabledState` Key
Patterns). It realizes the `disabled-activation-guard` behavior as the
`useDisabledState` hook and surfaces variants via `data-btn` / `data-style` /
`data-color`, exactly as the Semantic Structure above. See that reference doc for
the full template; `/kit-add button --target=react` emits it verbatim.

> Other targets (`html`, `astro`, `angular`, `vue`, `svelte`, `web-component`)
> carry no adapter — a generator projects them from the neutral body above:
> render the Semantic Structure in the target's template syntax, type the
> abstract `props`, and realize the Behavior spec in the target's reactivity
> model using the `init(root)` reference.
