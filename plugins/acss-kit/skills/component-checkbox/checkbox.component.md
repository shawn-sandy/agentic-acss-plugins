---
spec: component.md
version: alpha
name: checkbox
element: input
tokens:
  rounded: "{rounded.sm}"
  borderColor: "{colors.border}"
  background: "{colors.surface}"
  checkedBackground: "{colors.primary}"
  checkedBorder: "{colors.primary}"
  labelColor: "{colors.text}"
  requiredColor: "{colors.danger}"
  gap: "{spacing.sm}"
  labelTypography: "{typography.body-md}"
props:
  id:
    type: string
    required: true
    a11y: "required for label association via htmlFor + id"
  label:
    type: node
    required: true
    a11y: "always-visible associated label"
  size:
    values: [xs, sm, md, lg]
    default: md
    maps-to: "data-checkbox-size"
  checked:
    type: boolean
    a11y: "controlled checked state"
  defaultChecked:
    type: boolean
    a11y: "uncontrolled initial state"
  value:
    type: string
    default: "on"
  disabled:
    type: boolean
    maps-to: "aria-disabled"
    a11y: "stays in tab order; blocks onChange (WCAG 2.1.1)"
  required:
    type: boolean
    maps-to: "aria-required"
    a11y: "renders visible `*` with aria-label=required"
  validationState:
    values: [none, invalid]
    maps-to: "aria-invalid"
slots: [label]
variants:
  xs: { maps-to: "data-checkbox-size=xs" }
  sm: { maps-to: "data-checkbox-size=sm" }
  md: { maps-to: "data-checkbox-size=md" }
  lg: { maps-to: "data-checkbox-size=lg" }
behavior: controlled-mode-warning
a11y: [1.3.1, 1.4.3, 1.4.11, 2.1.1, 2.4.7, 2.5.8, 3.3.1, 3.3.2, 4.1.2]
targets: [react, html, astro, angular, vue, svelte, web-component]
---

# Component: Checkbox

> **Neutral COMPONENT.md** for the acss-kit `checkbox`. The framework-agnostic
> source of truth lives in the `##` body below; the canonical React projection is
> the `## Target: react` adapter at the end (byte-aligned with the legacy
> `reference.md`). `/kit-add checkbox` reads this file: `## Styles` →
> `checkbox.scss`, `## Target: react` → `checkbox.tsx`.
>
> **Verified against fpkit source:** `@fpkit/acss@6.5.0` (closest tagged ref to
> npm `6.6.0`). Wraps the kit-builder `Input` with `type="checkbox"` and exposes
> a boolean `onChange` API. Adds size variants (`xs` | `sm` | `md` | `lg`), an
> automatic visible label, and a controlled-vs-uncontrolled-mode warning in
> development. Inherits all validation, disabled, and ARIA logic from `Input`.

## Overview

A checkbox input with simplified ergonomics: boolean `onChange` (not the native
`ChangeEvent`), bundled visible label, size presets, and full validation
passthrough to the underlying `Input`. Renders the standard
`<input type="checkbox">` plus an associated `<label>` inside a wrapper `<div>`
that carries the size attribute for SCSS targeting.

## Semantic Structure

```html
<!-- variant: default (md) -->
<div data-checkbox-size="md">
  <input type="checkbox" id="terms" class="checkbox-input" value="on" />
  <label for="terms" class="checkbox-label">
    <!-- slot: label -->
  </label>
</div>

<!-- variant: small -->
<div data-checkbox-size="sm">
  <input type="checkbox" id="opt-sm" class="checkbox-input" value="on" />
  <label for="opt-sm" class="checkbox-label">
    <!-- slot: label -->
  </label>
</div>

<!-- variant: checked -->
<div data-checkbox-size="md">
  <input type="checkbox" id="agree" class="checkbox-input" value="on" checked />
  <label for="agree" class="checkbox-label">
    <!-- slot: label -->
  </label>
</div>

<!-- variant: required (visible asterisk with aria-label) -->
<div data-checkbox-size="md">
  <input
    type="checkbox"
    id="confirm"
    class="checkbox-input"
    value="on"
    aria-required="true"
  />
  <label for="confirm" class="checkbox-label">
    <!-- slot: label -->
    <span class="checkbox-required" aria-label="required"> *</span>
  </label>
</div>

<!-- variant: disabled (stays focusable; aria-disabled, not the native attribute) -->
<div data-checkbox-size="md">
  <input
    type="checkbox"
    id="opt-off"
    class="checkbox-input"
    value="on"
    aria-disabled="true"
  />
  <label for="opt-off" class="checkbox-label">
    <!-- slot: label -->
  </label>
</div>

<!-- variant: invalid (aria-invalid cascades from Input) -->
<div data-checkbox-size="md">
  <input
    type="checkbox"
    id="bad"
    class="checkbox-input"
    value="on"
    aria-invalid="true"
  />
  <label for="bad" class="checkbox-label">
    <!-- slot: label -->
  </label>
</div>
```

The host element is the native `<input type="checkbox">` (custom-rendered via
`appearance: none` + `::after`, but with native semantics preserved). The
wrapper `<div>` carries `data-checkbox-size` for SCSS targeting; size surfaces as
that data attribute. Disabled state surfaces as `aria-disabled="true"` (not the
native attribute) so the input stays focusable (WCAG 2.1.1). The `<label>` is
always rendered and associated via `for`/`id`.

## Props

| Prop | Values | Required | Surfaces as |
|---|---|---|---|
| `id` | string | yes | `id` attribute (label association via `htmlFor`) |
| `label` | node | yes | visible `<label>` content |
| `size` | `xs` \| `sm` \| `md` \| `lg` | no | `data-checkbox-size` on wrapper |
| `checked` | boolean | no | controlled checked state |
| `defaultChecked` | boolean | no | uncontrolled initial state |
| `value` | string | no | form-submission value (default `'on'`) |
| `disabled` | boolean | no | `aria-disabled` (inherited from Input) |
| `required` | boolean | no | `aria-required` + visible `*` |
| `validationState` | `none` \| `invalid` | no | `aria-invalid` (inherited from Input) |
| `onChange` | `(checked: boolean) => void` | no | boolean change handler |

## Tokens & CSS Variables

Themeable properties reference DESIGN.md primitives via `var(--token, <fallback>)`;
each keeps a hardcoded fallback so the component renders with no design system.

```scss
// Size tokens (data-checkbox-size attribute)
--checkbox-size-xs: 0.875rem;
--checkbox-size-sm: 1rem;
--checkbox-size-md: 1.25rem;   // default
--checkbox-size-lg: 1.5rem;

--checkbox-size: var(--checkbox-size-md);
--checkbox-radius: var(--radius-sm, 0.25rem);
--checkbox-border-color: var(--color-border, #d0d0d0);
--checkbox-bg: var(--color-surface, #fff);
--checkbox-checked-bg: var(--color-primary, #0066cc);
--checkbox-checked-border: var(--color-primary, #0066cc);
--checkbox-check-color: #fff;

--checkbox-gap: var(--space-sm, 0.5rem);
--checkbox-label-fs: 1rem;
--checkbox-label-color: var(--color-text, inherit);

--checkbox-focus-ring-color: var(--color-focus-ring, rgba(0, 102, 204, 0.4));
--checkbox-focus-ring: 0 0 0 3px var(--checkbox-focus-ring-color);

--checkbox-disabled-opacity: 0.6;
--checkbox-required-color: var(--color-danger, #dc3545);
```

## Styles

```scss
// checkbox.scss
.checkbox-input {
  // Hide native rendering but keep the input itself accessible
  appearance: none;
  -webkit-appearance: none;
  width: var(--checkbox-size, 1.25rem);
  height: var(--checkbox-size, 1.25rem);
  border: 2px solid var(--checkbox-border-color, #d0d0d0);
  border-radius: var(--checkbox-radius, var(--radius-sm, 0.25rem));
  background: var(--checkbox-bg, #fff);
  cursor: pointer;
  flex-shrink: 0;
  display: inline-grid;
  place-content: center;

  &:checked {
    background: var(--checkbox-checked-bg, #0066cc);
    border-color: var(--checkbox-checked-border, #0066cc);

    &::after {
      content: '';
      width: 60%;
      height: 30%;
      border-bottom: 2px solid var(--checkbox-check-color, #fff);
      border-left: 2px solid var(--checkbox-check-color, #fff);
      transform: rotate(-45deg) translateY(-15%);
    }
  }

  &:focus-visible {
    outline: none;
    box-shadow: var(--checkbox-focus-ring, 0 0 0 3px rgba(0, 102, 204, 0.4));
  }

  &[aria-disabled="true"] {
    cursor: not-allowed;
    opacity: var(--checkbox-disabled-opacity, 0.6);
  }
}

[data-checkbox-size] {
  display: inline-flex;
  align-items: center;
  gap: var(--checkbox-gap, var(--space-sm, 0.5rem));

  // Size presets — set the --checkbox-size CSS variable based on the data attr
  &[data-checkbox-size="xs"] { --checkbox-size: var(--checkbox-size-xs, 0.875rem); }
  &[data-checkbox-size="sm"] { --checkbox-size: var(--checkbox-size-sm, 1rem); }
  &[data-checkbox-size="md"] { --checkbox-size: var(--checkbox-size-md, 1.25rem); }
  &[data-checkbox-size="lg"] { --checkbox-size: var(--checkbox-size-lg, 1.5rem); }
}

.checkbox-label {
  font-size: var(--checkbox-label-fs, 1rem);
  color: var(--checkbox-label-color, inherit);
  cursor: pointer;
  user-select: none;
}

.checkbox-required {
  color: var(--checkbox-required-color, #dc3545);
  margin-inline-start: var(--space-xs, 0.125rem);
}
```

## Behavior

**`controlled-mode-warning`** — Checkbox supports both controlled (`checked` +
`onChange`) and uncontrolled (`defaultChecked`) modes. State ownership is
determined once: if `checked` is defined the input is controlled, otherwise it is
uncontrolled. In development, flipping between the two modes (e.g.
`checked={undefined}` after mounting with `checked={true}`) logs a console
warning so the ownership bug surfaces early; production builds skip the warning.
The boolean `onChange` callback adapts the native `ChangeEvent` — it receives
`e.target.checked` (true/false), never the raw event. While disabled, the
inherited `Input` disabled-state wrapper gates `onChange` so the callback never
fires.

Neutral reference implementation (static HTML / vanilla JS):

```js
// Idempotent: calling init() twice on the same root does not double-bind.
const SENTINEL = 'data-acss-checkbox-init';

export function init(root = document, opts = {}) {
  const inputs = root.querySelectorAll('.checkbox-input');
  for (const el of inputs) {
    if (el.getAttribute(SENTINEL) === 'true') continue;
    el.setAttribute(SENTINEL, 'true');
    el.addEventListener('change', (e) => {
      if (el.getAttribute('aria-disabled') === 'true') {
        e.preventDefault();
        return;
      }
      // Boolean onChange contract — emit checked, not the raw event.
      opts.onChange?.(e.target.checked);
    });
  }
}
```

A generator realizes this spec idiomatically per target (React boolean
`onChange` adapter, Vue `v-model`, Svelte `bind:checked`, Angular
`ControlValueAccessor`); the `react` adapter below ships the canonical
controlled/uncontrolled handling and dev-mode warning.

## Accessibility

WCAG 2.2 AA compliance for the generated `Checkbox` component.

**Label association (required)**
- The `id` and `label` props are both required by type. The component renders `<label htmlFor={id}>` so the label is programmatically associated with the input. Clicking the label toggles the checkbox; screen readers announce the label when the checkbox is focused.
- The label is always visible — Checkbox doesn't render visually-hidden labels. If you need a visually-hidden label, you're better off with a different design pattern.

**Native semantics — preserved**
- Renders a native `<input type="checkbox">`. Browser provides built-in keyboard handling: Space toggles. Tab navigates. Enter does NOT toggle a checkbox (intentional, native behavior — don't add custom Enter handling to mimic Space).
- The visual appearance is custom (`appearance: none` + `::after` checkmark) but the semantics remain native. Screen readers still announce "checkbox", "checked"/"not checked".

**Disabled vs aria-disabled**
- Inherits the kit-builder accessible-disabled pattern from Input: `disabled` prop sets `aria-disabled="true"` (not the native `disabled` attribute). The element stays focusable so screen-reader users discover it (WCAG 2.1.1 Keyboard).
- The `useDisabledState` wrapper from Input gates `onChange` so the boolean callback never fires while disabled.

**Validation states**
- `validationState="invalid"` cascades from Input — `aria-invalid="true"` is set automatically. Screen readers announce the invalid state on focus.
- `errorMessage` and `hintText` work exactly as in Input — the component generates `aria-describedby` ids; render the actual `<p>` elements yourself with matching ids near the checkbox.

**Required**
- `required` renders both `aria-required="true"` (on the input, via Input) and a visible `*` after the label. The asterisk has `aria-label="required"` so screen readers don't announce it as the literal symbol "asterisk".

**Focus visible**
- Native input is hidden visually but stays in tab order. `:focus-visible` adds the focus ring on the visual checkbox via `box-shadow`. The ring color must meet 3:1 against both the page background and the page-adjacent surface (WCAG 1.4.11 Non-text Contrast).

**Color contrast**
- Checkmark color (`--checkbox-check-color`) on checked background (`--checkbox-checked-bg`) must meet 3:1 (icon contrast, WCAG 1.4.11).
- Border color (`--checkbox-border-color`) when unchecked, against the page background, must meet 3:1 — the border is the only visual indicator of the unchecked checkbox.
- Disabled opacity (`--checkbox-disabled-opacity: 0.6`) plus the page background must keep checkmark and border above 3:1 in disabled-checked state. Verify with `validate_theme.py` for custom themes.

**Target size**
- `xs` and `sm` size presets fall below WCAG 2.5.8 Target Size Minimum (44 px). The wrapper's clickable label area expands the effective target size, but only if there's enough horizontal label text or padding. Use `xs`/`sm` only in dense forms where surrounding spacing or pointer accuracy compensates.
- `md` (1.25rem = 20 px) checkbox + label is typically a 44+ px tall row; meets the minimum when label text is present.
- `lg` (1.5rem = 24 px) easily meets the minimum.

**Controlled-mode warning**
- In development, the component logs a console warning if you flip between controlled and uncontrolled modes (e.g., `checked={undefined}` after mounting with `checked={true}`). This catches a common bug where state ownership is unclear. Production builds skip the warning.

**WCAG 2.2 AA criteria addressed**
- 1.3.1 Info and Relationships (label association via htmlFor + id)
- 1.4.3 Contrast Minimum (label text)
- 1.4.11 Non-text Contrast (checkmark, border, focus ring, required asterisk)
- 2.1.1 Keyboard (native checkbox toggling via Space)
- 2.4.7 Focus Visible (`:focus-visible` ring)
- 2.5.5 / 2.5.8 Target Size (md+ presets meet AA; xs/sm need surrounding compensation)
- 3.3.1 Error Identification (inherited from Input via `validationState` + `errorMessage`)
- 3.3.2 Labels or Instructions (label always present and visible)
- 4.1.2 Name, Role, Value (native input + label + state via aria-* attrs)

## Examples

```html
<div data-checkbox-size="md">
  <input type="checkbox" id="terms" class="checkbox-input" value="on" />
  <label for="terms" class="checkbox-label">I accept the terms and conditions</label>
</div>

<div data-checkbox-size="sm">
  <input type="checkbox" id="opt-sm" class="checkbox-input" value="on" />
  <label for="opt-sm" class="checkbox-label">Small</label>
</div>

<div data-checkbox-size="md">
  <input type="checkbox" id="confirm" class="checkbox-input" value="on" aria-required="true" />
  <label for="confirm" class="checkbox-label">
    I understand this action is permanent
    <span class="checkbox-required" aria-label="required"> *</span>
  </label>
</div>
```

## Target: react

`generation: { export: Checkbox, file: checkbox.tsx, scss: checkbox.scss, imports: "Input from '../input/input', type InputProps", dependencies: [input] }`

The React adapter is the canonical TSX projection. Checkbox depends on `Input` —
generate `input.tsx` first if it isn't already present. `/kit-add checkbox
--target=react` emits the assembled file: the Props Interface and the TSX
Template below.

## Props Interface

```tsx
export interface CheckboxProps extends Omit<
  InputProps,
  'type' | 'value' | 'onChange' | 'defaultValue' | 'placeholder'
> {
  /** Required for label association */
  id: string
  /** Visible label text */
  label: React.ReactNode
  /** Size preset (default: 'md') */
  size?: 'xs' | 'sm' | 'md' | 'lg'
  /** Controlled checked state */
  checked?: boolean
  /** Uncontrolled initial state */
  defaultChecked?: boolean
  /** Form-submission value when checked (default: 'on') */
  value?: string
  /** Boolean change handler — receives true/false, not a ChangeEvent */
  onChange?: (checked: boolean) => void
  /** Wrapper div CSS classes */
  classes?: string
  /** Input element CSS classes (default: 'checkbox-input') */
  inputClasses?: string
  /** CSS custom properties for theming / custom sizing */
  styles?: React.CSSProperties
}
```

## TSX Template

```tsx
import React from 'react'
import Input, { type InputProps } from '../input/input'

export interface CheckboxProps extends Omit<
  InputProps,
  'type' | 'value' | 'onChange' | 'defaultValue' | 'placeholder'
> {
  id: string
  label: React.ReactNode
  size?: 'xs' | 'sm' | 'md' | 'lg'
  checked?: boolean
  defaultChecked?: boolean
  value?: string
  onChange?: (checked: boolean) => void
  classes?: string
  inputClasses?: string
  styles?: React.CSSProperties
}

export const Checkbox = React.forwardRef<HTMLInputElement, CheckboxProps>(({
  id,
  label,
  checked,
  defaultChecked,
  value = 'on',
  onChange,
  classes,
  inputClasses,
  styles,
  size,
  name,
  disabled,
  required,
  validationState,
  errorMessage,
  hintText,
  onBlur,
  onFocus,
  autoFocus,
  ...props
}, ref) => {
  // Adapt boolean onChange to native ChangeEvent
  const handleChange = React.useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      onChange?.(e.target.checked)
    },
    [onChange],
  )

  const isControlled = checked !== undefined
  const checkedProp = isControlled ? { checked } : {}
  const defaultCheckedProp = !isControlled && defaultChecked !== undefined
    ? { defaultChecked }
    : {}

  // Dev-only: warn on controlled <-> uncontrolled mode flip.
  const wasControlledRef = React.useRef(isControlled)
  React.useEffect(() => {
    if (process.env.NODE_ENV === 'development') {
      if (wasControlledRef.current !== isControlled) {
        // eslint-disable-next-line no-console
        console.warn(
          `Checkbox id="${id}" is changing from ${wasControlledRef.current ? 'controlled' : 'uncontrolled'} to ${isControlled ? 'controlled' : 'uncontrolled'}. Pick one and stick with it.`,
        )
      }
      wasControlledRef.current = isControlled
    }
  }, [isControlled, id])

  return (
    <div className={classes} style={styles} data-checkbox-size={size}>
      <Input
        ref={ref}
        type="checkbox"
        id={id}
        name={name}
        value={value}
        {...checkedProp}
        {...defaultCheckedProp}
        classes={inputClasses || 'checkbox-input'}
        disabled={disabled}
        required={required}
        validationState={validationState}
        errorMessage={errorMessage}
        hintText={hintText}
        onChange={handleChange}
        onBlur={onBlur}
        onFocus={onFocus}
        autoFocus={autoFocus}
        {...props}
      />
      <label htmlFor={id} className="checkbox-label">
        {label}
        {required && (
          <span className="checkbox-required" aria-label="required">{' *'}</span>
        )}
      </label>
    </div>
  )
})

Checkbox.displayName = 'Checkbox'
export default Checkbox
```
