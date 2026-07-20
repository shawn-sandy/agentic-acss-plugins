# Modern selectors

## `:has()`

The parent selector. It matches the element on the left when the relative selector inside it matches, so specificity and the styled element stay on the left-hand side.

```css
.card:has(> img) {
  padding-block-start: 0;
}

.field:has(input:focus-visible) {
  outline: 2px solid currentColor;
}
```

**Restriction: no pseudo-elements.** `:has()` cannot contain a pseudo-element — `.card:has(::before)` is invalid and invalidates the whole rule. It also cannot be nested inside another `:has()`, and it cannot contain `::part()` or `::slotted()`. Pseudo-*classes* are fine; pseudo-*elements* are not.

---

## `:is()`, `:where()`, and `:not()` specificity

This is the part that is misremembered. `:is()` takes the **highest** specificity of its argument list — so `:is(a, #id)` costs a whole ID, even on the `a` match. `:where()` is identical in matching behaviour but contributes **zero** specificity, always, no matter what is inside it. That makes `:where()` the correct wrapper for defaults a consumer must be able to override with a single class.

`:not()` shares the same rule as `:is()`: in its multi-argument form it takes the highest specificity of its argument list, so `:not(.a, #b)` costs an ID. `:not()` also matches far wider than authors expect — `:not(.promo)` matches `html`, `body`, every wrapper, and every text-bearing element that is not `.promo`, so it inherits down the tree and paints things you never intended. Anchor it to a tag or class, and prefer scoping it to a child combinator over letting it float.

```css
:where(button, [type="button"]) {
  border-radius: 0.25rem;
}

.nav :is(a, button):hover {
  text-decoration: underline;
}

.list > li:not(:last-child) {
  border-block-end: 1px solid;
}
```

---

## `:nth-child(An+B of S)`

The `of S` clause filters the sibling set **before** counting, which is not the same as `:nth-child(An+B).class`. `li:nth-child(2n of .featured)` selects every second featured item; `li:nth-child(2n).featured` selects items in even sibling positions that happen to be featured.

```css
.row:nth-child(odd of :not([hidden])) {
  background-color: rgb(0 0 0 / 4%);
}
```

---

## Native CSS nesting

Nesting is now native. The `&` is a real selector that stands for the enclosing rule's selector list, and this is where it diverges from SCSS: SCSS's `&` is a *string concatenation* token, so `&-title` compiles to `.card-title`. Native CSS `&` is not string-based, so `&-title` is invalid and will not produce a compound class name. Native `&` is also equivalent to `:is(<parent selector list>)`, meaning it inherits the highest specificity of that list — a detail SCSS's textual expansion does not have.

A bare element or class selector nested without `&` is treated as a descendant, the same as SCSS. Use `&` explicitly when attaching a pseudo-class or compound.

```css
.card {
  padding: 1rem;

  & .title {
    font-weight: 600;
  }

  &:hover {
    background-color: rgb(0 0 0 / 4%);
  }

  @media (width >= 40rem) {
    padding: 2rem;
  }
}
```

---

## Checklist

- `:has()` styles the left-hand element and rejects pseudo-elements.
- `:where()` is zero specificity; `:is()` and multi-argument `:not()` take the highest of their list.
- Anchor `:not()` — unanchored, it matches nearly the whole document.
- `of S` filters before counting.
- Native `&` is a selector, not SCSS string concatenation — no `&-suffix`.
