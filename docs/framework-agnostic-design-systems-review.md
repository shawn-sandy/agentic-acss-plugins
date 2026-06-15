# Framework-Agnostic Design Systems — Review & Recommendations

> **Status:** for review
> **Date:** 2026-06-15
> **Source:** [Piccalilli — *Framework-agnostic design systems* (Part 1)](https://piccalil.li/blog/framework-agnostic-design-systems-part-1/)
> **Scope:** Compare the article's approach against acss-kit's DESIGN.md / COMPONENT.md direction; identify improvements vs. gaps; recommend solutions.
> **Companion artifacts:** five implementation plans under [`docs/plans/`](plans/), opened as PR #98.

This brief consolidates the session's analysis into one reviewable document. The five recommendations at the bottom each have a self-contained HTML implementation plan; this document is the *why* behind them.

---

## Verdict

The article and acss-plugins fight the **same enemy** — framework lock-in — and agree on almost every *principle*. They differ on exactly one thing: **where the portability boundary sits.**

- **The article bets on a runtime artifact.** Compile primitives to Web Components once; every framework consumes the same bundle. "Agnostic" = one thing runs everywhere.
- **acss-plugins bets on a spec + generation.** DESIGN.md / COMPONENT.md are the portable source of truth; an agent *projects* them into owned, idiomatic per-framework code. "Agnostic" = one spec, N generated outputs, you own each.

Most of the article is **validation that the current direction is sound.** The genuine gaps are narrow, and on the article's own stated "next hard problem" (tokens) acss-kit is already ahead.

### The core conceptual difference

The deep difference is **runtime portability vs. source portability**. The article moves the agnostic boundary to the browser (a custom element is the lingua franca). acss-kit moves it one layer earlier, to a markdown contract (the spec is the lingua franca; code is generated). The article's model yields a true drop-in bundle but couples consumers to that bundle plus its runtime; acss-kit's yields zero runtime coupling and idiomatic native code, at the cost of N artifacts to keep coherent. Neither is "more agnostic" — they relocate the same seam.

---

## Where the article validates the current direction (convergence)

Each of these article principles is *already* implemented in acss-kit — strong confirmation the direction is right:

| Article principle | acss-kit equivalent | Match |
|---|---|---|
| Framework lock-in is "baffling to bake in at day one" | "Installing `@fpkit/acss` creates coupling… generate self-contained implementations that you own" | Identical thesis |
| Component custom properties "reference system-level tokens with fallbacks" | Every generated prop is `var(--x, <fallback>)`; renders with or without a design system (spec.md §6) | Near-identical |
| Naming `--{prefix}-{component}-{property}` | `--{component}-{element?}-{variant?}-{property}` | Near-identical |
| "Components should be as primitive as possible… told explicitly what state to reflect" | COMPONENT.md = structure + styles + a11y + optional minimal `init(root)`; state is not baked in | Match |
| "Design tools are terrible places to codify systemic decisions" | DESIGN.md is a *token source* you ingest, then codify in CSS | Match |
| Token math: "logarithmic scales… programmatic hue and lightness shifts" | OKLCH palette algorithm: lightness targets + hue offsets (success 145°, warning 75°, danger 25°) | acss-kit is **ahead** |
| Tokens/components separation | "DESIGN.md owns tokens, COMPONENT.md owns components" (spec.md) | Match |

---

## The one real divergence — and the honest trade-off

| | Article (Web Components) | acss-kit (spec + generation) |
|---|---|---|
| Portable artifact | Compiled custom-element bundle | DESIGN.md / COMPONENT.md markdown |
| Consumer gets | A package to `npm` install | Generated source they own |
| Runtime coupling | Depends on the bundle + its WC runtime | **None** — plain TSX/SCSS/HTML |
| Theming | Through the Shadow DOM boundary (`::part`, piercing custom props) | Direct — it is your own CSS, no shadow boundary |
| Per-framework idiom | Thin wrapper around a generic element | Fully idiomatic React/Astro/etc. |
| Cost | One artifact, but you don't own it; WC ergonomics in React are awkward (events, refs, SSR) | N generated artifacts to keep coherent; no single drop-in |
| Updates | `npm update` | Re-generate / `/kit-update` (sha-drift detection) |

The article's model is better for "one library, many consuming apps you don't control." acss-kit's is better for "I want to own and freely modify the code, with no runtime dependency." That is a real, defensible difference in target audience — not a flaw to fix.

---

## Where acss-kit is ahead (do not change these)

1. **Tokens.** The article *defers tokens to a future Part 2* ("the next technical challenge feels naturally like figuring out a token workflow"). acss-kit already has OKLCH perceptually-uniform palettes, **WCAG 2.2 AA contrast validation by construction**, an 18-role catalogue, spacing/rounded/typography scales, and DESIGN.md round-trip scripts. Ahead on the precise thing the author flags as unsolved.
2. **Accessibility as a contract.** The `a11y:` front-matter plus the theme contrast validator make WCAG a first-class, checkable artifact. The article barely touches a11y.
3. **Future-proofing.** The article argues web standards outlive frameworks (true) — but a consumer still depends on its WC bundle + toolchain runtime. Generated source you own is arguably *more* future-proof: nothing is left to break.

---

## Recommendations

Ranked by leverage. Each links to its implementation plan.

| # | Recommendation | Gap it closes | Leverage | Effort | Plan |
|---|----------------|---------------|----------|--------|------|
| 1 | Realize the `web-component` projection target | No runtime-portable artifact exists (spec lists it; nothing builds it) | High | Medium | [realize-web-component-target.html](plans/realize-web-component-target.html) |
| 2 | Generate a component catalog from COMPONENT.md | Machine-readable contract has no docs consumer | High | Medium | [generate-component-catalog.html](plans/generate-component-catalog.html) |
| 3 | Emit a Custom Elements Manifest (`custom-elements.json`) | No interop with standard WC tooling | Medium | Low–Medium | [emit-custom-elements-manifest.html](plans/emit-custom-elements-manifest.html) |
| 4 | Document the primitive/composite boundary | Spec implies but never states the scope ceiling | Medium | Low | [document-primitive-composite-boundary.html](plans/document-primitive-composite-boundary.html) |
| 5 | Evaluate CSS `@scope` encapsulation (spike) | Encapsulation approach unexamined vs. the article's | Low | Low | [evaluate-css-scope-encapsulation.html](plans/evaluate-css-scope-encapsulation.html) |

### 1. Realize the `web-component` projection target — *highest leverage*

The COMPONENT.md spec already declares `web-component` "the universal runtime output every framework can consume" (spec.md §5), but no generator path or adapter realizes it. Building it is the **synthesis** of both philosophies: it produces exactly the article's artifact (a drop-in custom element) *without* abandoning the ownership/spec-first model — it becomes one more `## Target:`. This also unlocks the "agnostic primitive that React/Vue/Svelte apps all consume" use case acss-kit currently can't serve.
**Solution:** a `## Target: web-component` adapter contract + a projection reference (light-DOM default so DESIGN.md tokens keep cascading; Shadow DOM opt-in) + `/kit-add --target=web-component` + a structural validator wired into `tests/run.sh`.

### 2. Render COMPONENT.md into a docs/catalog site — *high leverage*

The article's strongest tooling idea is **docs-as-a-byproduct**: JSDoc → custom-elements manifest → auto-built props tables. acss-kit's front-matter (`props`, `variants`, `tokens`, `a11y`) *is* that manifest — it has the data and no consumer for it.
**Solution:** a stdlib-only generator that turns a directory of `*.component.md` into a self-contained, token-themed static catalog (props tables, variant gallery, a11y criteria, live previews), reusing the existing preview machinery.

### 3. Emit a Custom Elements Manifest — *medium leverage*

The article rides the standardized [CEM](https://github.com/webcomponents/custom-elements-manifest) JSON, which editors, Storybook, and analyzers already consume. acss-kit's front-matter is a bespoke superset.
**Solution:** serialize COMPONENT.md front-matter to `custom-elements.json` (generator/validator contract). Cheap once #1 exists; lets components appear in standard WC tooling. Pairs with #2 as a shared intermediate representation.

### 4. Name the primitive/composite boundary explicitly — *low effort, prevents drift*

The article draws a sharp line: primitives in the agnostic layer, stateful/composite logic in the app. acss-kit's spec implies this (presentational vs. `behavior`-bearing) but never states the ceiling.
**Solution:** a "Scope — primitives, not composites" paragraph in spec.md §1 and a one-line reminder in the `component-md` rule, plus an audit confirming no existing component.md violates it.

### 5. Consider `@scope` — *lowest priority; park it*

The article uses CSS `@scope` for encapsulation. acss-kit uses `data-*` + component-prefixed custom properties, and because consumers *own* the CSS, leakage is far less acute than for a shipped bundle. Only relevant if #1 ships with light DOM.
**Solution:** a time-boxed spike producing a decision record (Adopt / Don't-adopt / Revisit-after-#1) — no production CSS change.

---

## Suggested sequencing

- **#3 → #2** share `plugins/acss-kit/scripts/lib/component_md.py` (a COMPONENT.md parser); whichever lands first creates it, the other reuses. #3's intermediate manifest can become the single representation behind #2 (the article's manifest → docs architecture).
- **#1** is independent and the highest-leverage item — the clearest "improvement" the article surfaces.
- **#4 / #5** are low-risk and can land anytime; #5 is best deferred until after #1's light-DOM decision.

---

## Open questions for reviewers

- **Tag prefix & registration (blocks #1):** canonical custom-element prefix (`acss-`, `ui-`, or configurable) and auto-register vs. exported `register()`. Tracked in the #1 plan's Unresolved Questions.
- **Distribution:** should acss-kit ever ship a *bundled* custom-elements package (the article's distribution layer), or stay generation-only? Captured as a Next Step in #1.
- **`@scope` adoption:** deferred to the #5 spike's decision record.

---

## Sources

- [Piccalilli — *Framework-agnostic design systems* (Part 1)](https://piccalil.li/blog/framework-agnostic-design-systems-part-1/) — Part 2 (tokens) not yet published as of this review.
- COMPONENT.md spec: [`plugins/style-agent/docs/component-md/spec.md`](../plugins/style-agent/docs/component-md/spec.md)
- Implementation plans: [`docs/plans/`](plans/)
