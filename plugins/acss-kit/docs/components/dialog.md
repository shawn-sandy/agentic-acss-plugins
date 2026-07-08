# Dialog — Usage Guide

A modal dialog built on the native HTML `<dialog>` element, so focus trapping, the backdrop scrim, and Escape-to-close come for free — no npm packages. It is a compound component (`Dialog`, `Dialog.Header`, `Dialog.Body`, `Dialog.Footer`) and you drive open/close through a ref.

## Add it to your project

1. **One-time setup** (run once per project): `/setup` — installs `sass`, writes `.acss-target.json`, and creates the `ui.tsx` foundation every component imports.
2. **Add this component:** `/kit-add Dialog` — copies `dialog.tsx` + `dialog.scss` into your components directory (default `src/components/fpkit/`).
   - Or run `/kit-sync` once to install **all** components, the foundation, and a starter theme together.

Dialog depends on `Button` (for the close button and footer actions) — `/kit-add Dialog` pulls in `button.tsx` + `button.scss` too. No `@fpkit/acss` install required.

## Import

```tsx
import { useRef } from 'react'
import Dialog from './fpkit/dialog/dialog'
import Button from './fpkit/button/button'
import './fpkit/dialog/dialog.scss'
import './fpkit/button/button.scss'
```

`Dialog.Header`, `Dialog.Body`, and `Dialog.Footer` are attached to the default export. Adjust the paths to match the `componentsDir` in your `.acss-target.json`.

## Props

`Dialog` (root):

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `dialogRef` | `React.RefObject<HTMLDialogElement>` | — (required) | Ref used to call `showModal()` / `close()`. |
| `openOnMount` | `boolean` | `false` | Whether to open on mount. |
| `onClose` | `() => void` | — | Callback when the dialog closes. |
| `title` | `string` | — | Renders a header title, wired to `aria-labelledby`. |
| `description` | `string` | — | Renders a description paragraph under the title. |
| `showCloseButton` | `boolean` | `true` | Show the header close button. |
| `children` | `React.ReactNode` | — | Dialog body content. |
| `footer` | `React.ReactNode` | — | Footer action buttons. |
| `classes` | `string` | — | CSS class name. |
| `styles` | `React.CSSProperties` | — | Inline styles. |

Plus any native `<dialog>` attribute except `open`. Sub-components — `Dialog.Header` (`children`, `onClose`, `showCloseButton`, `classes`), `Dialog.Body` (`children`, `classes`), `Dialog.Footer` (`children`, `classes`).

## Examples

```tsx
function App() {
  const dialogRef = useRef<HTMLDialogElement>(null)

  return (
    <>
      <Button type="button" onClick={() => dialogRef.current?.showModal()}>
        Open Dialog
      </Button>

      <Dialog
        dialogRef={dialogRef}
        title="Confirm Action"
        description="This action cannot be undone."
        onClose={() => console.log('closed')}
        footer={
          <>
            <Button type="button" variant="outline" onClick={() => dialogRef.current?.close()}>
              Cancel
            </Button>
            <Button type="button" color="primary" onClick={() => {}}>
              Confirm
            </Button>
          </>
        }
      >
        <p>Are you sure you want to proceed?</p>
      </Dialog>
    </>
  )
}
```

Open with `dialogRef.current?.showModal()` and close with `dialogRef.current?.close()`. Backdrop clicks and the Escape key also close the dialog.

## Theming

Override these CSS custom properties in your theme to restyle every dialog. Each has a fallback, so overriding is optional.

| Variable | Purpose |
|----------|---------|
| `--dialog-bg` / `--dialog-color` | Dialog background/text. |
| `--dialog-radius` | Corner radius. |
| `--dialog-width` / `--dialog-max-width` / `--dialog-max-height` | Sizing constraints. |
| `--dialog-shadow` | Drop shadow. |
| `--dialog-header-padding` / `--dialog-body-padding` | Header and body padding. |
| `--dialog-footer-bg` / `--dialog-footer-justify` | Footer background and action alignment. |
| `--dialog-backdrop-bg` | `::backdrop` scrim color. |

```css
:root {
  --dialog-width: 28rem;
  --dialog-radius: 0.75rem;
  --dialog-backdrop-bg: rgba(0, 0, 0, 0.6);
}
```

Generate a full matching theme with `/theme-create` (see [styles.md](../styles.md)).

## Accessibility

- Opening with `showModal()` traps focus inside the dialog, and closing returns focus to the trigger — both native browser behaviors. Never use modeless `show()`; it does not enforce the trap.
- `Escape` fires the native `cancel` event and closes the dialog. No keybinding code needed.
- The native `<dialog>` supplies `role="dialog"` and `aria-modal="true"` automatically — don't add them. `aria-labelledby` references the generated title id; set `description` to add `aria-describedby` context.
- The close button carries `aria-label="Close dialog"` since the `×` glyph is not an accessible name.
- The browser focuses the first focusable element on open — often the close button. To land focus on a safer footer action, pass `autoFocus` to that button.
- Dialog title renders as `<h2>`; keep the surrounding heading outline in mind if the page already uses `<h2>` nearby.

## Related

- [Component index](README.md)
- [Button](button.md) — used for the close button and footer actions
- [Alert](alert.md) — for inline, non-blocking status messages
- Full maintainer reference: [`skills/component-dialog/reference.md`](../../skills/component-dialog/reference.md)
