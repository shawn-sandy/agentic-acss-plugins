# Alert — Usage Guide

A severity-aware notification for status messages. Supports info/success/warning/error levels with matching icons, optional dismissal, optional auto-hide, and three visual variants. Uses `role="alert"` / `role="status"` live regions so screen readers announce it correctly.

## Add it to your project

1. **One-time setup** (run once per project): `/setup` — installs `sass`, writes `.acss-target.json`, and creates the `ui.tsx` foundation every component imports.
2. **Add this component:** `/kit-add Alert` — copies `alert.tsx` + `alert.scss` into your components directory (default `src/components/fpkit/`).
   - Or run `/kit-sync` once to install **all** components, the foundation, and a starter theme together.

The generated component is self-contained — no `@fpkit/acss` install required. Alert inlines its severity icon SVGs, so it has no Icon dependency.

## Import

```tsx
import Alert from './fpkit/alert/alert'
import './fpkit/alert/alert.scss'
```

Adjust the path to match the `componentsDir` in your `.acss-target.json`.

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `open` | `boolean` | — (required) | Whether the alert is visible. |
| `children` | `React.ReactNode` | — (required) | Alert content. |
| `severity` | `'default' \| 'info' \| 'success' \| 'warning' \| 'error'` | `default` | Determines color, icon, and live-region role. |
| `title` | `string` | — | Optional title. |
| `dismissible` | `boolean` | `false` | Renders a close button; enables Escape-to-dismiss. |
| `onDismiss` | `() => void` | — | Callback when dismissed. |
| `variant` | `'outlined' \| 'filled' \| 'soft'` | `outlined` | Visual variant. |
| `autoHideDuration` | `number` | — | ms before auto-dismiss; omit to never auto-dismiss. |
| `pauseOnHover` | `boolean` | `true` | Pause the auto-hide timer on hover/focus. |
| `hideIcon` | `boolean` | `false` | Hide the severity icon. |
| `titleLevel` | `2 \| 3 \| 4 \| 5 \| 6` | — | Render the title as `<h2>`–`<h6>`; omit for `<strong>`. |
| `actions` | `React.ReactNode` | — | Action buttons rendered after the message. |

Plus any native `<div>` attribute except `title` / `children`.

## Examples

```tsx
// Basic
<Alert open={true} severity="info">
  Your session will expire in 5 minutes.
</Alert>

// With title and dismiss
<Alert
  open={isOpen}
  severity="error"
  title="Payment failed"
  dismissible
  onDismiss={() => setIsOpen(false)}
>
  Please check your card details and try again.
</Alert>

// Auto-dismiss after 5s
<Alert
  open={showSuccess}
  severity="success"
  autoHideDuration={5000}
  onDismiss={() => setShowSuccess(false)}
>
  Your changes have been saved.
</Alert>

// With actions
<Alert
  open={true}
  severity="warning"
  title="Unsaved changes"
  actions={
    <>
      <button onClick={saveChanges}>Save</button>
      <button onClick={discard}>Discard</button>
    </>
  }
>
  You have unsaved changes.
</Alert>
```

## Theming

Override these CSS custom properties in your theme to restyle every alert. Each has a fallback, so overriding is optional.

| Variable | Purpose |
|----------|---------|
| `--alert-padding` / `--alert-gap` | Inner padding and icon/content spacing. |
| `--alert-radius` | Corner radius. |
| `--alert-info-bg` / `--alert-info-color` | Info severity background/text (border via `--alert-info-border`). |
| `--alert-success-bg` / `--alert-success-color` | Success severity background/text. |
| `--alert-warning-bg` / `--alert-warning-color` | Warning severity background/text. |
| `--alert-error-bg` / `--alert-error-color` | Error severity background/text. |
| `--alert-icon-size` | Severity icon size. |
| `--alert-transition` | Show/hide opacity transition. |

```css
:root {
  --alert-radius: 0.5rem;
  --alert-info-bg: #e0f2fe;
  --alert-info-color: #075985;
}
```

Generate a full matching theme with `/theme-create` (see [styles.md](../styles.md)).

## Accessibility

- `error` severity renders `role="alert"` + `aria-live="assertive"` (interrupts the screen reader); `info` / `success` / `warning` render `role="status"` + `aria-live="polite"` (announced when the current speech finishes).
- The severity word ("error:", "success:") is rendered in a visually-hidden span before the content, so screen readers get the severity plus the message. The icon carries `aria-hidden="true"`.
- Dismissible alerts render an explicit `<button aria-label="Dismiss alert">` and respond to Escape.
- `autoHideDuration` pairs with `pauseOnHover` (default on) so the timer pauses on hover/focus — satisfying WCAG 2.2.1 Timing Adjustable. For critical messages, prefer `dismissible` without auto-hide.
- Each severity's default color pair meets 4.5:1 contrast. Verify custom overrides stay above AA.

## Related

- [Component index](README.md)
- [Dialog](dialog.md) — for modal, blocking messages that require a decision
- Full maintainer reference: [`skills/component-alert/reference.md`](../../skills/component-alert/reference.md)
