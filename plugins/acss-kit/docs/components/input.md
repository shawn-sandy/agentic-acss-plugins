# Input — Usage Guide

A text-based form control with first-class validation states, error/hint association, and the kit-builder accessible-disabled pattern. Emits `aria-required`, `aria-invalid`, `aria-readonly`, and a generated `aria-describedby` linking to error and hint text. Pair it with [Field](field.md) for label association.

## Add it to your project

1. **One-time setup** (run once per project): `/setup` — installs `sass`, writes `.acss-target.json`, and creates the `ui.tsx` foundation every component imports.
2. **Add this component:** `/kit-add Input` — copies `input.tsx` + `input.scss` into your components directory (default `src/components/fpkit/`). Add `Field` too (or run `/kit-sync`) for label association.
   - Or run `/kit-sync` once to install **all** components, the foundation, and a starter theme together.

The generated component is self-contained — no `@fpkit/acss` install required.

## Import

```tsx
import Field from './fpkit/field/field'
import Input from './fpkit/input/input'
import './fpkit/field/field.scss'
import './fpkit/input/input.scss'
```

Adjust the path to match the `componentsDir` in your `.acss-target.json`.

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `id` | `string` | — (required) | Label association and `aria-describedby` id generation. |
| `type` | `React.HTMLInputTypeAttribute` | `'text'` | HTML input type. |
| `name` | `string` | — | Form field name. |
| `value` | `string \| number \| readonly string[]` | — | Controlled value. |
| `defaultValue` | `string \| number \| readonly string[]` | — | Uncontrolled initial value. |
| `placeholder` | `string` | — | Placeholder text (not a substitute for a label). |
| `disabled` | `boolean` | `false` | Accessible disabled — renders `aria-disabled`, keeps the element focusable. |
| `isDisabled` | `boolean` | — | Legacy alias for `disabled`; `disabled` takes precedence. |
| `readOnly` | `boolean` | `false` | Read-only state. |
| `required` | `boolean` | `false` | Renders `aria-required` + native `required`. |
| `validationState` | `'none' \| 'valid' \| 'invalid'` | `'none'` | Drives `aria-invalid` and the `data-validation` attribute. |
| `errorMessage` | `string` | — | Links a `{id}-error` reference via `aria-describedby`. |
| `hintText` | `string` | — | Links a `{id}-hint` reference via `aria-describedby`. |
| `onEnter` | `React.KeyboardEventHandler` | — | Convenience handler for Enter; fires after `onKeyDown`. |
| `classes` | `string` | — | Custom CSS classes. |

Plus `onChange`, `onBlur`, `onFocus`, `onKeyDown`, `maxLength`, `minLength`, `pattern`, `autoComplete`, `autoFocus`, `inputMode`, and other native `<input>` attributes.

## Examples

```tsx
// Basic Field + Input
<Field labelFor="email" label="Email">
  <Input id="email" type="email" required />
</Field>

// With validation + error message
const [email, setEmail] = useState('')
const [emailErr, setEmailErr] = useState<string | undefined>()

<Field labelFor="email" label="Email">
  <Input
    id="email"
    type="email"
    value={email}
    onChange={(e) => setEmail(e.target.value)}
    validationState={emailErr ? 'invalid' : 'none'}
    errorMessage={emailErr}
    required
  />
  {emailErr && <p id="email-error" role="alert">{emailErr}</p>}
</Field>

// With hint text
<Field labelFor="password" label="Password">
  <Input
    id="password"
    type="password"
    hintText="At least 8 characters with one number"
    minLength={8}
    required
  />
  <p id="password-hint">At least 8 characters with one number</p>
</Field>

// Submit on Enter
<Input id="search" type="search" onEnter={(e) => runSearch(e.currentTarget.value)} />

// Read-only
<Input id="invoice" defaultValue="INV-12345" readOnly />
```

## Theming

Override these CSS custom properties in your theme to restyle every input. Each has a fallback, so overriding is optional.

| Variable | Purpose |
|----------|---------|
| `--input-bg` / `--input-color` | Background and text color. |
| `--input-border` | Border (the primary editable-area indicator). |
| `--input-radius` | Corner radius. |
| `--input-focus-border` / `--input-focus-ring` | Focus border and ring. |
| `--input-invalid-border` / `--input-invalid-ring` | Invalid-state styling. |
| `--input-valid-border` | Valid-state border. |
| `--input-disabled-bg` / `--input-disabled-opacity` | Disabled appearance. |

```css
:root {
  --input-radius: 0.5rem;
  --input-focus-border: #6d28d9;
}
```

Generate a full matching theme with `/theme-create` (see [styles.md](../styles.md)).

## Accessibility

- Input does not render its own `<label>`. Wrap it with [Field](field.md) (or a `<label htmlFor={id}>`) so the control has an accessible name; the `id` prop is required.
- Disabled state uses `aria-disabled="true"` instead of the native `disabled` attribute, keeping the input in the tab order (WCAG 2.1.1). `onChange`/`onBlur`/`onKeyDown` no-op while disabled; `onFocus` is intentionally not gated.
- `validationState="invalid"` sets `aria-invalid="true"` and `data-validation="invalid"`. Pass `errorMessage` and render the error yourself with id `{id}-error`.
- `hintText` links helper text via id `{id}-hint`; both hint and error are combined into one `aria-describedby`.
- Never rely on `placeholder` as the only label — it disappears on focus and has low contrast.

## Related

- [Component index](README.md)
- [Field](field.md) — provides the label association Input needs
- Full maintainer reference: [`skills/component-input/reference.md`](../../skills/component-input/reference.md)
