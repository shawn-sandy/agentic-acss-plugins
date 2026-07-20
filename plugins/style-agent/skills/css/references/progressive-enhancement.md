# Progressive enhancement

Detect the new feature and enhance upward. Write the baseline rule unconditionally, then wrap the modern improvement in an `@supports` block that tests for the feature you actually want. Browsers without it keep the baseline; browsers with it get the upgrade. No feature test is needed for the fallback, because the fallback is the default.

```css
.gallery {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

@supports (display: grid) {
  .gallery {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr));
  }
}
```

**Anti-pattern — `@supports not`.** Negative detection (`@supports not (display: grid) { ... }`) inverts the model: the fallback becomes conditional, so any browser that understands neither `@supports` nor the tested property gets nothing at all. It also means every future browser evaluates a rule written for the past. Use it only for a genuinely one-directional workaround, never as the default shape.

---

## Motion

`prefers-reduced-motion: reduce` is a user request, not a preference to weigh. Define animation in the `no-preference` branch, or define it unconditionally and neutralise it in a `reduce` block. Do not remove the state change — remove the movement.

```css
.panel {
  transition: opacity 200ms ease;
}

@media (prefers-reduced-motion: reduce) {
  .panel {
    transition-duration: 1ms;
    animation: none;
  }
}
```

## Contrast

`prefers-contrast` has three useful values: `more`, `less`, and `custom`. Under `more`, raise border and outline weight and drop decorative translucency — do not simply swap to pure black on white, which can lose meaning encoded in colour.

```css
.card {
  border: 1px solid rgb(0 0 0 / 20%);
}

@media (prefers-contrast: more) {
  .card {
    border-width: 2px;
    border-color: currentColor;
  }
}
```

---

## Checklist

- Baseline first, `@supports` for the upgrade — never the reverse.
- Test the exact declaration you intend to use, including its value.
- `prefers-reduced-motion` removes motion, not functionality.
- `prefers-contrast: more` strengthens edges rather than flattening colour.
