# Viewport units

## `vh` versus `dvh` / `svh` / `lvh`

On mobile, browser chrome (URL bar, toolbar) shows and hides as the user scrolls, so there is no single viewport height. `vh` resolves against the **large** viewport — chrome retracted — which is why `height: 100vh` overflows on first paint and pushes a footer or a bottom action bar below the fold.

| Unit | Resolves against |
|---|---|
| `lvh` | Large viewport — browser chrome retracted. Same as `vh`. |
| `svh` | Small viewport — browser chrome fully shown. Always fits. |
| `dvh` | Dynamic — tracks the live viewport, changes as chrome moves. |

`dvh` is the right default for a full-height layout. `svh` is the safe choice when the element must never be clipped even for a frame — a splash screen, or a modal that must show its action buttons. Avoid `dvh` on anything that animates or is `position: sticky`, since the value changes mid-scroll and can cause reflow jitter; use `svh` there.

Each has `vw` / `vi` / `vb` / `vmin` / `vmax` counterparts (`dvw`, `svmin`, and so on). Keep the old unit as a fallback for very old engines by declaring it first.

```css
.hero {
  min-height: 100vh;
  min-height: 100dvh;
}

.sheet {
  max-block-size: 100svh;
}
```

---

## `100vw` and the scrollbar

`100vw` is the width of the viewport **including** the classic scrollbar gutter. On a desktop browser with a visible scrollbar, an element at `width: 100vw` is roughly 15px wider than the content area, producing horizontal overflow and a second scrollbar. This is the single most common cause of a mysterious sideways scroll.

Use `100%` for a normal full-width block. Use `100dvw` when you genuinely need viewport width and can accept the same gutter caveat, or subtract the gutter explicitly.

```css
.full-bleed {
  inline-size: 100%;
}

.edge-to-edge {
  inline-size: calc(100vw - (100vw - 100%));
}
```

The `calc(100vw - (100vw - 100%))` trick resolves to the content width of the containing block, which is what "full width" almost always means. Reach for it only when the element is inside a constrained container and must break out.

---

## Checklist

- `vh` equals `lvh`, not `svh` — it is the tallest case, so it overflows.
- Prefer `dvh` for layout, `svh` for anything that must never clip or jitter.
- Declare a plain `vh` line first as the fallback.
- `100vw` includes the scrollbar. Default to `100%`.
