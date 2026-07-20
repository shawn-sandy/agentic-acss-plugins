# Responsive Text Reference

Fluid type with `clamp()` is the most-requested modern-CSS pattern and the easiest one to ship broken. The accessibility failure is invisible on a normal screen — it only appears when someone zooms.

---

## The gotcha: a pure-`vw` preferred term fails WCAG 1.4.4

WCAG 1.4.4 (Resize Text, Level AA) requires text to scale to 200% without loss of content or function. Browser zoom scales `rem` and `px`, but it does **not** scale viewport units — `vw` is measured against the viewport, and zooming does not change how wide the viewport is in `vw` terms.

So this fails:

```css
.headline {
  font-size: clamp(1.5rem, 4vw, 3rem);
}
```

At any viewport where `4vw` sits between the two bounds, the text is pinned to the viewport and a user at 200% zoom gets no size increase at all.

The fix is a `rem` addend in the preferred term, so part of the size always responds to zoom:

```css
.headline {
  font-size: clamp(1rem, 0.75rem + 1.5vw, 2rem);
}
```

Rules of thumb:

- The middle term of `clamp()` must always be `<rem value> + <vw value>`, never viewport units alone.
- Keep the `rem` part meaningful — roughly half the range or more. A token `0.05rem + 3.9vw` technically passes a grep and still fails real users.
- Both bounds are already in `rem`, so they zoom correctly; only the preferred term needs care.
- Test by zooming the browser to 200% and confirming the text actually grew.

---

## Worked slope formula

Pick two anchor points: a minimum font size at a minimum viewport width, and a maximum font size at a maximum viewport width. Convert every length to `rem` first (divide px by 16).

Target: **1rem at 320px (20rem)** growing to **2rem at 1280px (80rem)**.

1. Slope — how much the font grows per unit of viewport growth:
   `slope = (fontMax - fontMin) / (viewMax - viewMin)`
   `slope = (2 - 1) / (80 - 20) = 0.016667`

2. Viewport coefficient — the slope expressed as a percentage of the viewport:
   `vw = slope * 100 = 1.6667vw`

3. Intercept — the fixed `rem` addend that makes the line pass through the minimum anchor:
   `intercept = fontMin - (slope * viewMin)`
   `intercept = 1 - (0.016667 * 20) = 0.6667rem`

4. Assemble, clamping at the anchors:

```css
.headline {
  font-size: clamp(1rem, 0.6667rem + 1.6667vw, 2rem);
}
```

Sanity-check the endpoints: at a 20rem viewport, `0.6667 + (0.016667 * 20) = 1rem`; at 80rem, `0.6667 + 1.3333 = 2rem`. If the intercept comes out negative, the anchors are too far apart — raise the minimum font size or narrow the viewport range.

A container-relative variant swaps `vw` for `cqi` and needs a registered container on the parent; see [container-queries.md](container-queries.md).

```css
.card-slot {
  container-type: inline-size;
}

.card__title {
  font-size: clamp(1rem, 0.85rem + 2cqi, 1.75rem);
}
```

---

## Line length and line height

Fluid size without a bounded measure just produces very long lines on wide screens.

```css
.prose {
  max-inline-size: 65ch;
  font-size: clamp(1rem, 0.95rem + 0.25vw, 1.125rem);
  line-height: 1.5;
}
```

Keep `line-height` unitless so it scales with the computed font size rather than inheriting a fixed length.

---

## `text-wrap: balance` and `pretty`

Both fix ragged line breaks, and they are not interchangeable.

| Value | What it does | Use on |
|---|---|---|
| `balance` | Evens line lengths across the whole block | Short blocks: headings, pull quotes, card titles, labels |
| `pretty` | Leaves line lengths alone but avoids orphans and bad last-line breaks | Body copy, paragraphs, long descriptions |

```css
h1,
h2,
h3,
.card__title {
  text-wrap: balance;
}

p,
.prose {
  text-wrap: pretty;
}
```

Constraints worth knowing:

- `balance` is capped at a small number of lines (browsers stop around four to six) and does nothing beyond that — it is not a body-copy tool.
- `pretty` costs more layout work than `balance` on long text, but is applied lazily and is safe on ordinary page copy.
- Both degrade silently to normal wrapping where unsupported, so no `@supports` guard is needed.
- Neither affects the text's accessible content — they change line breaking only.

---

## Checklist

- Every `clamp()` preferred term has a `rem` addend.
- Bounds are in `rem`, not `px`.
- Zoomed to 200%, the text visibly grows.
- Long-form text has a `max-inline-size` in `ch`.
- `balance` on headings, `pretty` on paragraphs.
