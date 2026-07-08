# Field — Usage Guide

A minimal wrapper that pairs a `<label>` with a single form control and guarantees the label is associated via `htmlFor`. Field owns the layout and label association only — error and hint text live in the control (Input handles `errorMessage` / `hintText` and their `aria-describedby` ids).

## Add it to your project

1. **One-time setup** (run once per project): `/setup` — installs `sass`, writes `.acss-target.json`, and creates the `ui.tsx` foundation every component imports.
2. **Add this component:** `/kit-add Field` — copies `field.tsx` + `field.scss` into your components directory (default `src/components/fpkit/`).
   - Or run `/kit-sync` once to install **all** components, the foundation, and a starter theme together.

The generated component is self-contained — no `@fpkit/acss` install required. Layer a control (Input, Select, Textarea) inside it.

## Import

```tsx
import Field from './fpkit/field/field'
import Input from './fpkit/input/input'
import './fpkit/field/field.scss'
```

Adjust the paths to match the `componentsDir` in your `.acss-target.json`.

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `label` | `React.ReactNode` | — (required) | Label content — text or a React node. |
| `labelFor` | `string` | — (required) | Must match the `id` of the wrapped control (compile-time enforced). |
| `children` | `React.ReactNode` | — (required) | The form control rendered inside. |
| `id` | `string` | — | Optional id on the wrapper `<div>`. |
| `classes` | `string` | — | Wrapper CSS classes. |
| `styles` | `React.CSSProperties` | — | Inline styles. |

Plus any native `<label>` attribute except `htmlFor` (Field owns that via `labelFor`).

## Examples

```tsx
// Field + Input
<Field labelFor="email" label="Email address">
  <Input id="email" type="email" required />
</Field>

// Field + Select
<Field labelFor="country" label="Country">
  <select id="country" name="country">
    <option value="">Select a country</option>
    <option value="us">United States</option>
  </select>
</Field>

// Custom label content
<Field labelFor="card" label={<>Card number <small>(no spaces)</small></>}>
  <Input id="card" inputMode="numeric" pattern="\d*" required />
</Field>
```

The `labelFor` value must equal the wrapped control's `id` — that pairing is what associates the label with the control.

## Theming

Override these CSS custom properties in your theme to restyle every field. Each has a fallback, so overriding is optional. Field styles hang off the `[data-style="fields"]` hook the component sets.

| Variable | Purpose |
|----------|---------|
| `--field-display` / `--field-direction` | Layout mode and stacking direction. |
| `--field-gap` | Space between label and control. |
| `--field-margin-block-end` | Spacing below each field. |
| `--field-label-fs` | Label font size. |
| `--field-label-fw` | Label font weight. |
| `--field-label-color` | Label color. |
| `--field-label-margin-block-end` | Space below the label. |

```css
:root {
  --field-gap: 0.5rem;
  --field-label-fw: 600;
}
```

Generate a full matching theme with `/theme-create` (see [styles.md](../styles.md)).

## Accessibility

- `labelFor` is required by the type, so a missing label is impossible at the Field level. The remaining discipline is making the wrapped control's `id` match (WCAG 1.3.1, 4.1.2).
- Always pass a visible `label`. Field does not support visually-hidden labels — if you truly need one, use the bare control with `aria-label` / `aria-labelledby` instead.
- Field does not render `*`, required text, or error/hint paragraphs — the wrapped control owns those. Don't add `<p class="error">` siblings inside Field; the control won't pick them up in `aria-describedby`.

## Related

- [Component index](README.md)
- [Input](input.md) — the control most often wrapped by Field
- [Checkbox](checkbox.md) — bundles its own label; use instead of Field for checkboxes
- Full maintainer reference: [`skills/component-field/reference.md`](../../skills/component-field/reference.md)
