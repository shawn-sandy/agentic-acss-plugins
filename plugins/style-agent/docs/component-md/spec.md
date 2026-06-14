# COMPONENT.md specification

> **Status:** `alpha` — the format will change. Pin a commit SHA when depending on it.
>
> **Companion to [DESIGN.md](https://github.com/google-labs-code/design.md).**
> DESIGN.md describes a *visual identity* (tokens) that agents consume to build
> UIs. **COMPONENT.md describes a *component implementation*** — structure,
> props, behavior, and accessibility — that agents consume to **generate that
> component in any framework**, themed by a sibling DESIGN.md. Together they form
> a two-file design system: **DESIGN.md owns tokens, COMPONENT.md owns
> components.**

## 1. Purpose & philosophy

A COMPONENT.md file is a **framework-neutral** description of a single UI
component. It combines machine-readable front-matter (the component's contract)
with a human-readable markdown body (the canonical structure, styles, behavior,
and accessibility). Both humans and coding agents read it.

The core observation: a component's **semantic structure (HTML), styling
(CSS + tokens), and accessibility contract are framework-agnostic web
primitives.** Only two things are framework-specific — **template syntax** and
**reactivity/state binding**. COMPONENT.md captures the neutral majority as the
source of truth, and an agent **projects** it into a target framework (React,
HTML, Astro, Angular, Vue, Svelte, or a web component), optionally guided by
per-target adapter blocks.

## 2. File format

A COMPONENT.md is bipartite, mirroring DESIGN.md:

1. **YAML front-matter** — the machine-readable contract, delimited by `---`
   fences at the top of the file.
2. **Markdown body** — the neutral source of truth (`##` sections), optionally
   followed by `## Target: <framework>` adapter blocks.

One file describes **one component**; the conventional filename is
`<name>.component.md`.

## 3. Front-matter schema

```yaml
---
spec: component.md          # required — format marker
version: alpha              # required — spec version this file targets
name: button                # required — component identifier (kebab-case)
element: button             # required — the semantic host element
role: button                # optional — explicit ARIA role (omit when implicit)
tokens:                     # optional — {token.path} refs into a sibling DESIGN.md
  background: "{colors.primary}"
  textColor: "{colors.on-primary}"
  rounded: "{rounded.md}"
  paddingBlock: "{spacing.sm}"
  paddingInline: "{spacing.md}"
  typography: "{typography.label-md}"
props:                      # abstract prop model — projected per target
  type:
    values: [button, submit, reset]
    required: true
  disabled:
    type: boolean
    maps-to: "aria-disabled"   # how the prop surfaces in the DOM
    a11y: "stays in tab order; blocks activation"
  size:
    values: [xs, sm, md, lg, xl, 2xl]
    maps-to: "data-btn"
slots: [children]           # named content slots (children = default slot)
variants:                   # named variant → DOM expression
  outline: { maps-to: "data-style=outline" }
  pill:    { maps-to: "data-style=pill" }
behavior: disabled-activation-guard   # ref to a Behavior section id, or omit
a11y: [1.4.11, 2.1.1, 2.4.7, 2.5.8, 4.1.2]   # WCAG criteria addressed
targets: [react, html, astro, angular, vue, svelte, web-component]
---
```

| Field | Required | Meaning |
|---|---|---|
| `spec` | ✅ | Always `component.md`. |
| `version` | ✅ | Spec version (`alpha`). |
| `name` | ✅ | kebab-case component id. |
| `element` | ✅ | Semantic host element the structure renders. |
| `role` | — | Explicit ARIA role; omit when the element implies it. |
| `tokens` | — | Map of design properties → `{token.path}` refs (primitive groups only — see §6). |
| `props` | — | Abstract prop model: `values` / `type` / `required` / `default` / `maps-to` / `a11y`. |
| `slots` | — | Content slots; `children` is the default. |
| `variants` | — | Named variants and how they surface (`maps-to`). |
| `behavior` | — | Id of a Behavior section, or omit for presentational components. |
| `a11y` | — | WCAG 2.2 criteria the component addresses. |
| `targets` | — | Frameworks this file claims conformance for. |

## 4. Body sections (the neutral source of truth)

Sections use `##` headings and should appear in this order. **Required** sections
are marked; a conformant file must carry them (stateful components also require
**Behavior**).

| Section | Required | Contents |
|---|---|---|
| Overview | — | One paragraph: purpose + key accessibility note. |
| **Semantic Structure** | ✅ | The canonical structure as **semantic HTML**: element tree, `data-*` variant hooks, ARIA, and slot placeholders (`<!-- slot: children -->`). This is what every target projects from. |
| Props | — | Human-readable table elaborating the front-matter `props`. |
| Tokens & CSS Variables | — | The component's CSS custom properties, each referencing a `{token.path}` or carrying a `var(--x, <fallback>)` default. |
| **Styles** | ✅ | The component's CSS (selectors, `[data-*]` variants, `[aria-disabled]`/state, `:focus-visible`). Framework-agnostic — travels as-is. |
| **Behavior** | ✅ if stateful | A behavior *spec* (triggers, state transitions, invariants, ARIA effects) **plus** a neutral reference implementation as a vanilla `init(root)` function. Omit for purely presentational components. |
| **Accessibility** | ✅ | Keyboard, ARIA & screen reader, focus management, target size, contrast, and the WCAG 2.2 AA criteria addressed. |
| Examples | — | Usage examples as neutral HTML. |

## 5. Target adapters (`## Target: <framework>`)

After the neutral body, a file MAY include one or more adapter blocks:

```markdown
## Target: react

generation: { export: Button, file: button.tsx, scss: button.scss, imports: "UI from '../ui'" }

<!-- the idiomatic React/TSX template + TS props -->
```

- An adapter supplies **idiom hints or a full template** for a specific target.
- **When an adapter is present**, a generator uses it directly (e.g. the `react`
  adapter carries the canonical TSX, a Generation Contract, and TS prop types).
- **When an adapter is absent**, the generator **projects from the neutral
  body**: render Semantic Structure in the target's template syntax, type the
  abstract `props` per target, and realize the Behavior spec in the target's
  reactivity model (using the `init(root)` reference as the semantics).
- `web-component` is a valid target — the universal runtime output every
  framework can consume.

**Adapter policy.** Presentational components (no `behavior`) project cleanly
with no adapters. Stateful/compound components SHOULD ship adapters for targets
where projection is non-obvious; a generator MAY project a stateful component
without an adapter but SHOULD warn that the behavior wiring needs review.

## 6. Token references

A `{token.path}` resolves against the project's sibling **DESIGN.md**, using
**primitive** groups only: `{colors.*}`, `{spacing.*}`, `{rounded.*}`,
`{typography.*}`. A COMPONENT.md MUST NOT reference DESIGN.md's `components.*`
map (those are freeform per-project and don't align 1:1 with a component
library).

When no DESIGN.md is present, the reference falls back to the embedded CSS
default — every generated custom property is written as `var(--x, <fallback>)`,
so a component renders correctly with or without a design system.

## 7. Consumer behavior

| Scenario | Behavior |
|---|---|
| Unknown body section | Preserve; do not error |
| Missing a **required** section | Error; reject the file |
| Duplicate section heading | Error; reject the file |
| Unknown front-matter key | Accept with warning |
| Unknown `## Target:` framework | Preserve; best-effort projection |
| `tokens` reference to `components.*` | Error (primitive groups only) |
| Reference to an undefined `{token.path}` | Use the CSS fallback; warn |

## 8. Relationship to DESIGN.md

- **DESIGN.md** supplies tokens (`colors`, `typography`, `spacing`, `rounded`).
- **COMPONENT.md** supplies components and references those tokens by primitive
  path. The two are **loosely coupled through the file format**, never through
  shared code or a shared component list.
- A generator resolves a component's `{token.path}` refs against whatever
  DESIGN.md the project provides, themes the component accordingly, and emits it
  in the requested target framework.

## 9. Versioning

The format is `alpha` and will change. Consumers should pin a commit SHA. Files
declare the version they target via front-matter `version:`.

---

A complete, conformant example lives at
[`examples/button.component.md`](examples/button.component.md).
