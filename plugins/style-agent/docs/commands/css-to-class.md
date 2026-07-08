# /css-to-class — Usage Guide

Collapse a multi-class HTML element (or a bare class string) into a single, semantically named CSS class. Each utility token is resolved to its real property/value declarations by grepping the `.css` files already in your project, so the output works with plain CSS, compiled SCSS, Tailwind, or any utility-first setup.

## When to use it

- An element has grown a long "utility soup" `class="..."` list and you want one semantic selector instead.
- You need a reusable named class (e.g. `.testimonial-grid`) that inlines the declarations those utilities produced.
- You are consolidating the output of `/create-utilities` into a committed class.
- You want to see which tokens are project-defined vs. undefined (unresolved tokens are flagged for manual follow-up).

## How to run it

```text
/css-to-class [name]
```

Then paste one of these as input:

| Input form | Example |
|---|---|
| HTML element | `<div class="testimonial flex-grid py-8 items-center" data-flex-grid>` |
| Plain class list | `testimonial flex-grid py-8 items-center` |
| Quoted string | `"flex py-4 items-center justify-between"` |

- `name` is optional. Provide it to set the class name; omit it to auto-generate from the most semantic tokens.
- Name rules: max 20 characters, kebab-case (`[a-z][a-z0-9-]*`). Non-conforming names are coerced and you are warned.

## Example

Input:

```html
<div class="testimonial flex-grid py-8 items-center" data-flex-grid>
```

Output — a named class with declarations resolved from your project CSS (`py-8` and `items-center` matched; `testimonial` and `flex-grid` were not found in any project CSS file, so they remain manual placeholders), plus the refactored HTML:

```css
/* extracted: testimonial flex-grid py-8 items-center */
.testimonial-grid {
  /* testimonial: add declarations manually */
  /* flex-grid: add declarations manually */
  padding-block: 2rem;
  align-items: center;
}
```

```html
<div class="testimonial-grid" data-flex-grid>
```

## Notes

- Framework-agnostic — resolves tokens by grepping `.css` files in your project (`node_modules`, `.git`, `dist`, `build` excluded); SCSS is supported via its compiled output.
- Read-only lookup: it does not write to your stylesheet. Copy the emitted class block into your CSS yourself.
- Declarations found inside an at-rule (`@media`, `@supports`, `@layer`) keep their wrapper as a nested block so they still apply at the intended breakpoint or query.
- Unresolved tokens (custom/semantic classes not in any `.css` file) are preserved in place as `/* <token>: add declarations manually */` comments.
- Other attributes on the element (`data-*`, `id`, `aria-*`) are preserved untouched; only the `class` value is rewritten.
- The inverse operation is `/inline-style-to-class`.

## Related

- [/inline-style-to-class](inline-style-to-class.md) — convert inline styles or a JSX style object into a named class
- [/create-utilities](create-utilities.md) — generate a utility class string from a plain-language description
- [Command index](README.md) · [Developer guide](../README.md)
