# State Selectors Reference

Gotcha-first notes on the state selector family. The naive choice in each case is the one that ships and then fails a real user — a form that lights up red before anyone has typed, a disabled control that vanishes from the tab order, a focus ring deleted because it fired on a mouse click.

---

## `:user-invalid` over `:invalid` — the default for form styling

`:invalid` matches the moment the element exists. An empty `<input required>` is invalid on page load, before the user has typed a single character, so `input:invalid { border-color: red; }` paints an untouched form in error styling.

`:user-invalid` (and its counterpart `:user-valid`) only match **after** the user has interacted with the control and left it — the browser tracks the interaction for you, which is exactly the behaviour hand-rolled `.touched` classes exist to reproduce.

**Emit `:user-invalid` / `:user-valid` by default.** Reach for bare `:invalid` only when the user explicitly asks for a state that reflects the field's validity independent of interaction — for example, disabling a submit button while the form is incomplete, or styling a fieldset summary.

```css
.field-input:user-invalid {
  border-color: var(--field-invalid-border, #b3261e);
}

.field-input:user-valid {
  border-color: var(--field-valid-border, #146c2e);
}
```

Support note: `:user-invalid` is baseline across current browsers. If a project must support older engines, pair it with an interaction-set attribute rather than falling back to `:invalid`, which reintroduces the load-time flash.

---

## `[aria-disabled="true"]`, never `:disabled`

Per [.claude/rules/scss-conventions.md](../../../../../.claude/rules/scss-conventions.md), the disabled state is styled with the `[aria-disabled="true"]` attribute selector — never the native `disabled` attribute or its `:disabled` pseudo-class.

The reason is tab order. A natively disabled control is removed from the tab order entirely: keyboard users cannot reach it, screen readers skip past it, and its state is never announced. The user has no way to discover that the control exists, let alone why it is unavailable. An `aria-disabled="true"` control stays focusable, announces "disabled", and can carry a tooltip explaining what to do about it.

```css
.btn[aria-disabled="true"] {
  cursor: not-allowed;
  opacity: var(--btn-disabled-opacity, 0.6);
}
```

Styling `:disabled` is also a signal that the markup is wrong. If a rule needs `:disabled`, fix the element to use `aria-disabled="true"` (and guard its handler) instead of adding the selector.

---

## `:focus-visible`, not `:focus`

`:focus` matches on a mouse click as well as on keyboard focus. Authors see a ring appear after clicking a button, decide it looks like a bug, and write `:focus { outline: none; }` — which deletes the ring for keyboard users too and breaks navigation for everyone who does not use a pointer.

`:focus-visible` matches only when the browser decides a focus indicator is warranted — keyboard navigation, and pointer focus on text inputs. It removes the reason authors delete rings in the first place.

**Emit `:focus-visible` for every interactive element.** Never emit `outline: none` without an accompanying visible replacement.

```css
.btn:focus-visible {
  outline: 2px solid var(--focus-ring-color, #1a73e8);
  outline-offset: 2px;
}
```

If a design genuinely needs a ring on both pointer and keyboard focus, use `:focus-visible` for the primary rule and add `:focus` deliberately — do not use `:focus` alone as the default.

---

## `:empty` counts whitespace as content

`:empty` matches an element with **no child nodes at all** — no elements, and no text nodes. A single space or newline between the tags is a text node, so this does not match:

```css
.alert:empty {
  display: none;
}
```

An element written as `<div class="alert"> </div>`, or formatted across two lines by a template engine, has a whitespace text node and is not `:empty`. Comments are ignored, so `<div><!-- x --></div>` still matches.

Consequence: `:empty` is unreliable for hiding server-rendered or template-generated containers, because the formatter decides the outcome. Prefer a state attribute or class the template controls explicitly, and use `:empty` only where the markup is generated with no whitespace between the tags.

---

## `:placeholder-shown`

`:placeholder-shown` matches an input whose placeholder text is currently visible — i.e. the field is empty and a `placeholder` attribute is present. It is the selector behind floating-label patterns.

Two things it is not: it is not `:empty` (which never matches a replaced element like `<input>` in any useful way), and it is not `::placeholder` (the pseudo-element that styles the placeholder text itself).

```css
.field-input:not(:placeholder-shown) + .field-label {
  transform: translateY(-1.25rem);
  font-size: var(--field-label-sm, 0.75rem);
}

.field-input::placeholder {
  color: var(--field-placeholder-color, #6b7280);
}
```

An input with no `placeholder` attribute never matches `:placeholder-shown`, so a floating-label rule built on it silently does nothing. Placeholder text is not a label substitute — keep the real `<label>`.

---

## See also

- [modern-selectors.md](modern-selectors.md) — `:has()`, `:is()`/`:where()`/`:not()` specificity, native nesting
- [progressive-enhancement.md](progressive-enhancement.md) — `@supports` and user-preference media queries
