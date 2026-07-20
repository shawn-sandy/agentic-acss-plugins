# Container Queries Reference

Size a component from the width of the box it sits in, not the width of the viewport. The failure mode is silent: get one declaration wrong and the `@container` block simply never matches, with no error anywhere.

---

## The gotcha: `container-type` goes on the parent

A `@container` query resolves against the nearest **ancestor** that has been declared a container. Declare `container-type` on the element you are styling and nothing happens — an element cannot query itself.

```css
.card-slot {
  container-type: inline-size;
}

@container (min-width: 30rem) {
  .card {
    display: grid;
    grid-template-columns: 12rem 1fr;
  }
}
```

The parent (`.card-slot`) is the container. The child (`.card`) is what the query styles. Reverse them and the rule is dead code.

| Value | Queries you can write | Notes |
|---|---|---|
| `inline-size` | inline (width) only | The default choice. Only the inline axis is size-contained. |
| `size` | inline and block | Requires the container to have an explicit block size, or it collapses. |
| `normal` | style queries only | No size containment; the element is still a `container-name` target. |

Prefer `inline-size`. `size` contains the block axis too, so a container whose height comes from its content collapses to zero.

---

## Container units are not viewport units

| Unit | Relative to |
|---|---|
| `cqi` | 1% of the container's **inline** size |
| `cqb` | 1% of the container's **block** size |
| `cqw` / `cqh` | 1% of the container's width / height |
| `cqmin` / `cqmax` | the smaller / larger of `cqi` and `cqb` |
| `vw` / `vh` | 1% of the **viewport**, regardless of container |

Inside a container, `cqi` tracks the slot; `vw` still tracks the window. A component placed in a 300px sidebar and again in a 900px main column behaves identically under `vw` and correctly under `cqi`.

```css
.card-slot {
  container-type: inline-size;
}

.card__title {
  font-size: clamp(1rem, 0.85rem + 2cqi, 1.75rem);
}
```

Container units only resolve against a registered container. With no `container-type` ancestor they fall back to the small viewport size — another silent wrong answer. See [responsive-text.md](responsive-text.md) for why the `clamp()` middle term keeps a `rem` addend.

---

## Naming containers for nesting

When containers nest, an unnamed `@container` query binds to the *nearest* container ancestor, which is rarely the one you meant. Name them and target explicitly.

```css
.layout {
  container-type: inline-size;
  container-name: layout;
}

.card-slot {
  container-type: inline-size;
  container-name: card;
}

@container card (min-width: 30rem) {
  .card {
    grid-template-columns: 12rem 1fr;
  }
}

@container layout (min-width: 64rem) {
  .card {
    padding: 2rem;
  }
}
```

The `container` shorthand writes both: `container: card / inline-size;` (name first, type after the slash).

---

## Minimal correct template

Copy this shape whenever a component should adapt to its slot.

```css
.component-wrapper {
  container: component / inline-size;
}

.component {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

@container component (min-width: 28rem) {
  .component {
    flex-direction: row;
    align-items: center;
  }
}
```

Checklist before shipping:

- The `container-type` declaration is on an ancestor, never on the queried element.
- The container is not `display: contents` — that removes the box the query measures.
- Query conditions use lengths (`min-width`), not media features like `min-resolution`.
- Any `cqi`/`cqb` usage sits inside a registered container.

---

## Interaction with cascade layers

A `@container` block carries the specificity of the selectors inside it — the at-rule adds none. When container-scoped rules land in a different `@layer` than the base rules they are meant to override, layer order decides the winner and the query appears to do nothing. See [cascade-layers.md](cascade-layers.md), especially the rule that unlayered styles outrank every layered one.
