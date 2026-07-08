# /create-utilities — Usage Guide

Turn a plain-language description of visual intent into a ready-to-use utility class string. The command detects which utility library your project uses (acss-kit, Tailwind, Bootstrap, or a Tailwind-compatible fallback) and maps your description to the matching class names, then prints the class string and a one-line HTML example.

## When to use it

- You know what you want visually ("centered flex row, 1rem gap, primary background") but not the exact class names.
- You want class names that match the framework already in your project, without looking them up.
- You are scaffolding an element and want a sensible starting class list, focus styling included for interactive elements.
- You plan to consolidate the result into a named class afterward with `/css-to-class`.

## How to run it

```text
/create-utilities [description]
```

Then supply the intent as input:

| Input form | Example |
|---|---|
| Plain description | `"a card with white background, 1rem padding, subtle shadow, and rounded corners"` |
| Component phrase | `"primary submit button with hover state"` |
| HTML element with intent | `<div> <!-- make this a centered hero section -->` |

- If the description is too vague ("make it look nice"), the command asks a focused follow-up before generating.

## Example

Input:

```text
a centered flex row with 1rem gap and a primary background
```

Output — a class string plus a one-line HTML example (Tailwind / fallback vocabulary shown; `focus-visible:ring` is added automatically for interactive elements):

```text
flex items-center gap-4 bg-primary focus-visible:ring
```

```html
<button class="flex items-center gap-4 bg-primary focus-visible:ring">Label</button>
```

## Notes

- Framework detection drives the vocabulary: acss-kit (`utilities.css` with `.bg-primary`), Tailwind (`tailwind.config.*` or `@tailwind base`), Bootstrap (`bootstrap*.css` or `d-flex`/`btn`), else a Tailwind-compatible fallback. If more than one framework is detected, you are asked which to use.
- Classes are ordered layout → spacing → color → typography → border/radius → shadow → state.
- Focus styling for interactive elements (button/link/input): `focus-visible:ring` for Tailwind/fallback, `focus-ring` for Bootstrap. For acss-kit the bundle ships no focus utility, so the summary warns and suggests adding `:focus-visible` CSS or using an acss-kit component class.
- Emits classes only — it does not write to your stylesheet.
- Chains naturally into `/css-to-class [name]` to consolidate the string into a single named class.

## Related

- [/css-to-class](css-to-class.md) — consolidate the generated class string into one named class
- [/inline-style-to-class](inline-style-to-class.md) — convert inline styles or a JSX style object into a named class
- [Command index](README.md) · [Developer guide](../README.md)
