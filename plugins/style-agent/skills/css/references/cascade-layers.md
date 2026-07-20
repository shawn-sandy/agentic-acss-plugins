# Cascade Layers Reference

`@layer` lets low-specificity author styles beat high-specificity ones by ordering the cascade explicitly. Most first attempts appear to do nothing, and the reason is always the same rule below.

---

## The gotcha: unlayered styles win

**Any normal author declaration written outside a layer outranks every normal author declaration written inside one**, no matter the layer order and no matter the specificity. Unlayered author styles are treated as a final, implicit layer that sits above all declared layers. (`!important` inverts this — see below.)

So a plain `.btn { color: red; }` sitting anywhere in the stylesheet beats `@layer components { .btn { color: blue; } }` — even though `components` was declared last, and even if the layered selector is far more specific.

```css
@layer base, components;

@layer components {
  .btn {
    color: blue;
  }
}

.btn {
  color: red;
}
```

The button is red. This is the single most common cause of "my `@layer` refactor changed nothing" — a partially migrated stylesheet leaves the old rules unlayered, so they keep winning.

Fix it by moving everything into a layer. If some styles genuinely must always win, leave *only* those unlayered and say so in a comment.

---

## Declare the order first, once, at the top

Layer order is fixed by first appearance. A bare `@layer` statement at the top of the entry stylesheet declares the whole order up front, before any layer has content — so the order no longer depends on import sequence or file ordering.

```css
@layer reset, third-party, base, components, utilities;
```

Later layers win over earlier ones. Read that line as a priority ladder: `utilities` beats `components`, which beats `base`.

Rules to hold to:

- Put the order statement in the entry stylesheet, above every `@import` and every rule.
- Never re-declare the order later in a different sequence — the first declaration is authoritative and the second is ignored for ordering.
- Adding a layer name that never gets rules is harmless; it just reserves a slot.
- An unnamed `@layer { … }` block creates a new anonymous layer at that point that nothing else can add to. Prefer named layers.

---

## Where third-party CSS belongs

Vendor stylesheets are the reason layers exist: they ship high-specificity selectors you cannot edit. Import them into a low-priority layer and your own low-specificity rules will beat them.

```css
@layer reset, third-party, base, components, utilities;

@import url("normalize.css") layer(reset);
@import url("vendor-datepicker.css") layer(third-party);

@layer components {
  .datepicker__day {
    border-radius: 0.25rem;
  }
}
```

A single-class rule in `components` now overrides `.dp .dp__calendar td.dp__day` from the vendor bundle, with no `!important` and no specificity arms race.

If the vendor CSS is loaded via a `<link>` rather than `@import`, wrap it at the build step or re-emit it inside `@layer third-party { … }` — a `<link>`ed stylesheet cannot be assigned a layer from CSS.

---

## `!important` inverts layer order

`!important` does not just raise a declaration's priority — it flips the layer ladder for important declarations. Among `!important` declarations, **earlier layers win**, and important declarations in *unlayered* styles rank below important declarations in *any* layer.

```css
@layer reset, components, utilities;

@layer reset {
  .btn {
    color: green !important;
  }
}

@layer utilities {
  .btn {
    color: orange !important;
  }
}
```

The button is green. `reset` is the weakest layer for normal declarations and therefore the strongest for important ones.

Practical consequences:

- Do not reach for `!important` to escape a layer problem; it lands you in a second, reversed ordering you now have to reason about.
- A reset or third-party layer full of `!important` becomes unoverridable by design — check vendor CSS for this before layering it low.
- Keep `!important` for genuine escape hatches (print overrides, forced states), not for routine specificity fixes.

---

## Nested layers

Layers nest with `.` notation, and each parent orders its children independently.

```css
@layer components {
  @layer base, variants;
}

@layer components.variants {
  .btn--ghost {
    background: transparent;
  }
}
```

`components.variants` beats `components.base`, and both still lose to `utilities`.

---

## Related

Layer order decides which rule wins when the same selector appears in more than one layer — including selectors inside `@container` blocks, which contribute no specificity of their own. See [container-queries.md](container-queries.md) when a container query resolves correctly but its styles never paint.
