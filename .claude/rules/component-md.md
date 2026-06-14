---
paths:
  - "**/*.component.md"
  - "plugins/style-agent/docs/component-md/**"
---

# COMPONENT.md Conventions

When authoring or editing a `*.component.md` file (or the spec/examples under
`plugins/style-agent/docs/component-md/`), follow the spec at
[`plugins/style-agent/docs/component-md/spec.md`](../../plugins/style-agent/docs/component-md/spec.md):

- **Framework-neutral source of truth.** The body's `## Semantic Structure`
  (semantic HTML + `data-*` + ARIA + slot comments), `## Styles` (CSS),
  `## Behavior` (spec + neutral `init(root)`), and `## Accessibility` are the
  canonical, framework-agnostic description. Per-framework code goes in
  `## Target: <framework>` adapter blocks — never inline in the neutral body.
- **Required sections:** `Semantic Structure`, `Styles`, `Accessibility`, and
  `Behavior` (for stateful components). Missing a required section or a duplicate
  heading is an error.
- **Token references:** `{token.path}` resolves into a sibling DESIGN.md and uses
  **primitive groups only** — `{colors.*}`, `{spacing.*}`, `{rounded.*}`,
  `{typography.*}`. Never reference `components.*`. Every generated CSS custom
  property keeps a `var(--x, <fallback>)` default.
- **Targets:** declare supported frameworks in front-matter `targets:`. Absent a
  `## Target:` adapter, a generator projects from the neutral body.
