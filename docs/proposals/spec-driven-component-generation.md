---
status: proposal
type: feature
created: 2026-06-14
repo-name: acss-plugins
---

# Proposal: spec-driven component generation (`/kit-add` evolved)

> A skill that consumes **COMPONENT.md** (the neutral component spec) and
> **DESIGN.md** (the token/design system) to generate acss-kit library
> components **into any target framework** (React, HTML, Astro, Angular, Vue,
> Svelte, web-component), with brand tokens resolved from the project's
> DESIGN.md. This is the **consumer that closes the loop** of the two-file
> design system designed in
> [`design-md-spec-alignment.md`](../plans/design-md-spec-alignment.md) and
> [`component-md-framework-agnostic.md`](component-md-framework-agnostic.md).

## TL;DR

We don't need a greenfield skill — **`/kit-add` already is** a stack-aware,
multi-target, dependency-resolving component generator. It already detects the
project stack (`detect_stack.py`), already has a `--target` flag (`--target=html`
ships today), resolves dependency trees, and verifies integration. The proposal
is to **evolve its generation core** along two axes:

1. **Source:** read **COMPONENT.md** (neutral: semantic structure + abstract
   props + behavior spec + `## Target:` adapters) instead of the React-shaped
   `reference.md`. Project to the requested framework — use a `## Target:`
   adapter if present, else project from the neutral contract.
2. **Tokens:** become **DESIGN.md-aware** — resolve the COMPONENT.md's
   `{token.path}` references against the project's DESIGN.md (via the
   Workstream-A adapter + theme pipeline), falling back to the embedded
   `var(--x, <fallback>)` values when no DESIGN.md is present.

The result: `/kit-add button --target=angular --design=DESIGN.md` emits an
idiomatic Angular button, themed by the project's brand, accessible by contract.

## Context — what already exists

`/kit-add` (in `kit-core`) is further along than a blank slate:

- **Stack detection** — `detect_stack.py` classifies framework / bundler /
  cssPipeline / entrypoint into `.acss-target.json`; `detect_target.py` resolves
  the components dir.
- **A `--target` flag already exists** — `/kit-add --target=html` generates
  static-HTML versions of components whose `reference.md` carries a
  `## HTML Template` section; `/kit-list` marks those `[HTML]`. So **multi-target
  generation is already a nascent concept**, gated on which neutral sections a
  component doc carries.
- **Dependency resolution** — Step B reads each component's Generation Contract,
  walks deps bottom-up, skips existing files.
- **Integration verification** — `verify_integration.py` confirms the entrypoint
  imports what was written.

What's missing is exactly the two things this initiative is building: a
**neutral, multi-framework component spec** (COMPONENT.md) and a **token source**
(DESIGN.md). This skill is where they're consumed.

## Core finding

> This is the **payoff** of the whole DESIGN.md/COMPONENT.md effort: DESIGN.md
> supplies tokens, COMPONENT.md supplies components, and **this skill projects
> them into real, themed, accessible components in any framework.** It is an
> *evolution* of `/kit-add`, not a new skill — `--target=html` is the seed of
> exactly this generalization.

## The skill design

### Inputs

- **component(s)** — by name from the acss-kit library (or a path to a custom
  `*.component.md`).
- **`--target=<framework>`** — `react` (default today) → one of
  `react | html | astro | angular | vue | svelte | web-component`. Default:
  inferred from `detect_stack.py` (e.g. a Next project ⇒ `react`, an Astro
  project ⇒ `astro`), falling back to `react`.
- **`--design=<DESIGN.md>`** — optional. Else auto-detect a `DESIGN.md` at repo
  root; else use the existing generated theme; else the COMPONENT.md fallbacks.

### Pipeline

```
/kit-add <name> --target=<fw> [--design=DESIGN.md]
  │
  ├─ 1. Resolve design system
  │     DESIGN.md present? → validate_design_md.py → design_md_to_tokens.py
  │       → tokens_to_css.py (light/dark/space-radius/typography) → validate_theme.py
  │     else theme exists? → use it.   else → COMPONENT.md {token} fallbacks.
  │
  ├─ 2. Resolve COMPONENT.md  (acss-kit library, conforming to the style-agent spec)
  │     parse front-matter (props, tokens, slots, variants, behavior, targets)
  │     + neutral body (Semantic Structure, Styles, Behavior, Accessibility)
  │
  ├─ 3. Resolve tokens
  │     replace {token.path} in CSS vars/styles with concrete values
  │     from step 1 (or fallbacks)
  │
  ├─ 4. Project to <target>
  │     `## Target: <fw>` adapter present?  → use it (react = canonical TSX)
  │     else → project the neutral contract:
  │              structure → target template syntax
  │              abstract props → target prop model (TS iface / @Input / defineProps / attrs)
  │              behavior spec → target reactivity (hook / composable / action / directive),
  │                              using the neutral init(root) as reference semantics
  │     web-component = the universal target
  │
  ├─ 5. Emit  (reuse detect_target/detect_stack)
  │     component source + token-driven CSS, placed per project conventions;
  │     resolve component deps bottom-up; write theme files if DESIGN.md was used
  │
  └─ 6. Verify
        a11y contract checks where possible; verify_integration.py; summary
```

Steps 1, 5, 6 **reuse existing scripts** (`detect_stack.py`, `detect_target.py`,
`design_md_to_tokens.py` [Workstream A], `tokens_to_css.py`, `validate_theme.py`,
`verify_integration.py`). Steps 2–4 are the new spec-driven core.

## New skill vs. refactor — DECIDED: refactor

**Refactor `/kit-add` / `kit-core`'s generation core**, do not build a parallel
skill. Rationale: `/kit-add` already owns stack detection, `--target`, dep
resolution, and verification — a new skill would duplicate all of it. The change
is to swap the *source* (reference.md → COMPONENT.md) and add *token resolution*
(DESIGN.md), expanding the existing `--target` set.

Surface unchanged: `/kit-add <name> [--target=<fw>] [--design=...]`. The legacy
React path (`--target=react`, today's default) stays byte-identical via the
COMPONENT.md `## Target: react` adapter, so existing users see no change. (A
`/kit-build` alias is possible but unnecessary.)

## Where it lives

**acss-kit** — consistent with the boundary in
[`plugins-refactoring.md`](../plans/plugins-refactoring.md): acss-kit owns the
component *library* + generation + theme pipeline + stack detection; style-agent
owns the *format specs* (the COMPONENT.md spec it conforms to). The two
coordinate through the file formats, not shared code (the plugin self-containment
constraint).

## Dependencies & sequencing

This skill is **downstream of both workstreams** and must land after them:

| Needs | From |
|---|---|
| COMPONENT.md spec + the 15 reference docs inverted to neutral COMPONENT.md | Workstream B ([`component-md-spec.md`](../plans/component-md-spec.md)) + the sweep |
| `design_md_to_tokens.py` + token homes + `/theme-from-design` | Workstream A ([`design-md-token-parity.md`](../plans/design-md-token-parity.md)) |
| `## Target:` adapters for stateful/compound components | the neutral-first authoring (per the framework-agnostic decisions) |

So it slots in as roadmap **PR 7+** (after A's adapter and B's spec + inversion).

## Risks & tensions

- **Projection fidelity for non-React targets.** Behavior/reactivity is the lossy
  seam (the framework-agnostic finding). Mitigation: ship `## Target:` adapters
  for stateful/compound components; rely on the behavior spec + neutral
  `init(root)` for the rest; the agent projects the idiom. Purely presentational
  components (img, link, list) project trivially. **Policy (decided):**
  warn-don't-decline — project stateful components without an adapter but flag
  them for review (decision 5).
- **DESIGN.md optional.** Must degrade gracefully to theme-or-fallbacks; never
  hard-require a DESIGN.md to generate a component.
- **`/kit-add` migration.** The React path must stay identical through the
  reference.md → COMPONENT.md inversion. Golden-output tests (already planned in
  Workstream A PR 2) guard this.
- **Per-target dependency resolution.** Compound components (`Card.Title`) and
  sibling imports differ per framework; the projector handles assembly per
  target.
- **Verification gap.** `verify_integration.py` is React/Sass-aware today.
  **Decided (decision 4):** ship a documented manual integration check for
  non-React targets first; extend the verifier per target later. The gap is
  documented, not silent.

## Resolved decisions (2026-06-14 review)

1. **Refactor `/kit-add`** (not a new command). It already owns stack detection,
   `--target`, dep resolution, and verification; the React path stays
   byte-identical via the `## Target: react` adapter (guarded by Workstream-A
   PR 2 golden tests).
2. **Default target inferred from `detect_stack.py`** (fall back to `react`),
   with the inferred target **shown in the Step B4 preview** so the user can
   override before any file is written.
3. **Auto-detect a repo-root `DESIGN.md`** (override with `--design=`), and
   **never hard-require one** — absent a DESIGN.md, fall back to the COMPONENT.md
   `var(--x, <fallback>)` defaults so generation still succeeds. The
   `validate_design_md.py` gate catches an unusable DESIGN.md.
4. **Ship a documented manual integration check first** for non-React targets;
   extend `verify_integration.py` per target later. The gap is documented, not
   silent.
5. **Warn-don't-decline projection.** Presentational components project freely;
   for stateful/compound components with **no `## Target:` adapter** for the
   requested framework, **project but emit a warning** ("generated by projection
   from the neutral contract — review the behavior wiring"). The warning doubles
   as the signal that a `## Target:` adapter is worth authoring.

**Throughline:** decisions 1–3 make the skill *smart by default* (refactor,
infer, auto-detect) with *visible overrides*; decisions 4–5 *ship honestly with
documented gaps* rather than over-engineering or refusing.

## Next step

The five design decisions are **resolved** (above). This remains forward-looking
— it depends on COMPONENT.md and the DESIGN.md adapter existing — so it is held
as roadmap **PR 7+** and converts to an execution plan once Workstreams A and B
land. No open decisions block that conversion.
