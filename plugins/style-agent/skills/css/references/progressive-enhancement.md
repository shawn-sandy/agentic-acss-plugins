# Progressive enhancement

## What "baseline" means here

[Baseline](https://web.dev/baseline) is the W3C WebDX Community Group's status for a web feature across the core browser set — Chrome, Edge, Firefox, and Safari, desktop and mobile. Three states:

| Status | Meaning | Emit it how? |
|---|---|---|
| **Widely available** | Interoperable for at least 30 months | Unconditionally. No `@supports`, no fallback. |
| **Newly available** | Just landed in all four | Inside `@supports`, with a real fallback below it. |
| **Limited availability** | Not interoperable yet | Don't. Emit the fallback alone and say why. |

The 30-month gap between Newly and Widely is the point: it is the lag for users on old phones and locked-down enterprise browsers. A feature being "in every browser" and being safe to ship unconditionally are two different dates.

**Check status, don't recall it.** Baseline dates move — the Popover API was [announced as Newly available in April 2024, then corrected to January 2025](https://web.dev/blog/popover-baseline). Look a feature up at [webstatus.dev](https://webstatus.dev) rather than trusting a remembered date, and never write a status table into a doc where it will quietly rot.

A project can pin this as a build target with one Browserslist line, which every tool reading Browserslist then inherits:

```
# .browserslistrc
baseline widely available
```

See [Use Baseline with Browserslist](https://web.dev/articles/use-baseline-with-browserslist).

---

## Enhancing upward

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

- Widely available → emit unconditionally. Newly available → `@supports` with a fallback. Limited → don't emit.
- Baseline first, `@supports` for the upgrade — never the reverse.
- Test the exact declaration you intend to use, including its value.
- `prefers-reduced-motion` removes motion, not functionality.
- `prefers-contrast: more` strengthens edges rather than flattening colour.
