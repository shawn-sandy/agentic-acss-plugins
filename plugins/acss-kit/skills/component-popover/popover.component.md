---
spec: component.md
version: alpha
name: popover
element: div
role: dialog
tokens:
  background: "{colors.surface}"
  textColor: "{colors.on-surface}"
  border: "{colors.outline-variant}"
  rounded: "{rounded.md}"
  paddingBlock: "{spacing.sm}"
  paddingInline: "{spacing.md}"
props:
  id:
    type: string
    maps-to: "id + popovertarget"
  mode:
    values: [auto, manual]
    default: auto
    maps-to: "popover attribute"
  placement:
    values: [top, bottom, left, right]
    default: bottom
    maps-to: "data-placement"
  isOpen:
    type: boolean
    a11y: "controlled open state; drives showPopover()/hidePopover()"
  showCloseButton:
    type: boolean
    a11y: "default true for manual mode, false for auto"
  showArrow:
    type: boolean
    default: true
    maps-to: ".popover-arrow"
  triggerLabel:
    type: string
    a11y: "aria-label for the default trigger button"
  closeButtonLabel:
    type: string
    a11y: "aria-label for the close button"
slots: [children, trigger]
variants:
  auto:   { maps-to: "popover=auto" }
  manual: { maps-to: "popover=manual" }
behavior: native-popover-toggle
a11y: [1.4.3, 1.4.11, 2.1.1, 2.4.3, 2.4.7, 4.1.2]
targets: [react, html, astro, angular, vue, svelte, web-component]
---

# Component: Popover

> **Neutral COMPONENT.md** for the acss-kit `popover`. The framework-agnostic
> source of truth lives in the `##` body below; the canonical React projection is
> the `## Target: react` adapter at the end (byte-aligned with the legacy
> `reference.md`). `/kit-add popover` reads this file: `## Styles` → `popover.scss`,
> `## Target: react` → `popover.tsx`.
>
> **Verified against fpkit source:** [`@fpkit/acss@6.5.0`](https://github.com/shawn-sandy/acss/tree/9063512fa822963d8151c972bed9f5b0e531df0f) (closest tagged ref to
> npm `6.6.0`). Uses the native HTML Popover API (`popover` attribute +
> `popovertarget` + `showPopover()` / `hidePopover()`). Browser support: Chrome
> 125+, Edge 125+, Safari 17.4+, Firefox 125+. The native API provides automatic
> top-layer rendering, light dismiss, and keyboard handling — no `floating-ui`,
> `@radix-ui/popover`, or `react-popper` dependency.

## Overview

A popover anchored to a trigger button, built on the native HTML Popover API.
Supports auto-mode (light dismiss on outside click or Escape) and manual mode
(explicit close button required). Optional positioning arrow, controlled or
uncontrolled open state, and custom trigger element. Generates a unique ID so
multiple popovers on the same page don't collide.

## Semantic Structure

```html
<!-- variant: auto (light dismiss on outside click / Escape) -->
<button type="button" popovertarget="info" popovertargetaction="toggle"
        aria-label="More info" class="popover-trigger">
  <!-- slot: trigger (default trigger label) -->
</button>
<div id="info" popover="auto" class="popover" data-placement="bottom">
  <div class="popover-arrow" data-placement="bottom"></div>
  <div class="popover-content">
    <!-- slot: children -->
  </div>
</div>

<!-- variant: manual (explicit close button required) -->
<button type="button" popovertarget="confirm" popovertargetaction="toggle"
        aria-label="Confirm" class="popover-trigger">
  <!-- slot: trigger -->
</button>
<div id="confirm" popover="manual" class="popover" data-placement="bottom">
  <div class="popover-arrow" data-placement="bottom"></div>
  <div class="popover-content">
    <!-- slot: children -->
    <button type="button" popovertarget="confirm" popovertargetaction="hide"
            aria-label="Close" class="popover-close">×</button>
  </div>
</div>

<!-- variant: custom trigger (cloned with popovertarget attributes) -->
<button type="button" popovertarget="user-menu" popovertargetaction="toggle"
        aria-label="User menu">@alice</button>
<div id="user-menu" popover="auto" class="popover" data-placement="bottom">
  <div class="popover-content">
    <!-- slot: children -->
  </div>
</div>
```

The host element is a `<div popover>` rendered in the browser's top layer. The
trigger is a separate `<button>` linked via `popovertarget` (the popover's `id`)
plus `popovertargetaction="toggle"`. The `popover` attribute value (`auto` or
`manual`) selects the dismiss behavior. Placement surfaces as `data-placement`;
the optional arrow is a `.popover-arrow` child.

## Props

| Prop | Values | Required | Surfaces as |
|---|---|---|---|
| `id` | string | no | `id` attribute + `popovertarget` linking |
| `children` | content | yes | `.popover-content` slot |
| `trigger` | element | no | custom trigger (cloned with `popovertarget`) |
| `triggerLabel` | string | no | `aria-label` on the default trigger |
| `mode` | `auto` \| `manual` | no | `popover` attribute |
| `placement` | `top` \| `bottom` \| `left` \| `right` | no | `data-placement` |
| `isOpen` | boolean | no | controlled open state |
| `onToggle` | callback | no | native `toggle` event listener |
| `showCloseButton` | boolean | no | renders `.popover-close` |
| `closeButtonLabel` | string | no | `aria-label` on the close button |
| `showArrow` | boolean | no | renders `.popover-arrow` |
| `className` | string | no | extra class on the popover element |
| `styles` | object | no | inline CSS variables / styles |

## Tokens & CSS Variables

Themeable properties reference DESIGN.md primitives via `var(--token, <fallback>)`;
each keeps a hardcoded fallback so the component renders with no design system.

```scss
--popover-bg: var(--color-surface, #fff);
--popover-color: var(--color-text, inherit);
--popover-border: 1px solid var(--color-border, #e0e0e0);
--popover-radius: var(--radius-md, 0.375rem);
--popover-padding: 0.75rem 1rem;
--popover-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
--popover-max-width: 20rem;
--popover-z: 10;
--popover-arrow-size: 0.5rem;
```

## Styles

```scss
// popover.scss
.popover {
  // Native popover element resets — re-establish basic block
  margin: 0;
  border: var(--popover-border, 1px solid #e0e0e0);
  border-radius: var(--popover-radius, var(--radius-md, 0.375rem));
  background: var(--popover-bg, #fff);
  color: var(--popover-color, inherit);
  box-shadow: var(--popover-shadow, 0 4px 12px rgba(0, 0, 0, 0.15));
  max-width: var(--popover-max-width, 20rem);
  z-index: var(--popover-z, 10);
  inset: unset;

  &:popover-open {
    display: block;
  }
}

.popover-content {
  padding: var(--popover-padding, 0.75rem 1rem);
  position: relative;
}

.popover-arrow {
  position: absolute;
  width: var(--popover-arrow-size, 0.5rem);
  height: var(--popover-arrow-size, 0.5rem);
  background: inherit;
  border: inherit;
  transform: rotate(45deg);

  &[data-placement="bottom"] { top: calc(var(--popover-arrow-size, 0.5rem) * -0.5); left: 50%; border-bottom: none; border-right: none; }
  &[data-placement="top"]    { bottom: calc(var(--popover-arrow-size, 0.5rem) * -0.5); left: 50%; border-top: none; border-left: none; }
  &[data-placement="left"]   { right: calc(var(--popover-arrow-size, 0.5rem) * -0.5); top: 50%; border-left: none; border-bottom: none; }
  &[data-placement="right"]  { left: calc(var(--popover-arrow-size, 0.5rem) * -0.5); top: 50%; border-right: none; border-top: none; }
}

.popover-close {
  position: absolute;
  top: var(--space-xs, 0.25rem);
  right: var(--space-sm, 0.5rem);
  background: transparent;
  border: none;
  font-size: 1.25rem;
  line-height: 1;
  cursor: pointer;
  padding: 0.125rem 0.25rem;
  color: currentColor;

  &:focus-visible {
    outline: 2px solid currentColor;
    outline-offset: 2px;
  }
}

.popover-trigger {
  // The default trigger when no `trigger` prop is passed —
  // intentionally minimal so it inherits the parent's button styling
  cursor: pointer;
}
```

## Behavior

**`native-popover-toggle`** — opening and closing is handled entirely by the
native HTML Popover API; no JavaScript click handler is required. The trigger
`<button>` carries `popovertarget="<popover-id>"` and
`popovertargetaction="toggle"`, so Enter/Space/click toggles the linked
`<div popover>`. In `auto` mode the browser adds light-dismiss (outside click,
Escape) and returns focus to the trigger on close; `manual` mode requires an
explicit close button (`popovertargetaction="hide"`). For controlled usage,
external state drives `showPopover()` / `hidePopover()`, and a listener on the
native `toggle` event reports the new open/closed state back out.

Neutral reference implementation (static HTML / vanilla JS):

```js
// Idempotent: calling init() twice on the same root does not double-bind.
const SENTINEL = 'data-acss-popover-init';

export function init(root = document, opts = {}) {
  const popovers = root.querySelectorAll('.popover[popover]');
  for (const el of popovers) {
    if (el.getAttribute(SENTINEL) === 'true') continue;
    el.setAttribute(SENTINEL, 'true');

    // Controlled open state — drive showPopover() / hidePopover().
    if (typeof opts.isOpen === 'boolean') {
      const isOpen = el.matches(':popover-open');
      if (opts.isOpen && !isOpen) el.showPopover();
      else if (!opts.isOpen && isOpen) el.hidePopover();
    }

    // Report toggle state back out via the native ToggleEvent.
    el.addEventListener('toggle', (e) => {
      opts.onToggle?.(e.newState === 'open');
    });
  }
}
```

Triggering (toggle / hide) is wholly declarative via `popovertarget` /
`popovertargetaction` — no listener is needed to open or close. A generator
realizes the controlled-state and toggle-reporting spec idiomatically per target
(React effect, Vue watcher, Svelte action, Angular directive); the `react`
adapter below ships the canonical `useEffect` wiring.

## Accessibility

WCAG 2.2 AA compliance for the generated `Popover` component.

**Native Popover API**
- `popover="auto"` (default) gives the popover light-dismiss behavior: clicking outside closes it; pressing `Escape` closes it. The browser handles both — no JavaScript listeners needed.
- `popover="manual"` requires an explicit close action. Use for popovers that contain forms or interactive content where accidental dismissal would lose user input.
- Both modes render the popover in the browser's top layer (above all stacking contexts) so `z-index` from sibling elements doesn't matter.

**Keyboard interaction**
- Trigger button activates the popover via `popovertargetaction="toggle"` — Enter or Space on the trigger toggles the popover. No JavaScript click handler needed; this is a native browser behaviour.
- In `auto` mode, `Escape` closes the popover (browser default).
- Focus moves into the popover when opened only if the popover contains a focusable element and the user explicitly tabs into it. Unlike a `<dialog>` modal, focus is *not* trapped — by design, the user can keyboard-navigate to other parts of the page while the popover is open.

**ARIA & screen reader**
- Trigger button has an `aria-label` (default: `"Open"` via `triggerLabel`). When passing a custom `trigger`, ensure the trigger element has an accessible name.
- Close button has an explicit `aria-label="Close"` — the visual `×` glyph is not an accessible name on its own.
- The popover container itself does not get `role="dialog"` or `role="tooltip"` automatically. If the popover is used as a tooltip, add `role="tooltip"` and link the trigger via `aria-describedby`. If used as a menu, consider whether `role="menu"` and the menu-button pattern are more appropriate.

**Focus management on close**
- On close (light dismiss or close button), focus returns to the trigger button — native popover behaviour. This avoids losing the user's place after closing.

**Color contrast**
- Popover text color (`--popover-color`) on background (`--popover-bg`) must meet 4.5:1 (WCAG 1.4.3 AA).
- Popover border (`--popover-border`) provides visual separation from the page; in flat designs without shadow, the border must meet 3:1 against the page background (WCAG 1.4.11 Non-text Contrast).

**Browser support fallback**
- Browsers without Popover API support: the `popover` attribute is ignored, the popover renders as a normal `<div>` inline. Plan for graceful degradation by ensuring the surrounding layout doesn't break when the popover is always-visible. Or feature-detect `'showPopover' in HTMLElement.prototype` and provide an alternative UI.

**WCAG 2.2 AA criteria addressed**
- 1.4.3 Contrast Minimum (text on popover background)
- 1.4.11 Non-text Contrast (popover border)
- 2.1.1 Keyboard (native trigger toggle + Escape dismiss)
- 2.4.3 Focus Order (focus returns to trigger on close)
- 2.4.7 Focus Visible (close button focus ring)
- 4.1.2 Name, Role, Value (trigger and close button have accessible names; user must add `role` if popover serves a specific semantic role)

## Examples

```html
<!-- Default — auto mode (light dismiss) -->
<button type="button" popovertarget="info" popovertargetaction="toggle"
        aria-label="More info" class="popover-trigger">More info</button>
<div id="info" popover="auto" class="popover" data-placement="bottom">
  <div class="popover-content">
    <p>Additional context shown in a popover.</p>
  </div>
</div>

<!-- Manual mode — explicit close required -->
<button type="button" popovertarget="confirm" popovertargetaction="toggle"
        aria-label="Confirm" class="popover-trigger">Confirm</button>
<div id="confirm" popover="manual" class="popover" data-placement="bottom">
  <div class="popover-content">
    <h3>Are you sure?</h3>
    <p>This action cannot be undone.</p>
    <button type="button" popovertarget="confirm" popovertargetaction="hide"
            aria-label="Cancel confirmation" class="popover-close">×</button>
  </div>
</div>
```

## Target: react

`generation: { export: Popover, file: popover.tsx, scss: popover.scss, imports: "React with useEffect, useId, useRef", dependencies: [] }`

The React adapter is the canonical TSX projection — Popover uses the native HTML
Popover API directly with no upstream dependencies (the trigger is a raw
`<button>`, not the kit-builder `Button`, so Popover doesn't depend on
`button.tsx`). `/kit-add popover --target=react` emits the assembled file: the
Props Interface and the TSX Template below.

## Props Interface

```tsx
export interface PopoverProps {
  /** Unique ID — defaults to a generated id; required for popovertarget linking */
  id?: string
  /** Content rendered inside the popover */
  children: React.ReactNode
  /** Custom trigger element (default: `<button>` with triggerLabel) */
  trigger?: React.ReactNode
  /** aria-label for the default trigger button */
  triggerLabel?: string
  /** "auto" (light dismiss) or "manual" (explicit close required) */
  mode?: 'auto' | 'manual'
  /** Visual placement hint relative to the trigger */
  placement?: 'top' | 'bottom' | 'left' | 'right'
  /** Controlled open state */
  isOpen?: boolean
  /** Toggle callback */
  onToggle?: (open: boolean) => void
  /** Show close button (default: true for manual mode, false for auto) */
  showCloseButton?: boolean
  /** aria-label for the close button */
  closeButtonLabel?: string
  /** Show positioning arrow (default: true) */
  showArrow?: boolean
  /** Custom CSS class on the popover element */
  className?: string
  /** Inline CSS variables / styles */
  styles?: React.CSSProperties
}
```

## TSX Template

```tsx
import React, { useEffect, useId, useRef } from 'react'

export interface PopoverProps {
  id?: string
  children: React.ReactNode
  trigger?: React.ReactNode
  triggerLabel?: string
  mode?: 'auto' | 'manual'
  placement?: 'top' | 'bottom' | 'left' | 'right'
  isOpen?: boolean
  onToggle?: (open: boolean) => void
  showCloseButton?: boolean
  closeButtonLabel?: string
  showArrow?: boolean
  className?: string
  styles?: React.CSSProperties
}

export const Popover: React.FC<PopoverProps> = ({
  id,
  children,
  trigger,
  triggerLabel = 'Open',
  mode = 'auto',
  placement = 'bottom',
  isOpen,
  onToggle,
  showCloseButton,
  showArrow = true,
  closeButtonLabel = 'Close',
  className = '',
  styles,
}) => {
  const generatedId = useId()
  const popoverId = id || generatedId
  const popoverRef = useRef<HTMLDivElement>(null)

  const shouldShowCloseButton =
    showCloseButton !== undefined ? showCloseButton : mode === 'manual'

  // Controlled open state — drive showPopover() / hidePopover()
  useEffect(() => {
    const popover = popoverRef.current
    if (!popover || isOpen === undefined) return

    try {
      const isCurrentlyOpen =
        popover.matches(':popover-open') || popover.hasAttribute('data-popover-open')
      if (isOpen && !isCurrentlyOpen) popover.showPopover()
      else if (!isOpen && isCurrentlyOpen) popover.hidePopover()
    } catch {
      const isCurrentlyOpen = popover.hasAttribute('data-popover-open')
      if (isOpen && !isCurrentlyOpen) popover.showPopover()
      else if (!isOpen && isCurrentlyOpen) popover.hidePopover()
    }
  }, [isOpen])

  // Toggle callback — listen to the native ToggleEvent
  useEffect(() => {
    const popover = popoverRef.current
    if (!popover || !onToggle) return

    const handleToggle = (event: Event) => {
      const toggleEvent = event as ToggleEvent
      onToggle(toggleEvent.newState === 'open')
    }
    popover.addEventListener('toggle', handleToggle)
    return () => popover.removeEventListener('toggle', handleToggle)
  }, [onToggle])

  const renderTrigger = () => {
    if (trigger) {
      return React.cloneElement(trigger as React.ReactElement, {
        popovertarget: popoverId,
        popovertargetaction: 'toggle',
      })
    }
    return (
      <button
        type="button"
        popovertarget={popoverId}
        popovertargetaction="toggle"
        aria-label={triggerLabel}
        className="popover-trigger"
      >
        {triggerLabel}
      </button>
    )
  }

  return (
    <>
      {renderTrigger()}
      <div
        ref={popoverRef}
        id={popoverId}
        popover={mode}
        className={`popover ${className}`.trim()}
        data-placement={placement}
        style={styles}
      >
        {showArrow && <div className="popover-arrow" data-placement={placement} />}
        <div className="popover-content">
          {children}
          {shouldShowCloseButton && (
            <button
              type="button"
              popovertarget={popoverId}
              popovertargetaction="hide"
              aria-label={closeButtonLabel}
              className="popover-close"
            >
              ×
            </button>
          )}
        </div>
      </div>
    </>
  )
}

Popover.displayName = 'Popover'
export default Popover
```
