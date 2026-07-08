# Popover — Usage Guide

A popover anchored to a trigger button, built on the native HTML Popover API (`popover` attribute + `popovertarget`). It supports auto mode (light dismiss on outside click or Escape) and manual mode (explicit close button), an optional positioning arrow, and controlled or uncontrolled open state — no `floating-ui` or `@radix-ui` dependency. Browser support: Chrome/Edge 125+, Safari 17.4+, Firefox 125+.

## Add it to your project

1. **One-time setup** (run once per project): `/setup` — installs `sass`, writes `.acss-target.json`, and creates the `ui.tsx` foundation every component imports.
2. **Add this component:** `/kit-add Popover` — copies `popover.tsx` + `popover.scss` into your components directory (default `src/components/fpkit/`).
   - Or run `/kit-sync` once to install **all** components, the foundation, and a starter theme together.

The generated component is self-contained — no `@fpkit/acss` install required.

## Import

The trigger, popover panel, arrow, and close button are all rendered by the single `Popover` component.

```tsx
import Popover from './fpkit/popover/popover'
import './fpkit/popover/popover.scss'
```

Adjust the path to match the `componentsDir` in your `.acss-target.json`.

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `children` | `React.ReactNode` | — (required) | Content rendered inside the popover. |
| `id` | `string` | generated | Unique id; required for `popovertarget` linking (auto-generated via `useId`). |
| `trigger` | `React.ReactNode` | — | Custom trigger element; cloned with the required `popovertarget` attributes. Defaults to a `<button>`. |
| `triggerLabel` | `string` | `'Open'` | `aria-label` and text for the default trigger button. |
| `mode` | `'auto' \| 'manual'` | `auto` | `auto` = light dismiss; `manual` = explicit close required. |
| `placement` | `'top' \| 'bottom' \| 'left' \| 'right'` | `bottom` | Visual placement hint relative to the trigger. |
| `isOpen` | `boolean` | — | Controlled open state. |
| `onToggle` | `(open: boolean) => void` | — | Toggle callback (fires on the native ToggleEvent). |
| `showCloseButton` | `boolean` | `true` for `manual`, `false` for `auto` | Show the close button. |
| `closeButtonLabel` | `string` | `'Close'` | `aria-label` for the close button. |
| `showArrow` | `boolean` | `true` | Show the positioning arrow. |
| `className` | `string` | `''` | Custom CSS class on the popover element. |
| `styles` | `React.CSSProperties` | — | Inline CSS variables / styles. |

## Examples

```tsx
// Default — auto mode (light dismiss)
<Popover id="info" triggerLabel="More info">
  <p>Additional context shown in a popover.</p>
</Popover>

// Manual mode — explicit close required
<Popover
  id="confirm"
  mode="manual"
  triggerLabel="Confirm"
  closeButtonLabel="Cancel confirmation"
>
  <h3>Are you sure?</h3>
  <p>This action cannot be undone.</p>
  <button type="button" onClick={handleConfirm}>Yes, proceed</button>
</Popover>

// Custom trigger
<Popover
  id="user-menu"
  trigger={<button type="button" aria-label="User menu">@alice</button>}
  placement="bottom"
>
  <ul>
    <li><a href="/profile">Profile</a></li>
    <li><a href="/logout">Log out</a></li>
  </ul>
</Popover>

// Controlled
const [open, setOpen] = useState(false)
<Popover
  id="controlled"
  isOpen={open}
  onToggle={setOpen}
  triggerLabel="Toggle externally"
>
  <p>State driven from parent.</p>
</Popover>
```

## Theming

Override these CSS custom properties in your theme to restyle every popover. Each has a fallback, so overriding is optional.

| Variable | Purpose |
|----------|---------|
| `--popover-bg` | Panel background. |
| `--popover-color` | Panel text color. |
| `--popover-border` | Panel border. |
| `--popover-radius` | Corner radius. |
| `--popover-padding` | Content padding. |
| `--popover-shadow` | Drop shadow. |
| `--popover-max-width` | Maximum panel width. |
| `--popover-arrow-size` | Size of the positioning arrow. |

```css
:root {
  --popover-radius: 0.5rem;
  --popover-max-width: 24rem;
}
```

Generate a full matching theme with `/theme-create` (see [styles.md](../styles.md)).

## Accessibility

- `popover="auto"` gives native light-dismiss: outside click or Escape closes it, handled by the browser with no JS listeners. Use `popover="manual"` for content (like forms) where accidental dismissal would lose input.
- The trigger toggles via `popovertargetaction="toggle"` — Enter or Space works natively. Focus is not trapped (unlike a modal dialog) by design.
- The default trigger has an `aria-label` (via `triggerLabel`); pass a custom `trigger` only if it has its own accessible name. The close button has an explicit `aria-label` since the `×` glyph is not a name.
- The container gets no `role="dialog"`/`role="tooltip"` automatically — add `role="tooltip"` + `aria-describedby`, or a menu pattern, if the popover serves that role.
- On close, focus returns to the trigger (native behavior). Popover text/background must meet 4.5:1 (WCAG 1.4.3); a border-only design must meet 3:1 (WCAG 1.4.11).
- In browsers without Popover API support the panel renders inline as a normal `<div>` — plan for graceful degradation or feature-detect `'showPopover' in HTMLElement.prototype`.

## Related

- [Component index](README.md)
- [Button](button.md) — pass a kit Button as the `trigger`
- [Dialog](dialog.md) — for modal content that should trap focus
- Full maintainer reference: [`skills/component-popover/reference.md`](../../skills/component-popover/reference.md)
