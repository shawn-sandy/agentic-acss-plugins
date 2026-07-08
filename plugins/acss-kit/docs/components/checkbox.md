# Checkbox — Usage Guide

A checkbox with simplified ergonomics: a boolean `onChange` (not the native `ChangeEvent`), a bundled visible label, size presets, and full validation passthrough. It wraps the kit's `Input`, so it inherits all validation, disabled, and ARIA logic.

## Add it to your project

1. **One-time setup** (run once per project): `/setup` — installs `sass`, writes `.acss-target.json`, and creates the `ui.tsx` foundation every component imports.
2. **Add this component:** `/kit-add Checkbox` — copies `checkbox.tsx` + `checkbox.scss` into your components directory (default `src/components/fpkit/`).
   - Or run `/kit-sync` once to install **all** components, the foundation, and a starter theme together.

Checkbox depends on `Input` — `/kit-add Checkbox` pulls in `input.tsx` + `input.scss` too. No `@fpkit/acss` install required.

## Import

```tsx
import Checkbox from './fpkit/checkbox/checkbox'
import './fpkit/input/input.scss'
import './fpkit/checkbox/checkbox.scss'
```

Import `input.scss` as well as `checkbox.scss` — the checkbox reuses Input's validation styling. Adjust the paths to match the `componentsDir` in your `.acss-target.json`.

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `id` | `string` | — (required) | Required for label association. |
| `label` | `React.ReactNode` | — (required) | Visible label text. |
| `size` | `'xs' \| 'sm' \| 'md' \| 'lg'` | `md` | Size preset (sets `data-checkbox-size`). |
| `checked` | `boolean` | — | Controlled checked state. |
| `defaultChecked` | `boolean` | — | Uncontrolled initial state. |
| `value` | `string` | `'on'` | Form-submission value when checked. |
| `onChange` | `(checked: boolean) => void` | — | Receives `true`/`false`, not a `ChangeEvent`. |
| `required` | `boolean` | `false` | Sets `aria-required` and renders a `*` after the label. |
| `disabled` | `boolean` | `false` | Accessible disabled (via `aria-disabled`, inherited from Input). |
| `validationState` | `'none' \| 'invalid'` (from Input) | — | Cascades `aria-invalid`. |
| `errorMessage` / `hintText` | `string` | — | Passed through to Input for `aria-describedby`. |
| `classes` | `string` | — | Wrapper `<div>` CSS classes. |
| `inputClasses` | `string` | `'checkbox-input'` | Input element CSS classes. |
| `styles` | `React.CSSProperties` | — | CSS custom properties for theming / custom sizing. |

Plus the remaining `Input` props except `type`, `value`, `onChange`, `defaultValue`, and `placeholder`.

## Examples

```tsx
// Basic
<Checkbox id="terms" label="I accept the terms and conditions" />

// Controlled
const [agreed, setAgreed] = useState(false)
<Checkbox
  id="terms"
  label="I accept the terms"
  checked={agreed}
  onChange={setAgreed}
  required
/>

// Validation + error
<Checkbox
  id="confirm"
  label="I understand this action is permanent"
  checked={confirmed}
  onChange={setConfirmed}
  validationState={!confirmed ? 'invalid' : 'none'}
  errorMessage={!confirmed ? 'Confirmation required' : undefined}
  required
/>

// Size variants
<Checkbox id="opt-sm" label="Small" size="sm" />
<Checkbox id="opt-lg" label="Large" size="lg" />

// Custom sizing via CSS variables
<Checkbox
  id="opt-custom"
  label="Custom 2rem"
  styles={{ '--checkbox-size': '2rem', '--checkbox-gap': '1rem' } as React.CSSProperties}
/>
```

## Theming

Override these CSS custom properties in your theme to restyle every checkbox. Each has a fallback, so overriding is optional.

| Variable | Purpose |
|----------|---------|
| `--checkbox-size` | Box size (or set per-size `--checkbox-size-xs`…`--checkbox-size-lg`). |
| `--checkbox-radius` | Corner radius. |
| `--checkbox-border-color` / `--checkbox-bg` | Unchecked border and background. |
| `--checkbox-checked-bg` / `--checkbox-check-color` | Checked fill and checkmark color. |
| `--checkbox-gap` | Space between box and label. |
| `--checkbox-label-fs` / `--checkbox-label-color` | Label size and color. |
| `--checkbox-focus-ring` | Focus ring box-shadow. |
| `--checkbox-required-color` | Color of the required `*`. |

```css
:root {
  --checkbox-checked-bg: #6d28d9;
  --checkbox-radius: 0.375rem;
}
```

Generate a full matching theme with `/theme-create` (see [styles.md](../styles.md)).

## Accessibility

- `id` and `label` are both required. The component renders `<label htmlFor={id}>`, so clicking the label toggles the box and screen readers announce the label on focus.
- Renders a native `<input type="checkbox">` — Space toggles, Tab navigates. The visual appearance is custom (`appearance: none` + `::after` checkmark) but the semantics stay native.
- `disabled` uses `aria-disabled` (not native `disabled`), inherited from Input, so the control stays discoverable in the tab order (WCAG 2.1.1).
- `required` renders `aria-required="true"` plus a visible `*` labeled `aria-label="required"`; `validationState="invalid"` cascades `aria-invalid`.
- `xs` and `sm` presets fall below the 44 px target-size minimum on their own — the label row usually compensates, but reserve them for dense forms. `md` and `lg` meet the minimum.

## Related

- [Component index](README.md)
- [Field](field.md) — pair with Field for label + layout around any control
- [Input](input.md) — the underlying control Checkbox wraps
- Full maintainer reference: [`skills/component-checkbox/reference.md`](../../skills/component-checkbox/reference.md)
