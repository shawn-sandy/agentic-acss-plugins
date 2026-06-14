---
status: proposal
type: design
created: 2026-06-14
repo-name: acss-plugins
---

# Investigation: can `COMPONENT.md` be framework-agnostic?

> Extends Workstream B of
> [`design-md-spec-alignment.md`](../plans/design-md-spec-alignment.md) and the
> spec plan [`component-md-spec.md`](../plans/component-md-spec.md). Question:
> can the `COMPONENT.md` format describe a component **once**, framework-neutral,
> such that an agent can generate it in **any** framework (React, HTML, Astro,
> Angular, Vue, Svelte, web components)? **Answer: yes** — and our own
> `reference.md` already contains the neutral contract for proof.

## TL;DR

A component is mostly framework-agnostic already. **Semantic HTML, CSS/design
tokens, and the accessibility contract are framework-neutral web primitives** —
only two things are framework-specific: **template syntax** and **reactivity /
state binding**. Our `button/reference.md` demonstrates this directly: its HTML
Template "mirrors the TSX output exactly — same root element, classes, `data-*`,
ARIA," and its CSS + Accessibility sections are identical regardless of target.

So `COMPONENT.md` becomes framework-agnostic by **inverting the hierarchy**:
promote the neutral contract (structure + props + tokens + a11y + behavior spec)
to the source of truth, and treat React/HTML/Astro/Angular/Vue/Svelte as
**render targets the agent projects into** — with the Vanilla-JS `init(root)`
already serving as the neutral reference behavior.

## Evidence from our own kit

`reference.md` already splits cleanly into neutral vs. React-specific sections:

| Section | Framework-agnostic? | Notes |
|---|---|---|
| Overview | ✅ | Purpose/semantics |
| **HTML Template** | ✅ | Semantic element tree + `data-*` + ARIA + slot comments — the neutral structural source |
| CSS Variables | ✅ | Pure custom properties |
| SCSS Template | ✅ | Pure CSS selectors (incl. `[data-*]` variant hooks, `[aria-disabled]` state) |
| **Accessibility** | ✅ | Keyboard, ARIA, focus, target size, WCAG criteria — 100% neutral |
| **Vanilla JS** (`init(root)`) | ✅ | Neutral reference *behavior* for static HTML |
| Generation Contract | ❌ | `export_name`, `file.tsx`, `imports` — React packaging |
| Props Interface | ⚠️ | TypeScript *type*; the *prop model* is neutral, the syntax is not |
| Key Patterns (`useDisabledState`) | ❌ | React hook — one realization of a neutral behavior |
| TSX Template | ❌ | JSX projection of the HTML structure |
| Usage Examples | ⚠️ | JSX today; trivially neutral as HTML |

**Coverage today:** the neutral HTML + Vanilla-JS layers already ship for 4
components (alert, button, card, dialog). The other 11 are React-only. So the
format *can* carry the neutral layer (proven), it just isn't universal yet.

## What is invariant vs. framework-specific

| Aspect | Invariant core | Framework-specific projection |
|---|---|---|
| **Structure** | Semantic element tree, `data-*` variant hooks, ARIA, slots | JSX vs HTML vs `.astro` vs Angular template vs Vue/Svelte SFC vs `<template>` |
| **Props / API** | Abstract prop table: name, values, required, default, **maps-to** (attribute/slot/aria) | TS interface (React/Angular), `@Input()` (Angular), `defineProps` (Vue), `export let` (Svelte), attributes (HTML) |
| **Styling** | CSS custom properties + selectors | None — CSS travels as-is everywhere |
| **Accessibility** | Roles, keyboard, focus, live regions, WCAG criteria | None — semantic HTML + ARIA is universal |
| **Tokens** | `{token.path}` → `--var` | None |
| **Behavior / state** | Behavior *spec* (events, state transitions, invariants) + neutral `init(root)` reference | React hook, Vue composable, Svelte action, Angular directive, signals |
| **Packaging** | — | export style, file extension, imports, compound assembly |

The neutral core is the **majority** of a component; only behavior-binding and
packaging genuinely vary. That asymmetry is what makes this tractable.

## The projection model (how an agent generates per framework)

Two viable strategies — not mutually exclusive:

### Strategy 1 — Agent-projected from the neutral contract (recommended)

The agent reads the neutral `COMPONENT.md` + the target framework and **generates
idiomatic code**: render the semantic structure in the target's template syntax,
type the abstract props per target, and realize the behavior spec in the target's
reactivity model (using the Vanilla-JS `init` as the reference semantics).
LLMs are strong at exactly this transform ("render this semantic HTML + behavior
as an idiomatic Angular component"). Optional `## Target: <framework>` blocks
carry *hints* (idioms, gotchas) or full templates where projection needs
steering; absent, the agent projects from the contract.

### Strategy 2 — Compile to a web component (universal runtime target)

`COMPONENT.md` → a **Custom Element** (vanilla or Lit) that *every* framework
consumes natively. One output, maximal reach. Trade-offs: web-component interop
is excellent in Angular/Vue/Svelte/Astro, historically awkward in React
(improving with React 19's native custom-element support), and has SSR/hydration
nuances. Best offered *alongside* Strategy 1 as a "universal" target, not the only
one.

**Recommendation:** Strategy 1 as the default (agent projection covers all named
frameworks today), with `web-component` available as one selectable target.

## Prior art (this is a known-solvable shape)

- **Mitosis (Builder.io)** — writes a component once and *compiles* to React,
  Vue, Angular, Svelte, Solid, Qwik, web components, HTML. Proves one-source →
  many-frameworks is viable; confirms the **hard seam is state/reactivity/
  lifecycle**, while structure and styling port cleanly. `COMPONENT.md` differs
  by being **agent-projected from semantic HTML**, not compiler-transpiled from
  JSX — lighter, and it leans on the LLM for idiom rather than a transform per
  target.
- **Stencil / Lit** — author once, ship **web components** usable in any
  framework (Strategy 2's precedent).
- **Web Components / Custom Elements** — the browser-level framework-agnostic
  component primitive; the universal runtime target.
- **ARIA Authoring Practices Guide (APG)** — the canonical proof that a
  component's **semantics, roles, and keyboard behavior are inherently
  framework-agnostic**; our Accessibility section already mirrors APG patterns.

## The hard parts (stated honestly)

- **Behavior / state / reactivity** is the lossy seam (same finding as Mitosis).
  Mitigation: express behavior as a **spec** (triggers, state transitions,
  invariants, ARIA effects) plus the **Vanilla-JS `init(root)` reference impl**;
  that's enough for an agent to realize idiomatically per framework. Pure
  presentational components (img, link, list) have *no* behavior and project
  trivially.
- **Props typing** — the abstract prop table must carry enough (value enums,
  required, default, maps-to) for the agent to emit a TS interface, Angular
  `@Input`s, Vue `defineProps`, or plain attributes.
- **Slots / children** — neutral concept (slot comments); maps to `children`
  (React), `<slot>` (web component/Vue/Svelte/Astro), `ng-content` (Angular).
- **Compound components** (`Card.Title`) — assembly differs per framework;
  the contract describes the part hierarchy, the agent projects the idiom.
- **Scoped vs global styling** — our CSS is global-by-design (custom properties +
  classes), which ports everywhere; component-scoped styling models (CSS Modules,
  Vue `scoped`, Svelte styles) are an *optional* per-target concern, not required.

## Proposed neutral `COMPONENT.md` structure

Front-matter (neutral):

```yaml
spec: component.md
version: alpha
name: button
element: button            # the semantic host element
role: button               # implicit/explicit ARIA role
tokens:                    # {token.path} into DESIGN.md primitives
  background: "{colors.primary}"
  rounded: "{rounded.md}"
props:                     # abstract — agent types per target
  type:    { values: [button, submit, reset], required: true }
  disabled:{ type: boolean, maps-to: "aria-disabled", a11y: "stays focusable" }
  size:    { values: [xs, sm, md, lg, xl, 2xl], maps-to: "data-btn" }
slots: [children]
variants: { outline: { maps-to: "data-style=outline" }, ... }
behavior: disabled-activation-guard     # ref to the behavior spec section
a11y: [2.1.1, 2.4.7, 2.5.8, 4.1.2]
targets: [react, html, astro, angular, vue, svelte, web-component]
```

Body (neutral sections): **Overview · Semantic Structure** (the HTML template,
canonical) **· Props · Tokens & CSS Variables · Styles** (CSS) **· Behavior**
(spec + Vanilla-JS reference) **· Accessibility · Examples** (neutral HTML).
Optional **`## Target: <framework>`** adapter blocks for idiom hints or
full templates.

## Implication for acss-kit (and the COMPONENT.md spec)

This **inverts** today's `reference.md`: the React TSX template becomes *one*
`## Target: react` adapter over the neutral contract, not the source of truth.
Concretely:

1. The neutral layers already exist for 4 components — **extract and normalize**
   them (HTML Structure, CSS, Accessibility, Vanilla-JS behavior) for all 15.
2. Add the **abstract props table** and **behavior spec** (the two pieces only
   implicitly present in the TS types + React hooks today).
3. Keep React as a first-class `## Target: react` block (so `/kit-add` output is
   unchanged for existing users).
4. `COMPONENT.md` (the `style-agent` spec) defines the neutral envelope + the
   `## Target:` extension mechanism; acss-kit's docs conform to it.

This is a larger reshape than the Workstream-B plan currently assumes (which
inherited the React-shaped 9 sections). The spec should be authored
**neutral-first** from the start to avoid a second migration.

## Resolved decisions (2026-06-14 review)

1. **Projection strategy: agent-projected + web-component target.** The agent
   projects the neutral contract idiomatically per framework (default), and
   `web-component` is offered as one selectable universal target.
2. **Neutral source of truth: semantic HTML template** (element tree + `data-*` +
   ARIA + slot comments) — pragmatic, agent-friendly, already present in 4
   components. (Not an abstract AST.)
3. **Per-target adapter blocks: hints only where projection is non-obvious** —
   stateful/compound components carry `## Target: <framework>` hints; purely
   presentational components rely on agent projection from the neutral contract.
4. **Officially supported targets: the broad set** — `react`, `html`, `astro`,
   `angular`, `vue`, `svelte`, `web-component`.
5. **Authoring order: neutral-first now.** Author `COMPONENT.md` neutral-first
   from the start; React becomes the first `## Target:` adapter. This re-scopes
   the Workstream-B plan ([`component-md-spec.md`](../plans/component-md-spec.md))
   — done in this pass.

## Next step

Fold this into the Workstream-B spec plan
([`component-md-spec.md`](../plans/component-md-spec.md)): re-scope it to author
the spec **neutral-first**, with the React projection as the first `## Target:`
adapter and the `paws-and-paths`/button example carried over. Resolve the five
decisions above before drafting the spec text.
