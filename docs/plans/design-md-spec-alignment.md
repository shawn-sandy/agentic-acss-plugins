---
status: proposal
type: design
created: 2026-06-14
repo-name: acss-plugins
---

# Proposal: Aligning our markdown component patterns with `DESIGN.md`

> **This is a proposal for review, not an execution plan.** It captures the
> comparison between Google Labs' [`DESIGN.md`](https://github.com/google-labs-code/design.md)
> spec and our own markdown patterns, and proposes a two-part path: (A) let our
> components consume a `DESIGN.md`, and (B) publish a sibling spec for our
> component markdown. No spec text or code is written yet. Two scope decisions
> are already locked (see [Locked decisions](#locked-decisions)); the rest is
> open for discussion.

## Context

`DESIGN.md` (Google Labs, `version: alpha`) is a format spec for describing a
**visual identity to coding agents**. One file, two halves:

- **YAML front-matter** — machine-readable tokens: `colors`, `typography`,
  `spacing`, `rounded`, and a `components` map. Token references use
  `{colors.primary-60}` path syntax. Dimensions carry `px`/`em`/`rem` units.
- **Markdown body** — human-readable rationale in a fixed `##` section order:
  Overview → Colors → Typography → Layout → Elevation & Depth → Shapes →
  Components → Do's and Don'ts.

It is documented as a portable standard: a consumer-behavior table (unknown
section → preserve; **duplicate heading → reject the file**), a `version` field,
and an explicit "agents read this to produce UIs" consumption model with
`lint` / `diff` / `export` tooling (to Tailwind, W3C DTCG, Figma variables).

Crucially, its `components` section is **only style tokens** —
`backgroundColor`, `textColor`, `typography`, `rounded`, `padding`, `size`,
`height`, `width`, with variants expressed as sibling keys
(`button-primary`, `button-primary-hover`). It says nothing about props,
markup, behavior, or accessibility.

## The core finding

We have **two** markdown artifacts, at two different layers. `DESIGN.md`
overlaps with exactly one of them:

| Our artifact | Layer | Encodes | DESIGN.md overlap |
|---|---|---|---|
| `styles` skill + theme CSS (`light.css`/`dark.css`, `theme.schema.json`, OKLCH generator, `validate_theme.py`) | **Design-token layer** | Colors only — but with generation + WCAG contrast enforcement | **High** — this is the same layer |
| `component-<name>/reference.md` (9-section embedded-markdown shape) | **Implementation layer** | Full TSX/SCSS code, props interface, a11y contract | **None** — DESIGN.md has no equivalent |

> **`DESIGN.md` is a sibling to our `styles`/theme layer, not to our component
> `reference.md`.** Its `components` map is style tokens; our `reference.md` is
> a code-generation spec. They are complementary, which is *why* the work
> splits cleanly into two non-overlapping workstreams below.

### Side-by-side: token layer

| Dimension | `DESIGN.md` | Our `styles`/theme layer |
|---|---|---|
| Authoring surface | YAML front-matter | CSS custom properties (`light.css`/`dark.css`) |
| Color model | Any CSS color (hex, `oklch()`, named, `color-mix`) | Hex in files; OKLCH internally for generation |
| Color roles | Recommended (non-normative): `primary`, `secondary`, `tertiary`, `neutral`, `surface`, `on-surface`, `error` | **Enforced**: 15 required `--color-*` roles + 3 optional (18 total) |
| Typography tokens | First-class (`fontFamily`, `fontSize`, `fontWeight`, `lineHeight`, `letterSpacing`, `fontFeature`, `fontVariation`) | **None** — no token home |
| Spacing tokens | First-class scale map | **None** — components use rem literals |
| Rounded (radius) tokens | First-class scale map | **None** — components use rem literals |
| Component-level tokens | `components.<name>.<prop>` map | Per-component CSS vars (`--btn-primary-bg`, `--btn-padding-block`) |
| Light/dark | Single palette; dark mode underspecified | Both modes, auto-mirrored |
| Contrast enforcement | Lint warns | **`validate_theme.py` gate** (10 WCAG AA pairs) |
| Token references | `{colors.primary}` path syntax | `var(--color-primary, <fallback>)` cascade |
| Interop targets | tokens.json, Figma, Tailwind, DTCG | Internal JSON schema (round-trip only) |

The two systems are strikingly close on colors, and our contrast gate is
*stronger* than DESIGN.md's lint. The gaps are **typography, spacing, and
rounded** — DESIGN.md has token homes for all three; we have none.

## Locked decisions

Settled before this draft:

1. **Deliverable: proposal doc only.** No spec text and no adapter code in this
   pass — this document is the artifact, for review first.
2. **Token scope: full parity with `DESIGN.md`.** The target is to give our
   token layer a home for **typography, spacing, and rounded** in addition to
   colors — not to stay colors-only. This is the larger, more invasive scope
   and changes how components reference dimensions (rem literals → tokens).

## Workstream A — let our components *consume* a `DESIGN.md`

The seam is our **theme pipeline**, not the per-component files. Components
already read semantic CSS variables, and those roles are owned exclusively by
theme files (the `@layer foundation, components, utilities, theme` cascade
means theme always wins). So "consuming `DESIGN.md`" =
**adding `DESIGN.md` as a new input to the `styles` pipeline**, alongside
seed-hex / Figma / image extraction:

```
DESIGN.md (YAML front-matter)
   └─ design_md_to_tokens.py        ← NEW adapter (parse + map)
        └─ tokens_to_css.py         ← exists
             ├─ light.css / dark.css           (colors)
             ├─ typography.css                  (NEW — typography tokens)
             └─ space-radius.css                (NEW — spacing + rounded tokens)
        └─ validate_theme.py        ← exists (WCAG contrast gate)
```

Surfaced as a new flow (`/theme-from-design DESIGN.md`) or by extending
`/theme-extract` to accept a `.md` input.

### Color mapping (DESIGN.md → our roles)

| DESIGN.md token | Our role | Notes |
|---|---|---|
| `colors.primary` | `--color-primary` | direct |
| `colors.surface` | `--color-surface` | direct |
| `colors.on-surface` | `--color-text` | rename |
| `colors.neutral` | `--color-background` / `--color-border` | needs translation table |
| `colors.error` | `--color-danger` | alias |
| `colors.secondary` / `tertiary` | `--color-brand-accent` (optional) | best-effort |
| *(roles DESIGN.md omits)* | the rest of our 15 required roles | **seed the OKLCH generator from `primary` to synthesize the gaps**, then run `validate_theme.py` |

Because our 15 roles are *required* and DESIGN.md's are *recommended/optional*,
the adapter must fill gaps: map what's present, generate the remainder via our
existing OKLCH algorithm, and gate the whole result on contrast. DESIGN.md is
also mode-thin (single palette) where we are light+dark — the adapter generates
both modes from the supplied primitives.

### Typography / spacing / rounded mapping (the full-parity work)

This is the part that does not exist yet and is the bulk of the effort:

| DESIGN.md | New token home (proposed) | Component change |
|---|---|---|
| `typography.<name>` (`fontFamily`, `fontSize`, `fontWeight`, `lineHeight`, `letterSpacing`, …) | `--font-*` custom properties in a new `typography.css` theme file | Components reference `--font-body-md-*` instead of hardcoded `font-size`/`line-height` |
| `spacing.<scale>` (`xs`…`xl`, `base`) | `--space-*` custom properties | Components reference `--space-md` instead of rem literals in padding/gap/margin |
| `rounded.<scale>` (`sm`…`full`) | `--radius-*` custom properties | Components reference `--radius-md` instead of hardcoded `border-radius` |

Open questions this raises (flagged, not resolved):

- **Schema growth.** `theme.schema.json` and `_tokens.py` `ROLE_GROUPS` are
  colors-only today. Full parity means new schema sections, new validators
  (units, scale completeness), and new round-trip coverage in
  `css_to_tokens.py`.
- **Component template churn.** Every `reference.md` SCSS Template currently
  hardcodes rem for spacing and radius. Full parity implies a sweep to swap
  literals for `var(--space-*)` / `var(--radius-*)` — touching all 15
  components. This is the single biggest ripple and should likely be its own
  staged sub-effort.
- **Contrast vs. typography/spacing.** Our validation gate is contrast-only.
  Typography/spacing tokens have no equivalent automated gate — we'd decide
  whether to add scale-completeness / minimum-target-size checks or leave them
  unvalidated.

## Workstream B — publish a sibling spec for our component markdown

`DESIGN.md`'s value is partly that it is *written up as a portable, versioned
standard*. Our `reference.md` shape is equally rigorous but only encoded
implicitly inside the `acss-kit-component-author` maintainer skill and
kit-core's Step B. The proposal: **formalize our component-markdown format into
a documented spec** — working name `COMPONENT.md` — mirroring
`DESIGN.md/docs/spec.md`:

- Purpose + bipartite format (front-matter + markdown body).
- Fixed section order (our existing 9 sections: Verification banner, Overview,
  Generation Contract, Props Interface, TSX Template, CSS Variables, SCSS
  Template, Accessibility, Usage Examples).
- Grammar for each block (Generation Contract fields, Props union literals,
  TSX/SCSS template rules, the Accessibility WCAG-criteria contract).
- **A token-reference syntax that points *into* `DESIGN.md`** — the CSS
  Variables section would declare `--btn-primary-bg: {colors.primary}` and
  `--btn-padding-block: {spacing.md}` instead of hardcoding values. This is the
  hinge that connects B back to A.
- Consumer-behavior table (unknown section → preserve; duplicate → reject) and
  a `version: alpha` field, matching DESIGN.md's conventions.

The payoff is a **two-file design system**: `DESIGN.md` owns visual identity
(tokens), `COMPONENT.md` owns component implementation and *references* DESIGN.md
tokens. That fills a niche DESIGN.md deliberately leaves empty (it stops at
style tokens for components), and it makes our format publishable and
interoperable the same way DESIGN.md is.

### Why B likely precedes A in execution

Writing the `COMPONENT.md` spec first forces the `{path}` token-reference
contract that the adapter in A must then resolve. The spec defines the
interface; the adapter implements it. B is also docs-only and lower-risk. (This
ordering is a recommendation for the *eventual* build, not a decision for this
proposal pass.)

## Risks & tensions

- **Full parity is a large surface.** Typography + spacing + rounded token
  homes plus a 15-component SCSS sweep is materially bigger than the colors-only
  alternative. Worth staging into independent PRs (token homes → one component
  pilot → bulk sweep), mirroring how the component-skill split was staged.
- **DESIGN.md is `alpha`.** The upstream format may change. Pinning to a commit
  SHA (as we already do for fpkit references) and isolating all DESIGN.md
  knowledge inside `design_md_to_tokens.py` limits blast radius.
- **Naming divergence.** Our roles (`--color-danger`, `--color-text`) differ
  from DESIGN.md's (`error`, `on-surface`). The translation table is a
  maintenance surface and a place silent mismatches can hide — it needs tests.
- **Round-trip symmetry.** We currently round-trip CSS↔JSON via
  `css_to_tokens.py`. A DESIGN.md export path (CSS → DESIGN.md) would be the
  natural symmetric feature but is explicitly out of scope here; note it as a
  follow-on.

## Open questions for review

1. **Spec home & name.** Does `COMPONENT.md` live in `style-agent`
   (framework-agnostic, matches DESIGN.md's neutrality) or `acss-kit` (where the
   `reference.md` shape originates)? Is `COMPONENT.md` the right name?
2. **Token file layout.** One combined `theme.css` or separate
   `typography.css` / `space-radius.css` files? Affects the `@layer` cascade and
   import order.
3. **Staging.** Should full parity land as one cohesive effort or as
   independent PRs (token homes first, component sweep last)?
4. **DESIGN.md authoring.** Do we *generate* a DESIGN.md from a seed color
   (a new `styles` output) in addition to consuming one — i.e. is DESIGN.md an
   import format, an export format, or both?

## Next step

This proposal is for review. On approval, the natural follow-on is to convert
the two workstreams into execution plans under `docs/plans/` — `COMPONENT.md`
spec (Workstream B) first, then the `design_md_to_tokens.py` adapter and
full-parity token homes (Workstream A).
