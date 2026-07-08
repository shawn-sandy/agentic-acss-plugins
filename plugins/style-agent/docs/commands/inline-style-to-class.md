# /inline-style-to-class — Usage Guide

Convert an inline `style` attribute, a JSX `style={{ ... }}` object, or a `<style>` block into a single, semantically named CSS class and append it to your project stylesheet. Hard-coded colors, units, and values are replaced with CSS variables — reusing an existing variable when one already holds that value, and creating a new one when none does. The inverse of `/css-to-class`.

## When to use it

- You have inline styles or a JSX style object and want a reusable, tokenized CSS class instead.
- You want hard-coded literals (`#2563eb`, `1rem`) swapped for `var(...)` references that reuse your existing design tokens.
- You are migrating a `<style>` block's rule into your main stylesheet.
- You selected an element in your IDE and want the style lifted out and the class wired in-place.

## How to run it

```text
/inline-style-to-class [name]
```

Then provide one of these as input:

| Input form | Example |
|---|---|
| IDE selection | Select an element/style block in your editor, then run the command |
| HTML inline attribute | `<div style="background: #2563eb; padding: 1rem">` |
| JSX style object | `<Button style={{ backgroundColor: theme.primary, padding: 8 }}>` |
| `<style>` block | `<style>.hero { color: red; padding: 2rem; }</style>` |

- `name` is optional. Provide it to set the class name; omit it to auto-generate from the element tag and first declared property (e.g. `div-bg`, `btn-pad`).
- Name rules: max 20 characters, kebab-case (`[a-z][a-z0-9-]*`). Non-conforming names are coerced and you are warned.

## Example

Input:

```html
<div style="background: #2563eb; padding: 1rem">
```

Output — a tokenized class appended to your stylesheet (here `#2563eb` matched an existing `--color-primary`; `1rem` had no match, so `--space-1rem` was created), plus the refactored HTML:

```css
/* from: style attr on <div> */
.div-bg {
  background: var(--color-primary, #2563eb);
  padding: var(--space-1rem, 1rem);
}
```

```html
<div class="div-bg">
```

## Notes

- Appends the class to a stylesheet detected from your project's own conventions — plain CSS, SCSS, or Sass-indented syntax. If no stylesheet is found, the class is emitted to chat only.
- Reuse-or-create tokens: an existing custom property is referenced when its value matches; otherwise a new variable is declared in your tokens/variables file, an existing `:root` block, or a new `:root` block. Matching is exact on the normalised value — no color-format or unit conversion (`16px` never matches `1rem`).
- The original literal is always kept as the `var()` fallback, so the class still renders if the variable is absent.
- Values already written as `var(...)` pass through untouched; unresolved JSX expressions become `/* unresolved */` placeholders.
- IDE selection enables in-place editing — the `style` attribute is removed and the `class` added directly in your source file (falls back to emitting refactored source in chat when the edit would be ambiguous).
- Other attributes (`data-*`, `id`, `aria-*`) are preserved; the new class is appended to any existing `class`/`className`.

## Related

- [/css-to-class](css-to-class.md) — collapse a utility class list into one named class (the inverse)
- [/create-utilities](create-utilities.md) — generate a utility class string from a plain-language description
- [Command index](README.md) · [Developer guide](../README.md)
