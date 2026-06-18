---
spec: component.md
version: alpha
name: input
element: input
tokens:
  background: "{colors.surface}"
  textColor: "{colors.on-surface}"
  border: "{colors.outline-variant}"
  rounded: "{rounded.md}"
  paddingInline: "{spacing.md}"
  paddingBlock: "{spacing.sm}"
  focusBorder: "{colors.primary}"
  invalidBorder: "{colors.error}"
  validBorder: "{colors.success}"
props:
  id:
    type: string
    required: true
    a11y: "label association + aria-describedby id generation"
  type:
    type: string
    default: text
    maps-to: "type attribute"
  validationState:
    values: [none, valid, invalid]
    default: none
    maps-to: "data-validation + aria-invalid"
  errorMessage:
    type: string
    maps-to: "aria-describedby={id}-error"
  hintText:
    type: string
    maps-to: "aria-describedby={id}-hint"
  disabled:
    type: boolean
    maps-to: "aria-disabled"
    a11y: "stays in tab order; blocks activation (WCAG 2.1.1)"
  isDisabled:
    type: boolean
    a11y: "legacy compat; `disabled` takes precedence"
  readOnly:
    type: boolean
    maps-to: "aria-readonly + native readonly"
  required:
    type: boolean
    maps-to: "aria-required + native required"
slots: []
variants:
  valid:   { maps-to: "data-validation=valid" }
  invalid: { maps-to: "data-validation=invalid" }
behavior: disabled-activation-guard
a11y: [1.3.1, 1.4.3, 1.4.11, 2.1.1, 2.4.7, 3.3.1, 3.3.2, 4.1.2]
targets: [react, html, astro, angular, vue, svelte, web-component]
---

# Component: Input

> **Neutral COMPONENT.md** for the acss-kit `input`. The framework-agnostic
> source of truth lives in the `##` body below; the canonical React projection is
> the `## Target: react` adapter at the end (byte-aligned with the legacy
> `reference.md`). `/kit-add input` reads this file: `## Styles` → `input.scss`,
> `## Target: react` → `input.tsx`.
>
> **Verified against fpkit source:** [`@fpkit/acss@6.5.0`](https://github.com/shawn-sandy/acss/tree/9063512fa822963d8151c972bed9f5b0e531df0f) (closest tagged ref to
> npm `6.6.0`). Vendored Input keeps the upstream feature surface:
> `validationState` (`none` | `valid` | `invalid`), `errorMessage` + `hintText`
> with auto-generated `aria-describedby` ids, accessible disabled handling, and
> the `onEnter` shortcut for Enter-key form submission. Intentional divergences:
> `useDisabledState` and `resolveDisabledState` are inlined into the generated
> `input.tsx` (same pattern as Button) so the file is self-contained.

## Overview

A text-based form control with first-class validation states, error/hint
association, and the kit-builder accessible-disabled pattern. Supports the
standard HTML input types (`text`, `email`, `password`, `number`, `tel`, `url`,
`search`, etc.) plus `checkbox` (consumed internally by the `Checkbox`
component). Emits `aria-required`, `aria-invalid`, `aria-readonly`, and a
generated `aria-describedby` linking to error and hint text rendered by the
parent.

## Semantic Structure

```html
<!-- variant: default -->
<input type="text" id="field" />

<!-- variant: required -->
<input type="email" id="email" required aria-required="true" />

<!-- variant: invalid (links to externally-rendered error text) -->
<input
  type="email"
  id="email"
  data-validation="invalid"
  aria-invalid="true"
  aria-describedby="email-error"
/>
<p id="email-error" role="alert"><!-- error message --></p>

<!-- variant: with hint text -->
<input
  type="password"
  id="password"
  aria-describedby="password-hint"
/>
<p id="password-hint"><!-- hint text --></p>

<!-- variant: disabled (stays focusable; aria-disabled, not the native attribute) -->
<input type="text" id="field" class="is-disabled" aria-disabled="true" />

<!-- variant: read-only -->
<input type="text" id="invoice" readonly aria-readonly="true" />
```

The host element is `<input>`. `Input` does not render its own `<label>` —
wrap it with `Field` (or a `<label htmlFor={id}>`) for a programmatic name.
Validation surfaces as `data-validation` plus `aria-invalid`; error and hint
text are rendered by the parent and linked via a generated `aria-describedby`.
Disabled state surfaces as `aria-disabled="true"` paired with an `is-disabled`
class so visual and assistive states stay in sync (WCAG 2.1.1).

## Props

| Prop | Values | Required | Surfaces as |
|---|---|---|---|
| `id` | string | yes | `id` attribute + `aria-describedby` id base |
| `type` | HTML input type (default `text`) | no | `type` attribute |
| `validationState` | `none` \| `valid` \| `invalid` | no | `data-validation` + `aria-invalid` |
| `errorMessage` | string | no | `aria-describedby="{id}-error"` |
| `hintText` | string | no | `aria-describedby="{id}-hint"` |
| `disabled` | boolean | no | `aria-disabled` + `is-disabled` class |
| `isDisabled` | boolean | no | legacy compat (`disabled` wins) |
| `readOnly` | boolean | no | `aria-readonly` + native `readonly` |
| `required` | boolean | no | `aria-required` + native `required` |

## Tokens & CSS Variables

Themeable properties reference DESIGN.md primitives via `var(--token, <fallback>)`;
each keeps a hardcoded fallback so the component renders with no design system.

```scss
--input-display: block;
--input-width: 100%;
--input-bg: var(--color-surface, #fff);
--input-color: var(--color-text, inherit);
--input-border: 1px solid var(--color-border, #d0d0d0);
--input-radius: var(--radius-md, 0.375rem);
--input-padding-inline: var(--space-md, 0.75rem);
--input-padding-block: var(--space-sm, 0.5rem);
--input-fs: 1rem;
--input-line-height: 1.5;
--input-transition: border-color 0.15s ease, box-shadow 0.15s ease;

--input-focus-outline: none;
--input-focus-border: var(--color-primary, #0066cc);
--input-focus-ring: 0 0 0 3px rgba(0, 102, 204, 0.2);

--input-invalid-border: var(--color-danger, #dc3545);
--input-invalid-ring: 0 0 0 3px rgba(220, 53, 69, 0.2);

--input-valid-border: var(--color-success, #28a745);

--input-disabled-bg: var(--color-surface-subtle, #f5f5f5);
--input-disabled-opacity: 0.7;
--input-placeholder-color: var(--color-text-subtle, #a0a0a0);
```

## Styles

```scss
// input.scss
input,
textarea,
select {
  display: var(--input-display, block);
  width: var(--input-width, 100%);
  background: var(--input-bg, #fff);
  color: var(--input-color, inherit);
  border: var(--input-border, 1px solid #d0d0d0);
  border-radius: var(--input-radius, var(--radius-md, 0.375rem));
  padding-inline: var(--input-padding-inline, var(--space-md, 0.75rem));
  padding-block: var(--input-padding-block, var(--space-sm, 0.5rem));
  font-size: var(--input-fs, 1rem);
  line-height: var(--input-line-height, 1.5);
  transition: var(--input-transition);

  &::placeholder {
    color: var(--input-placeholder-color, #a0a0a0);
  }

  &:focus {
    outline: var(--input-focus-outline, none);
    border-color: var(--input-focus-border, #0066cc);
    box-shadow: var(--input-focus-ring, 0 0 0 3px rgba(0, 102, 204, 0.2));
  }

  &[data-validation="invalid"],
  &[aria-invalid="true"] {
    border-color: var(--input-invalid-border, #dc3545);
    &:focus {
      box-shadow: var(--input-invalid-ring, 0 0 0 3px rgba(220, 53, 69, 0.2));
    }
  }

  &[data-validation="valid"] {
    border-color: var(--input-valid-border, #28a745);
  }

  &[aria-disabled="true"],
  &.is-disabled {
    background: var(--input-disabled-bg, #f5f5f5);
    opacity: var(--input-disabled-opacity, 0.7);
    cursor: not-allowed;
  }

  &[aria-readonly="true"] {
    background: var(--input-disabled-bg, #f5f5f5);
  }
}
```

## Behavior

**`disabled-activation-guard`** — when `disabled` is set, the input stays
focusable (in tab order) but blocks activation: `onChange`, `onBlur`, and
`onKeyDown` handlers are no-ops, and `aria-disabled="true"` announces the state.
`onFocus` is intentionally NOT gated — focus on a disabled input is allowed,
mirroring native button behaviour. The visual `is-disabled` class is kept in
sync with the ARIA state. Re-enabling restores handler behavior.

Neutral reference implementation (static HTML / vanilla JS):

```js
// Idempotent: calling init() twice on the same root does not double-bind.
const SENTINEL = 'data-acss-input-init';

export function init(root = document, opts = {}) {
  const inputs = root.querySelectorAll('input, textarea, select');
  for (const el of inputs) {
    if (el.getAttribute(SENTINEL) === 'true') continue;
    el.setAttribute(SENTINEL, 'true');
    const guard = (e) => {
      if (el.getAttribute('aria-disabled') === 'true') {
        e.preventDefault();
        e.stopPropagation();
        return;
      }
      opts.onActivate?.(e);
    };
    el.addEventListener('input', guard);
    el.addEventListener('keydown', (e) => {
      if (el.getAttribute('aria-disabled') === 'true') {
        e.preventDefault();
        e.stopPropagation();
        return;
      }
      if (e.key === 'Enter') opts.onEnter?.(e);
    });
  }
}
```

A generator realizes this spec idiomatically per target (React hook, Vue
composable, Svelte action, Angular directive); the `react` adapter below ships
the canonical `useDisabledState` hook.

## Accessibility

WCAG 2.2 AA compliance for the generated `Input` component.

**Label association**
- `Input` does not render its own `<label>`. Wrap with `Field` (or any `<label htmlFor={id}>` pattern) so the control has a programmatic accessible name. The `id` prop is required by type.
- For controls genuinely without a visible label (search box with a magnifying-glass placeholder), pass `aria-label` directly. Don't rely on `placeholder` for accessibility — placeholder text disappears on focus and is not a label.

**Disabled vs aria-disabled**
- Pass `disabled` (typed prop). The component renders `aria-disabled="true"` instead of the native `disabled` attribute, keeping the input in the tab order so screen-reader users can discover it (WCAG 2.1.1 Keyboard).
- The `useDisabledState` hook gates `onChange`, `onBlur`, `onKeyDown` so they no-op while disabled. `onFocus` is intentionally NOT gated — focus on a disabled input is allowed, mirroring native button behaviour.

**Validation states**
- `validationState="invalid"` sets `aria-invalid="true"` and the `data-validation="invalid"` attribute (for SCSS targeting). Screen readers announce "invalid entry" when the field receives focus.
- Pass `errorMessage="..."` so the component generates an `id={id + '-error'}` reference in `aria-describedby`. Render the error text yourself with that id (Field doesn't render it; the parent form composition does).
- `validationState="valid"` is informational — it adds the success styling without announcing anything to screen readers.

**Hint text**
- `hintText` works the same way as `errorMessage` but with id `{id}-hint`. The component generates a multi-id `aria-describedby` so both hint and error are linked.

**Read-only**
- `readOnly` renders `aria-readonly="true"` plus the native `readonly` attribute. Read-only inputs stay focusable and selectable but reject text changes.

**Required**
- `required` renders `aria-required="true"` plus the native `required` attribute. The visual required indicator (asterisk) is *not* automatically rendered by Input — that's a Field/parent concern.

**Color contrast**
- `--input-color` on `--input-bg` must meet 4.5:1 for body text, 3:1 for inputs at large sizes (WCAG 1.4.3).
- `--input-border` against the page background must meet 3:1 (WCAG 1.4.11 Non-text Contrast) since the border is the primary visual indicator of the input's editable area.
- Focus-ring color (`--input-focus-ring`) must meet 3:1 against the page background — at the default `rgba(0, 102, 204, 0.2)` on a white page, the *fill* is too light, but the focus *border* (`--input-focus-border` at full opacity) carries the visual weight. Validate both.
- `--input-disabled-opacity: 0.7` plus `--input-disabled-bg` must keep text contrast above 4.5:1 in disabled state. Verify with `validate_theme.py` if generating a custom palette.

**Placeholder vs label**
- Don't use `placeholder` as the only label. Placeholders disappear on focus and have lower contrast — both fail accessibility for users with cognitive or low-vision needs. Pair Input with a Field, or pass `aria-label` if a visible label is genuinely impossible.

**WCAG 2.2 AA criteria addressed**
- 1.3.1 Info and Relationships (label association via Field; `aria-describedby` for error/hint)
- 1.4.3 Contrast Minimum (input text on background)
- 1.4.11 Non-text Contrast (border, focus ring)
- 2.1.1 Keyboard (aria-disabled keeps element focusable)
- 2.4.7 Focus Visible (focus border + ring)
- 3.3.1 Error Identification (`aria-invalid` + `errorMessage` id linkage)
- 3.3.2 Labels or Instructions (Field provides label; `hintText` provides instructions)
- 4.1.2 Name, Role, Value (native input + accessible name + state via aria-* attrs)

## Examples

```html
<!-- Basic Field + Input -->
<label for="email">Email</label>
<input type="email" id="email" required aria-required="true" />

<!-- With validation + error message -->
<input
  type="email"
  id="email"
  data-validation="invalid"
  aria-invalid="true"
  aria-describedby="email-error"
/>
<p id="email-error" role="alert">Enter a valid email address.</p>

<!-- Read-only -->
<input type="text" id="invoice" value="INV-12345" readonly aria-readonly="true" />
```

## Target: react

`generation: { export: Input, file: input.tsx, scss: input.scss, imports: "UI from '../ui'", dependencies: [] }`

The React adapter is the canonical TSX projection — `useDisabledState` and
`resolveDisabledState` are inlined into `input.tsx` (no shared hook/util tree).
`/kit-add input --target=react` emits the assembled file: the Props Interface,
the inlined Key Pattern, and the TSX Template below.

## Props Interface

```tsx
export type InputValidationState = 'none' | 'valid' | 'invalid'

export type InputProps = {
  /** Required for label association and aria-describedby id generation */
  id: string
  /** HTML input type (default: 'text') */
  type?: React.HTMLInputTypeAttribute
  /** Form field name */
  name?: string
  /** Controlled value */
  value?: string | number | readonly string[]
  /** Uncontrolled initial value */
  defaultValue?: string | number | readonly string[]
  /** Placeholder text */
  placeholder?: string
  /** Inline styles */
  styles?: React.CSSProperties
  /** Custom CSS classes */
  classes?: string
  /** Accessible disabled (aria-disabled pattern; keeps element focusable) */
  disabled?: boolean
  /** Legacy alias for `disabled` — `disabled` takes precedence */
  isDisabled?: boolean
  /** Read-only state */
  readOnly?: boolean
  /** Required for submission and screen readers */
  required?: boolean
  /** Validation state — drives aria-invalid and the data-validation attribute */
  validationState?: InputValidationState
  /** Error message rendered by the parent and linked via aria-describedby */
  errorMessage?: string
  /** Hint / helper text linked via aria-describedby */
  hintText?: string
  /** Native change handler */
  onChange?: React.ChangeEventHandler<HTMLInputElement>
  /** Blur handler */
  onBlur?: React.FocusEventHandler<HTMLInputElement>
  /** Focus handler — NOT gated by disabled state (intentional) */
  onFocus?: React.FocusEventHandler<HTMLInputElement>
  /** Key-down handler */
  onKeyDown?: React.KeyboardEventHandler<HTMLInputElement>
  /** Convenience handler for Enter — fires after onKeyDown */
  onEnter?: React.KeyboardEventHandler<HTMLInputElement>
  maxLength?: number
  minLength?: number
  pattern?: string
  autoComplete?: string
  autoFocus?: boolean
  inputMode?: 'text' | 'numeric' | 'decimal' | 'tel' | 'email' | 'url' | 'search' | 'none'
} & Omit<React.ComponentPropsWithoutRef<'input'>, 'id' | 'disabled' | 'value' | 'defaultValue' | 'onChange' | 'onBlur' | 'onFocus' | 'onKeyDown'>
```

## Key Pattern: Inline Disabled-State Helpers

Same shape as `button.tsx`. Inline these in `input.tsx` rather than importing from a hooks/utils file:

```tsx
const resolveDisabledState = (d?: boolean, id?: boolean) => d ?? id ?? false

function useDisabledState<T extends HTMLElement = HTMLInputElement>(
  disabled: boolean | undefined,
  handlers: {
    onChange?: (e: React.ChangeEvent<T>) => void
    onKeyDown?: (e: React.KeyboardEvent<T>) => void
    onBlur?: (e: React.FocusEvent<T>) => void
  } = {},
  className?: string,
) {
  const isDisabled = Boolean(disabled)
  const merged = [isDisabled ? 'is-disabled' : '', className]
    .filter(Boolean).join(' ')
  const wrap = <E,>(fn?: (e: E) => void) => fn
    ? (e: any) => { if (isDisabled) { e.preventDefault(); e.stopPropagation(); return } fn(e) }
    : undefined

  return {
    disabledProps: { 'aria-disabled': isDisabled, className: merged },
    handlers: {
      onChange: wrap(handlers.onChange),
      onKeyDown: wrap(handlers.onKeyDown),
      onBlur: wrap(handlers.onBlur),
    },
  }
}
```

## TSX Template

```tsx
import UI from '../ui'
import React from 'react'

// [inline resolveDisabledState and useDisabledState as above]

export const Input = React.forwardRef<HTMLInputElement, InputProps>(({
  type = 'text',
  name,
  value,
  defaultValue,
  placeholder,
  id,
  styles,
  classes,
  isDisabled,
  disabled,
  readOnly,
  required = false,
  validationState = 'none',
  errorMessage,
  hintText,
  onChange,
  onBlur,
  onFocus,
  onKeyDown,
  onEnter,
  maxLength,
  minLength,
  pattern,
  autoComplete,
  autoFocus = false,
  inputMode,
  ...props
}: InputProps, ref) => {
  const isInputDisabled = resolveDisabledState(disabled, isDisabled)

  const { disabledProps, handlers } = useDisabledState<HTMLInputElement>(
    isInputDisabled,
    {
      onChange,
      onBlur,
      onKeyDown: (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === 'Enter' && onEnter) onEnter(e)
        onKeyDown?.(e)
      },
    },
    classes,
  )

  const isInvalid = validationState === 'invalid'

  const describedByIds: string[] = []
  if (errorMessage && id) describedByIds.push(`${id}-error`)
  if (hintText && id) describedByIds.push(`${id}-hint`)
  const ariaDescribedBy = describedByIds.length > 0 ? describedByIds.join(' ') : undefined

  return (
    <UI
      as="input"
      ref={ref}
      id={id}
      type={type}
      name={name}
      value={value}
      defaultValue={defaultValue}
      placeholder={placeholder}
      className={disabledProps.className}
      styles={styles}
      readOnly={readOnly}
      required={required}
      maxLength={maxLength}
      minLength={minLength}
      pattern={pattern}
      autoComplete={autoComplete}
      autoFocus={autoFocus}
      inputMode={inputMode}
      {...handlers}
      onFocus={onFocus}
      aria-disabled={disabledProps['aria-disabled']}
      aria-readonly={readOnly}
      aria-required={required}
      aria-invalid={isInvalid}
      aria-describedby={ariaDescribedBy}
      data-validation={validationState}
      {...props}
    />
  )
})

Input.displayName = 'Input'
export default Input
```
