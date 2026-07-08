# Icon Button — Usage Guide

An accessible icon-only (or icon + label) button built on top of [Button](button.md). A TypeScript XOR type requires exactly one of `aria-label` or `aria-labelledby` at compile time, so the icon always has a programmatic accessible name (WCAG 1.1.1 / 4.1.2).

## Add it to your project

1. **One-time setup** (run once per project): `/setup` — installs `sass`, writes `.acss-target.json`, and creates the `ui.tsx` foundation every component imports.
2. **Add this component:** `/kit-add IconButton` — copies `icon-button.tsx` + `icon-button.scss` into your components directory (default `src/components/fpkit/`). It depends on `Button`, so add that too (or run `/kit-sync`).
   - Or run `/kit-sync` once to install **all** components, the foundation, and a starter theme together.

The generated component is self-contained — no `@fpkit/acss` install required.

## Import

```tsx
import IconButton from './fpkit/icon-button/icon-button'
import './fpkit/button/button.scss' // base .btn styles + focus-visible ring
import './fpkit/icon-button/icon-button.scss'
```

Adjust the path to match the `componentsDir` in your `.acss-target.json`. IconButton renders `Button` from `../button/button`, so both the `.tsx` and `button.scss` must be present — the icon button inherits its variant styling, disabled appearance, and focus ring from `button.scss`.

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `icon` | `React.ReactNode` | — (required) | The icon element rendered inside the button. |
| `type` | `'button' \| 'submit' \| 'reset'` | `button` | Prevents implicit form submit. |
| `aria-label` | `string` | — | Accessible name. Required unless `aria-labelledby` is passed. |
| `aria-labelledby` | `string` | — | Accessible name by reference. Required unless `aria-label` is passed. |
| `label` | `string` | — | Optional text shown beside the icon at desktop widths; always in the a11y tree. |
| `variant` | `'text' \| 'pill' \| 'icon' \| 'outline'` | `icon` | Inherited from Button; `outline` restores padding for label layout. |

The XOR type means passing **both** `aria-label` and `aria-labelledby` — or **neither** — is a TypeScript compile-time error. Plus any other `ButtonProps` (`size`, `color`, `disabled`, `onClick`, etc.) except `children`.

## Examples

```tsx
// Icon-only — compile-time accessible-name requirement enforced
<IconButton type="button" aria-label="Close menu" icon={<CloseIcon />} />

// Icon + responsive label (label hidden below 48rem; always in a11y tree)
<IconButton
  type="button"
  aria-label="Settings"
  icon={<SettingsIcon />}
  label="Settings"
  variant="outline"   // restores padding for label layout
/>

// Labelled by external element
<>
  <span id="del-label">Delete item</span>
  <IconButton type="button" aria-labelledby="del-label" icon={<TrashIcon />} />
</>
```

## Theming

Override these CSS custom properties in your theme. Each has a fallback, so overriding is optional. IconButton also inherits color and focus tokens from [Button](button.md).

| Variable | Purpose |
|----------|---------|
| `--icon-btn-size` | Tap-target size (default `3rem` / 48 px). |
| `--icon-btn-padding` | Inner padding (default `0`). |
| `--icon-btn-radius` | Corner radius (default `50%` — circular). |
| `--icon-btn-gap` | Gap between icon and label. |
| `--icon-label-bp` | Breakpoint above which the label appears (default `48rem`). |
| `--icon-label-fs` | Label font size. |

```css
:root {
  --icon-btn-radius: 0.5rem;
  --icon-btn-size: 2.75rem;
}
```

Generate a full matching theme with `/theme-create` (see [styles.md](../styles.md)).

## Accessibility

- The XOR type makes the accessible name a build-time guarantee — you cannot ship an icon button without `aria-label` or `aria-labelledby`.
- Default `--icon-btn-size: 3rem` (48 px) exceeds WCAG 2.5.5 Target Size (AAA); keep it at or above 44 px if you shrink it.
- Inherits Button's keyboard behavior (Enter/Space activation), `:focus-visible` ring, and `aria-disabled` disabled pattern that keeps the button in the tab order.
- The optional `label` is visually hidden below the breakpoint with `clip` (not `display: none`), so screen readers announce it at every viewport.

## Related

- [Component index](README.md)
- [Button](button.md) — the base component IconButton is built on
- [Icon](icon.md) — supplies the glyph you pass to `icon`
- Full maintainer reference: [`skills/component-icon-button/reference.md`](../../skills/component-icon-button/reference.md)
