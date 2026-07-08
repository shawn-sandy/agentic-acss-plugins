# Button — Usage Guide

The primary interactive element. Size, style, and color variants are applied via HTML `data-*` attributes. Uses `aria-disabled` instead of the native `disabled` attribute so a disabled button stays in the tab order and reachable by keyboard (WCAG 2.1.1).

## Add it to your project

1. **One-time setup** (run once per project): `/setup` — installs `sass`, writes `.acss-target.json`, and creates the `ui.tsx` foundation every component imports.
2. **Add this component:** `/kit-add Button` — copies `button.tsx` + `button.scss` into your components directory (default `src/components/fpkit/`).
   - Or run `/kit-sync` once to install **all** components, the foundation, and a starter theme together.

The generated component is self-contained — no `@fpkit/acss` install required.

## Import

```tsx
import Button from './fpkit/button/button'
import './fpkit/button/button.scss'
```

Adjust the path to match the `componentsDir` in your `.acss-target.json`.

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `type` | `'button' \| 'submit' \| 'reset'` | — (required) | Prevents implicit form submit. |
| `children` | `React.ReactNode` | — | Button content. |
| `disabled` | `boolean` | `false` | Accessible disabled — keeps the element focusable (WCAG 2.1.1). |
| `size` | `'xs' \| 'sm' \| 'md' \| 'lg' \| 'xl' \| '2xl'` | `md` | Maps to `data-btn`. |
| `variant` | `'text' \| 'pill' \| 'icon' \| 'outline'` | — | Maps to `data-style`. |
| `color` | `'primary' \| 'secondary' \| 'danger' \| 'success' \| 'warning'` | — | Maps to `data-color`. |
| `block` | `boolean` | `false` | Stretches to 100% width. |
| `classes` | `string` | — | CSS class(es); takes precedence over `className`. |

Plus any native `<button>` attribute (`onClick`, `aria-*`, etc.).

## Examples

```tsx
// Basic
<Button type="button" onClick={() => {}}>Click me</Button>

// Color + size
<Button type="button" color="primary" size="lg">Save</Button>
<Button type="button" color="danger">Delete</Button>

// Full-width primary
<Button type="button" color="primary" block>Continue</Button>

// Accessible disabled (still focusable)
<Button type="button" color="primary" disabled>Cannot click</Button>

// Style variants
<Button type="button" variant="outline">Outlined</Button>
<Button type="button" variant="pill" color="primary">Pill</Button>
```

## Theming

Override these CSS custom properties in your theme to restyle every button. Each has a fallback, so overriding is optional.

| Variable | Purpose |
|----------|---------|
| `--btn-size-md` | Default font size (other sizes: `--btn-size-xs`…`--btn-size-xl`). |
| `--btn-radius` | Corner radius. |
| `--btn-padding-block` / `--btn-padding-inline` | Padding. |
| `--btn-primary-bg` / `--btn-primary-color` | Primary color-variant background/text. |
| `--btn-danger-bg` | Danger-variant background. |
| `--btn-focus-outline` / `--btn-focus-outline-offset` | Focus ring. |
| `--btn-disabled-opacity` | Disabled appearance. |

```css
:root {
  --btn-radius: 0.5rem;
  --btn-primary-bg: #6d28d9;
}
```

Generate a full matching theme with `/theme-create` (see [styles.md](../styles.md)).

## Accessibility

- Disabled state uses `aria-disabled="true"` — the button stays keyboard-focusable so users understand it exists (native `disabled` removes it from the tab order).
- Ships a visible focus ring (`--btn-focus-outline`).
- Always pass an explicit `type` to avoid accidental form submits.

## Related

- [Component index](README.md)
- [Icon Button](icon-button.md) — icon-only variant
- Full maintainer reference: [`skills/component-button/reference.md`](../../skills/component-button/reference.md)
