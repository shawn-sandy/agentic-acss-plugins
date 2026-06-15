---
spec: component.md
version: alpha
name: field
element: div
tokens:
  gap: "{spacing.sm}"
  marginBlockEnd: "{spacing.md}"
  labelColor: "{colors.text}"
  labelMarginBlockEnd: "{spacing.xs}"
  labelTypography: "{typography.label-sm}"
props:
  label:
    type: node
    required: true
  labelFor:
    type: string
    required: true
    maps-to: "label htmlFor"
    a11y: "programmatic label-control association (WCAG 1.3.1, 4.1.2)"
  id:
    type: string
  classes:
    type: string
  styles:
    type: object
slots: [children]
a11y: [1.3.1, 3.3.2, 4.1.2]
targets: [react, html, astro, angular, vue, svelte, web-component]
---

# Component: Field

> **Neutral COMPONENT.md** for the acss-kit `field`. The framework-agnostic
> source of truth lives in the `##` body below; the canonical React projection is
> the `## Target: react` adapter at the end (byte-aligned with the legacy
> `reference.md`). `/kit-add field` reads this file: `## Styles` → `field.scss`,
> `## Target: react` → `field.tsx`.
>
> **Verified against fpkit source:** `@fpkit/acss@6.5.0` (closest tagged ref to
> npm `6.6.0`). Field is the small label+control wrapper from
> `components/form/fields.tsx`. The vendored version preserves the upstream
> `labelFor` requirement (compile-time accessible-name guarantee for the wrapped
> control) and the `data-style="fields"` SCSS hook.

## Overview

A minimal wrapper that pairs a `<label>` with a single form control (Input,
Select, Textarea, etc.) and ensures the label is associated via `htmlFor`. Field
doesn't render error or helper text — those concerns live in the control itself
(Input handles `errorMessage` / `hintText` and generates the `aria-describedby`
ids). Use Field for the layout + label association; layer the control inside.

## Semantic Structure

```html
<!-- variant: default (Field + Input) -->
<div data-style="fields">
  <label for="email">Email address</label>
  <!-- slot: children — the wrapped control, whose id matches labelFor -->
</div>

<!-- variant: Field + native select -->
<div data-style="fields">
  <label for="country">Country</label>
  <!-- slot: children -->
</div>

<!-- variant: custom label content -->
<div data-style="fields">
  <label for="card">Card number <small>(no spaces)</small></label>
  <!-- slot: children -->
</div>
```

The host element is a `<div data-style="fields">` wrapper. It always contains a
`<label>` whose `for` (`htmlFor` in React) points at the wrapped control's `id`,
followed by the control itself in the `children` slot. The `data-style="fields"`
attribute is the SCSS styling hook.

## Props

| Prop | Values | Required | Surfaces as |
|---|---|---|---|
| `label` | React node | yes | `<label>` content |
| `labelFor` | string | yes | `<label htmlFor>` (control `id`) |
| `id` | string | no | `id` on the wrapper div |
| `classes` | string | no | class on the wrapper |
| `styles` | object | no | inline styles on the wrapper |

## Tokens & CSS Variables

```scss
--field-display: flex;
--field-direction: column;
--field-gap: var(--space-sm, 0.375rem);
--field-margin-block-end: var(--space-md, 1rem);

--field-label-fs: 0.875rem;
--field-label-fw: 500;
--field-label-color: var(--color-text, inherit);
--field-label-margin-block-end: var(--space-xs, 0.25rem);
```

## Styles

```scss
// field.scss
[data-style="fields"] {
  display: var(--field-display, flex);
  flex-direction: var(--field-direction, column);
  gap: var(--field-gap, var(--space-sm, 0.375rem));
  margin-block-end: var(--field-margin-block-end, var(--space-md, 1rem));

  > label {
    font-size: var(--field-label-fs, 0.875rem);
    font-weight: var(--field-label-fw, 500);
    color: var(--field-label-color, inherit);
    margin-block-end: var(--field-label-margin-block-end, var(--space-xs, 0.25rem));
    display: block;
  }
}
```

## Accessibility

WCAG 2.2 AA compliance for the generated `Field` component.

**Label association (required)**
- `labelFor` is required by the type; pass the `id` of the wrapped control. The `<label htmlFor={labelFor}>` association lets users click the label to focus the control and lets screen readers announce the label when the control is focused (WCAG 1.3.1 Info and Relationships, WCAG 4.1.2 Name, Role, Value).
- The compile-time `labelFor: string` requirement makes "missing label" impossible at the Field level. The remaining authoring discipline is making sure the wrapped control's `id` matches.

**Visible label policy**
- Always pass a visible `label` — Field does not support visually-hidden labels. If you need a visually-hidden label (rare; consider whether the design is excluding sighted users with cognitive needs), use the bare control with an `aria-label` or `aria-labelledby` instead of Field.

**Layout & required indicators**
- Field doesn't render `*` or "required" text. The wrapped Input handles `aria-required` and visual required indicators if needed. This split keeps Field's responsibility narrow.

**Error & helper text**
- Field doesn't render error or hint text. Input/Textarea/Select render their own error / hint paragraphs and link them via `aria-describedby`. Don't manually add `<p class="error">` siblings inside Field — the control will not pick them up in `aria-describedby`.

**WCAG 2.2 AA criteria addressed**
- 1.3.1 Info and Relationships (programmatic label-control association)
- 3.3.2 Labels or Instructions (visible label is required)
- 4.1.2 Name, Role, Value (control gets its accessible name from the `<label>`)

## Examples

```html
<!-- Field + input -->
<div data-style="fields">
  <label for="email">Email address</label>
  <input id="email" type="email" required />
</div>

<!-- Field + native select -->
<div data-style="fields">
  <label for="country">Country</label>
  <select id="country" name="country">
    <option value="">Select a country</option>
    <option value="us">United States</option>
  </select>
</div>
```

## Target: react

`generation: { export: Field, file: field.tsx, scss: field.scss, imports: "UI from '../ui'", dependencies: [] }`

The React adapter is the canonical TSX projection — `/kit-add field --target=react`
emits the assembled file: the Props Interface and the TSX Template below.

## Props Interface

```tsx
export type FieldProps = {
  /** Label content — accepts text or a React node */
  label: React.ReactNode
  /**
   * REQUIRED — must match the `id` of the wrapped control.
   * The type makes the value required; runtime can't enforce that the wrapped control
   * actually has a matching `id`, so authoring discipline matters here.
   */
  labelFor: string
  /** The form control rendered inside (Input, Select, Textarea, etc.) */
  children: React.ReactNode
  /** Optional id on the wrapper div */
  id?: string
  classes?: string
  styles?: React.CSSProperties
} & Omit<React.ComponentPropsWithoutRef<'label'>, 'htmlFor'>
```

## TSX Template

```tsx
import UI from '../ui'
import React from 'react'

export type FieldProps = {
  label: React.ReactNode
  labelFor: string
  children: React.ReactNode
  id?: string
  classes?: string
  styles?: React.CSSProperties
} & Omit<React.ComponentPropsWithoutRef<'label'>, 'htmlFor'>

export const Field = ({
  label,
  labelFor,
  id,
  styles,
  classes,
  children,
  ...props
}: FieldProps) => (
  <UI
    as="div"
    id={id}
    styles={styles}
    classes={classes}
    data-style="fields"
    {...props}
  >
    <label htmlFor={labelFor}>{label}</label>
    {children}
  </UI>
)

Field.displayName = 'Field'
export default Field
```
