# /css — Usage Guide

Turn a plain-language description into a CSS/SCSS rule or an inline `style` attribute, reusing your project's existing custom properties when they match. The command greps your project for custom-property declarations before mapping relative words like "small", consults bundled references for modern-CSS features with known footguns (`@container`, `@layer`, `clamp()` fluid type, `@supports`, logical properties, modern selectors, state selectors, viewport units), then prints the rule with a summary naming which references it consulted.

## When to use it

- You know the effect you want ("a card that adapts to the width of its slot") but not the correct modern-CSS incantation.
- You want a rule that uses the design tokens your project already declares, rather than hard-coded literals.
- You are reaching for `@container`, `@layer`, fluid type, logical properties, or state selectors and want the gotchas handled — `container-type` on the parent, unlayered styles outranking layered ones, a `rem` addend in `clamp()` for WCAG 1.4.4, `:user-invalid` over `:invalid`.
- You want a raw CSS rule. If you want a utility-class string instead, use `/create-utilities`.

## How to run it

```text
/css [description]
```

Then supply the intent as input:

| Input form | Example |
|---|---|
| Plain description | `"a flex row aligned centered with a small gap"` |
| Inline request | `"inline: a card with 1rem padding and a subtle shadow"` |
| Modern-CSS intent | `"a card that adapts to the width of its slot"` |

- If the description is too vague ("make it look nice"), if a size word maps equally to two adjacent scale steps, if an interactive element does not say which states it wants, or if adaptive sizing does not say container-versus-viewport, the command asks — every triggered question batched into a single round. A concrete, fully-specified description is emitted with no questions at all.

## Example

Input:

```text
a flex row aligned centered with a small gap
```

Output — a CSS rule using the variables your project already declares (here `--space-2: 0.5rem` matched, so the gap resolves to `var(--space-2)`; with no matching variable it emits the `0.5rem` literal):

```css
.flex-row-center {
  display: flex;
  align-items: center;
  gap: var(--space-2, 0.5rem);
}
```

The summary names the token choice, the proposed class name, and which references were consulted (or states none), then closes with two or three concrete refinement offers drawn from what was emitted.

## Notes

- **Class mode prints by default.** The rule is appended to a stylesheet only when you name a target file, and the resolved target path and class name are confirmed with you before anything is written. On a same-name-different-value collision the class name gets a numeric suffix (`-2`, `-3`), reported in the summary.
- **SCSS vs. plain CSS** is inferred from your project's stylesheet extensions; no stylesheet at all means plain CSS.
- **Inline mode** fires when you say `inline` or point at an element. It is refused with a one-line reason — falling back to class mode — when the description implies `:hover`, `:focus-visible`, `@media`, `@container`, `@layer`, `@supports`, or a pseudo-element, since an inline style cannot carry any of those.
- **Interactive elements** (button, link, input, select, custom widgets) get a `:focus-visible` rule alongside the requested styling, or a summary warning when the output mode cannot carry one.
- **Tokens are reused, never invented.** An exact-value match uses the variable; a semantic-name match uses it and names the choice in the summary; no match emits the literal. No new custom property is created unless you explicitly ask — the inverse of `/inline-style-to-class`, where the value is already committed.

## Related

- [/create-utilities](create-utilities.md) — the utility-class-string counterpart when your project uses a utility framework
- [/inline-style-to-class](inline-style-to-class.md) — promote a `/css inline` result into a named class
- [/css-to-class](css-to-class.md) — collapse an existing utility class list into one named class
- [Command index](README.md) · [Developer guide](../README.md)
