# Logical properties

Physical properties (`width`, `margin-left`, `top`) are pinned to the screen. Logical properties are pinned to the text: **inline** is the direction the text runs, **block** is the direction lines stack. In a default `writing-mode: horizontal-tb` with `direction: ltr` the two agree, which is why the difference is invisible until it is not.

The rationale is writing mode. Under `direction: rtl` or `writing-mode: vertical-rl`, a layout built from `margin-left` and `width` has to be rewritten selector by selector; the same layout built from `margin-inline-start` and `inline-size` flips itself. That covers RTL locales, vertical CJK typesetting, and any component dropped into a container that sets either.

| Physical | Logical |
|---|---|
| `width` | `inline-size` |
| `height` | `block-size` |
| `margin-left` / `margin-right` | `margin-inline-start` / `margin-inline-end` |
| `padding-top` / `padding-bottom` | `padding-block-start` / `padding-block-end` |
| `top` / `right` / `bottom` / `left` | `inset-block-start` / `inset-inline-end` / `inset-block-end` / `inset-inline-start` |
| `border-left` | `border-inline-start` |
| `text-align: left` | `text-align: start` |

---

## Shorthands

`margin-inline` and `padding-block` take one or two values — one applies to both ends, two apply start then end. `inset` is the four-sided shorthand for the positioning offsets and replaces the `top/right/bottom/left` block entirely.

```css
.prose {
  inline-size: min(65ch, 100%);
  margin-inline: auto;
  padding-block: 2rem 3rem;
}

.overlay {
  position: fixed;
  inset: 0;
}

.callout {
  border-inline-start: 4px solid currentColor;
  padding-inline-start: 1rem;
}
```

`margin-inline: auto` is the logical replacement for `margin: 0 auto` centring, and it is the one substitution that pays off immediately even in a single-locale project.

---

## Gotchas

- Logical and physical shorthands can fight: `margin: 0` after `margin-inline: auto` wins by order and resets it. Pick one family per rule.
- `inline-size` on a vertical writing mode is a height in pixels on screen. That is the point, not a bug.
- Sizing keywords still apply: `inline-size: fit-content` and `min-inline-size` behave exactly as their physical twins.
- `inset` only does anything on a positioned element (`relative`, `absolute`, `fixed`, `sticky`).
