---
status: proposed
type: feature
created: 2026-06-14
repo-name: acss-plugins
---

# Plan: DESIGN.md token parity + adapter (Workstream A)

> Execution plan for **roadmap PRs 1–4** of
> [`design-md-spec-alignment.md`](design-md-spec-alignment.md), picking up after
> the Workstream B spec plan ([`component-md-spec.md`](component-md-spec.md)).
> Gives our token layer **full DESIGN.md parity** (typography + spacing + rounded
> on top of colors), sweeps the 15 components onto those tokens, then lands the
> `design_md_to_tokens.py` adapter that consumes a DESIGN.md via `css-tailwind`.
> All work lives in **acss-kit** (placement settled in
> [`plugins-refactoring.md`](plugins-refactoring.md): the adapter emits acss role
> CSS and depends on the OKLCH pipeline). Decisions assumed: **Route 1**
> (`css-tailwind` input, `npx` accepted), **hard-fail on missing primary**,
> **phased sweep**.

## Context

Today the token layer is **colors-only**. `_tokens.py:ROLE_GROUPS` is the single
source of truth (18 `--color-*` roles); `tokens_to_css.py` renders them via
`format_palette` as `var(--role, <hex>)` under `:root` / `[data-theme="dark"]`;
`generate_palette.py` produces the `{role: hex}` JSON from a seed;
`validate_theme.py` gates 10 WCAG contrast pairs; `css_to_tokens.py` reverses the
write. There is **no home for typography, spacing, or rounded** — components
hardcode rem/px literals (measured: ~97 spacing + ~19 radius + ~47 typography =
~163 sites across 14 of 15 components).

DESIGN.md has first-class `typography` / `spacing` / `rounded`. To consume one
faithfully we must first *have somewhere to put those tokens*, then point
components at them, then build the adapter.

## Objective

Land four sequenced PRs: (1) token homes + writers + validators; (2) a
button-only sweep pilot with a golden test; (3) the bulk 14-component sweep plus
the `alert` state-color fix; (4) the `design_md_to_tokens.py` adapter +
`validate_design_md.py` + `/theme-from-design`. Each keeps `tests/run.sh` green.

## Naming + layout decisions (resolve at PR 1)

- **Custom-property prefixes:** `--space-*` (spacing scale), `--radius-*`
  (rounded scale), `--font-<role>-{family,size,weight,line,tracking}` (flattened
  typography composites). These mirror the `css-tailwind` export prefixes
  (Appendix F of the proposal) so the adapter's remap is mechanical.
- **File layout:** separate generated files **`space-radius.css`** and
  **`typography.css`**, imported in the `@layer theme` block after
  `light.css`/`dark.css`. (Open question 2 in the proposal — this plan picks
  separate files; revisit if the cascade argues for one.)
- **Mode-independence:** spacing/rounded/typography are **mode-independent** (no
  light/dark split) — a single `:root` block, unlike colors.

## PR 1 — Token homes (no component changes)

1. **Extend `_tokens.py` with non-color token kinds.** Add `SPACE_SCALE`,
   `RADIUS_SCALE` (ordered `[(name, default)]` lists, e.g. `xs…xl`, `full`) and
   `TYPOGRAPHY_TOKENS` (role → sub-prop map). Add `format_scale()` and
   `format_typography()` writers that render mode-independent `:root` blocks with
   the `var(--x, <fallback>)` convention. Keep `ROLE_GROUPS`/`format_palette`
   untouched.
   - *Why:* `_tokens.py` is the single source of truth both writer and reader
     import; new kinds belong beside the existing one so round-trip stays
     symmetric. *Verify:* `format_scale({"md":"1rem"}, ...)` emits
     `--space-md: var(--space-md, 1rem);`; `ALL_ROLES` (colors) is unchanged;
     `python _tokens.py --self-test` (add cases) passes.

2. **Extend `theme.schema.json`** with `spacing`, `rounded`, and `typography`
   sections (additive; colors block unchanged). Update
   `references/theme-schema.md` to document them.
   - *Why:* the schema is the internal contract for `tokens_to_css.py` /
     `css_to_tokens.py`; new sections keep round-trip validation honest.
     *Verify:* a tokens JSON carrying spacing/rounded/typography validates;
     `theme-reference-reviewer` agent passes on the edited references.

3. **Teach `tokens_to_css.py` to emit `space-radius.css` + `typography.css`.**
   When the input JSON carries the new sections, write the new files via the new
   formatters; skip silently when absent (back-compat — colors-only input still
   produces only `light.css`/`dark.css`).
   - *Why:* additive output keeps every existing `/theme-create` call working
     byte-identically. *Verify:* colors-only input produces an unchanged
     `light.css` (golden diff); input with spacing produces `space-radius.css`;
     `--self-test` covers both.

4. **Round-trip in `css_to_tokens.py`** — parse `--space-*`/`--radius-*`/
   `--font-*` back into the JSON sections.
   - *Why:* the CSS↔JSON round-trip is a load-bearing invariant (`/theme-extract`
     writes JSON; `/style-tune` reads it). *Verify:* `css_to_tokens(tokens_to_css(x)) == x`
     for a fixture carrying all four token kinds.

5. **Add `validate_tokens.py`** (generator/validator contract: data/text to
   stdout, errors to stderr, exit 0/1/2) — checks scale completeness (required
   steps present), dimension-unit validity (`px|em|rem`), and typography
   sub-prop presence. Leave `validate_theme.py` (contrast) untouched.
   - *Why:* dimensions/typography have no contrast gate; a structural validator
     is their equivalent guardrail. *Verify:* a malformed scale (missing `md`,
     or `12` with no unit) exits 1 with a reason; a valid set exits 0;
     `python-script-reviewer` agent passes.

6. **Seed defaults + docs.** Ship default `space-radius.css` / `typography.css`
   values (a sane scale) so projects without a DESIGN.md still get tokens. Update
   `styles/SKILL.md` and `references/role-catalogue.md`.
   - *Why:* parity must not regress the colors-only happy path. *Verify:*
     `tests/run.sh` green; a fresh `/theme-create` still works with no new
     required input.

## PR 2 — Sweep pilot: `button` only

1. **Capture a golden baseline.** Run `/kit-add button` against a clean
   `tests/sandbox/` from current `main`; snapshot `button.tsx` + `button.scss`
   into `tests/fixtures/golden/component-button/`. Add a `tests/run.sh` step that
   re-runs and diffs.
   - *Why:* the sweep's premise is value-preserving CSS; a golden makes that
     mechanical, catching drift visual review misses. *Verify:* on `main` the
     diff is clean; the step is wired into `tests/run.sh`.

2. **Rewrite `component-button/reference.md` SCSS + CSS Variables** to consume
   tokens: spacing literals → `var(--space-*)`, radius → `var(--radius-*)`,
   font props → `var(--font-btn-*)`, each keeping a hardcoded fallback so the
   component still renders with no theme present.
   - *Why:* button is the dep-leaf for many components and the canonical
     reference — proving the pattern here de-risks the bulk pass. *Verify:* the
     regenerated `button.scss` contains `var(--space-` / `var(--radius-`; every
     `var()` has a fallback; rendered output is visually equivalent to the
     golden (values resolve to the same computed pixels).

3. **Fix the `--color-primary-dark` debt.** Button references
   `--color-primary-dark`, which is **not** one of the 18 canonical roles
   (schema has `--color-primary-hover`). Repoint it.
   - *Why:* a live bug surfaced in the inventory — the hover color silently falls
     back today. *Verify:* `grep -r 'color-primary-dark' plugins/acss-kit` returns
     nothing; button hover resolves to `--color-primary-hover`.

## PR 3 — Bulk sweep (remaining 14) + `alert` fix

1. **Sweep the other 14 `reference.md` SCSS templates** onto `--space-*` /
   `--radius-*` / `--font-*` (~150 sites), each with fallbacks. Heaviest:
   Dialog (12 spacing), Nav (9), Button done. Add golden fixtures per component.
   - *Why:* completes parity so a DESIGN.md actually reshapes the whole kit.
     *Verify:* `tests/run.sh` golden diffs clean for all 15; no remaining bare
     rem/px in swept properties (a lint grep over the SCSS templates).

2. **Wire `alert` state colors to roles.** Replace hardcoded `#d1ecf1` etc. with
   `--color-info` / `--color-success` / `--color-warning` / `--color-danger`
   (+ derived `-bg`/border via `color-mix`, matching the bridge convention).
   - *Why:* alerts can't be themed today; parity means a theme/DESIGN.md recolors
     them. *Verify:* alert SCSS references the four semantic roles; contrast of
     each state's text-on-bg passes `validate_theme.py`-style checks.

## PR 4 — `design_md_to_tokens.py` adapter + validator + command

1. **`validate_design_md.py`** (detector contract: JSON + `reasons`, exit 0/1).
   Shell `npx @google/design.md lint`, normalize findings; **hard-fail
   (exit 1) on missing primary** and on duplicate section headings; warnings
   become `reasons` at exit 0.
   - *Why:* the primary is the OKLCH seed; an unusable DESIGN.md must be rejected
     before the pipeline runs. *Verify:* a DESIGN.md with no `primary` exits 1; a
     valid one exits 0 with `reasons: []`; `python-script-reviewer` passes.

2. **`design_md_to_tokens.py`** (generator/validator contract). Shell
   `npx @google/design.md export --format css-tailwind`, parse the `@theme`
   custom properties (stdlib regex — reuse `_tokens.py:parse_vars`), then:
   remap M3 names → our roles per the proposal's **Appendix A** table; **collapse**
   the surface/on-pairs; **synthesize** roles M3 omits (success/warning/info/
   focus-ring) by calling `generate_palette.py` on the resolved primary; lift
   `--spacing-*`/`--radius-*`/`--text-*` into the new token sections; normalize
   px→rem, the `DEFAULT` rounded key, `9999px`→`full`, quoted `fontWeight`.
   Emit the `theme.tokens.json` shape `tokens_to_css.py` consumes.
   - *Why:* this is the import path; offloading YAML + `{ref}` resolution to the
     upstream CLI keeps us stdlib and drift-free. *Verify:* the
     `paws-and-paths` example produces the role table in the proposal's
     Appendix D (2 roles synthesized, rest mapped); piping its output through
     `tokens_to_css.py` + `validate_theme.py` yields a contrast-valid theme.

3. **`/theme-from-design <DESIGN.md>` flow** in `styles/SKILL.md` (and a
   `commands/theme-from-design.md` delegating to it). Pipeline:
   `validate_design_md.py` → `design_md_to_tokens.py` → `tokens_to_css.py`
   (light/dark/space-radius/typography) → `validate_theme.py` +
   `validate_tokens.py` → `verify_integration.py`. Surface the synthesized roles
   and any contrast warnings.
   - *Why:* one command turns a DESIGN.md into a full, gated theme — the headline
     deliverable. *Verify:* `/theme-from-design examples/paws-and-paths/DESIGN.md`
     writes four CSS files and reports which roles were synthesized; rerun is
     idempotent.

4. **Document the `npx` dependency.** Note in `styles/SKILL.md` and the plugin
   README that `/theme-from-design` requires Node/`npx` (Route 1 decision).
   - *Why:* a runtime prerequisite must be discoverable. *Verify:* README +
     SKILL mention it; the flow fails gracefully with a clear message when `npx`
     is absent.

## Out of scope (roadmap PRs 5–6)

- **`tokens_to_design_md.py` + `/design-export`** (export *out* to DESIGN.md /
  DTCG / Tailwind) — roadmap PR 5.
- **Figma bridge** (`get_variable_defs` → DESIGN.md), **PostToolUse hook** on
  `DESIGN.md`, and the **`tests/run.sh` round-trip step** — roadmap PR 6.
- **`reference.md` → `COMPONENT.md` inversion** of the 15 docs — this plan's
  sweep (PR 2–3) edits the **`reference.md` SCSS in place** (swapping literals for
  `var(--space/radius/font-*)`), keeping `/kit-add` working. The inversion to
  neutral COMPONENT.md is **gated on the generator refactor** (`/kit-add` reading
  COMPONENT.md) and ships with it (spec-driven generation, roadmap PR 7), which
  *relocates* the already-token-driven SCSS into COMPONENT.md `## Styles`.

## Pre-submit checklist (per PR)

1. `tests/run.sh` green (golden diffs included from PR 2 on).
2. `plugin.json` version bumped via `/release-plugin acss-kit` (minor per PR —
   PR 1 and PR 4 are user-facing).
3. New scripts pass their contract (`python-script-reviewer`): detector for
   `validate_design_md.py`, generator/validator for `design_md_to_tokens.py` /
   `validate_tokens.py`.
4. `marketplace.json` + README + CHANGELOG updated when commands/behaviour change
   (PR 1 token homes, PR 4 `/theme-from-design`).
5. `.claude/rules/python-scripts.md` inventory note if a contract family changes
   (it does not — both new contracts already exist).

## Dependencies

PR 1 → PR 2 → PR 3 (sweep needs token homes; bulk needs the pilot pattern).
PR 1 → PR 4 (adapter needs the token sections to emit). PR 4 is independent of
PRs 2–3 — the adapter can land before the component sweep finishes, since
components keep their fallbacks throughout.
