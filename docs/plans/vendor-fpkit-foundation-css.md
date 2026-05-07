# Vendor fpkit foundation CSS into `acss-kit`

## Context

`acss-kit` ships components, the polymorphic `UI` primitive, and OKLCH theme
files (`light.css` / `dark.css` / `brand-*.css`). It does **not** ship the
base/foundation CSS layer that fpkit loads from `packages/fpkit/src/index.scss`
before any component styles. As a result, a fresh project that installs
`acss-kit` + `acss-utilities` gets:

- working components (Button, Card, etc.) and utility classes,
- working color theme tokens,

but **no CSS reset, no base typography for `<h1>`–`<h6>` / `<p>` / `<ul>`,
no root layout, no spacing / motion / breakpoint tokens beyond colors, no
shadow scale, no column system, no element rules** — and that's why projects
feel unusable until the developer hand-writes a base layer.

This plan adds the missing foundation layer, vendored from fpkit's
`@fpkit/acss@6.5.0` tag (SHA `9063512fa822963d8151c972bed9f5b0e531df0f`)
**with documented project-side patches**, mirroring the precedent set by
`assets/foundation/ui.tsx`.

Layout primitives (Box, Stack, Cluster, Grid, Flex, Landmarks) and presentation
components missing from `references/components/` (Tag, Badge, Details, Progress,
Heading, Text, Breadcrumbs, Title, TextToSpeech) are explicitly **out of scope**
for this PR — see Next Steps.

## Gap audit (from `index.scss` at the pinned tag)

| Upstream `@use` | Purpose | Plugin status |
|---|---|---|
| `sass/tokens` (`_index`, `_breakpoints`, `_color-primitives`, `_motion`) | Tier 1 raw + Tier 2 non-color tokens | **Vendor** |
| `sass/tokens/_color-semantic` | Color semantic roles | **Skip** — overlaps with theme files |
| `sass/_reset` | CSS reset (margin, box-sizing) | **Vendor** |
| `sass/_layout` | Base layout / page-level rules | **Vendor** |
| `sass/_type` | Heading + paragraph + line-height base | **Vendor + patch** (heading color) |
| `sass/_properties` | Custom-property registrations | **Vendor** |
| `sass/_globals` | Global element rules | **Vendor** |
| `sass/_elements` | Element-specific styling (hr, blockquote, …) | **Vendor** |
| `sass/_grid` (legacy) | Legacy grid container | **Vendor** |
| `sass/_columns` | Column system | **Vendor** |
| `sass/styles/_shadows` | Shadow scale | **Vendor** |
| `sass/styles/_colors` | Color helper classes | **Vendor** |
| `sass/_mixins`, `sass/_loading-animation`, `sass/_styles` | Internal helpers | **Vendor** (transitive) |
| `sass/utilities/*` | Atomic utilities | **Skip** — covered by `acss-utilities` plugin |
| `components/*/*.scss` | Component styles | Already covered per-component |

## Objective

Ship the missing foundation CSS as a compiled `foundation.css` barrel
(plus the SCSS sources copied alongside for fork/override), wire it into
`/kit-add` first-run setup with a backward-compat prompt for existing
installs, and enforce predictable cascade via CSS `@layer`.

## Steps

1. **Pin the upstream ref + enumerate project patches.** Create
   `plugins/acss-kit/assets/foundation/SOURCE.md`. It must contain:

   - The pinned ref: `@fpkit/acss@6.5.0`, SHA
     `9063512fa822963d8151c972bed9f5b0e531df0f`.
   - Manual refresh commands (`gh api` to fetch each file at the pinned ref;
     `cp` / `sass` to recompile).
   - **Every project-side divergence**, each with a one-line rationale:
     - **(P1)** `tokens/_color-semantic.scss` excluded from `_index.scss` —
       theme files own every `--color-*` role.
     - **(P2)** `_globals.scss` heading rules patched to use
       `color: var(--color-text, #212529)` per
       `.claude/rules/scss-conventions.md`.
     - **(P3)** Project-authored
       `@media (prefers-reduced-motion: reduce) { :root { --transition: none; --tran-all: none; } }`
       block appended to the compiled `foundation.css`.
     - **(P4)** Compiled `foundation.css` wrapped in
       `@layer foundation { … }` so theme + utilities + components can win
       predictably (see step 4).

   Why: every refresh starts here, so divergences must be discoverable in one
   place.

2. **Vendor SCSS sources** under
   `plugins/acss-kit/assets/foundation/sass/` mirroring upstream layout
   (kept nested so refresh is a flat `cp` from a sibling fpkit clone):

   ```text
   assets/foundation/sass/
   ├── _index.scss               # project-authored — omits tokens/_color-semantic (P1)
   ├── _reset.scss
   ├── _layout.scss
   ├── _type.scss
   ├── _properties.scss
   ├── _globals.scss             # patched per P2 (heading color)
   ├── _elements.scss
   ├── _grid.scss
   ├── _columns.scss
   ├── _mixins.scss
   ├── _loading-animation.scss
   ├── _styles.scss
   ├── tokens/
   │   ├── _index.scss            # project-authored — omits _color-semantic (P1)
   │   ├── _breakpoints.scss
   │   ├── _color-primitives.scss
   │   ├── _color-semantic.scss   # vendored but NOT @forwarded
   │   └── _motion.scss
   └── styles/
       ├── _shadows.scss
       └── _colors.scss
   ```

3. **Compile the `foundation.css` barrel.** Run `sass` over the new
   `_index.scss` and commit
   `plugins/acss-kit/assets/foundation/foundation.css`. Document the
   exact `sass` version + CLI flags used in `SOURCE.md`. The compiled file
   must include the project-authored reduced-motion block (P3) and be
   wrapped in `@layer foundation { … }` (P4).

4. **Establish CSS layer ordering.** Document the canonical layer order in
   `skills/components/SKILL.md` and `skills/styles/SKILL.md`:

   ```css
   @layer foundation, components, utilities, theme;
   ```

   Cascade outcome: **theme > utilities > components > foundation**. Theme
   files (`light.css` / `dark.css` / `brand-*.css`) declare into the `theme`
   layer; component generators must wrap component CSS in
   `@layer components`; the `acss-utilities` bridge / utility files must
   declare into `@layer utilities`. Why: matches the Round 2a precedence
   decisions and removes import-order fragility.

5. **Update `/kit-add` first-run setup**
   (`plugins/acss-kit/commands/kit-add.md` + the `## First-Run Setup`
   section in `skills/components/SKILL.md`):

   - **First-run signal:** target dir does not contain `ui.tsx` AND does
     not contain `foundation.css`. Action: copy both
     `assets/foundation/foundation.css` and the full
     `assets/foundation/sass/` tree into the target dir
     (`src/components/fpkit/foundation.css` + `src/components/fpkit/foundation/sass/`).
   - **Existing-install signal:** target dir contains `ui.tsx` but **not**
     `foundation.css`. Action: print a prompt explaining the visual change
     (reset + base typography), the layer ordering, and the manual revert
     path. Only copy if the user confirms via `AskUserQuestion`.
   - **Already-installed signal:** target dir contains both. Action: skip
     silently (idempotent).
   - Print the import hint in all install branches:
     `Add to your app entry: import './components/fpkit/foundation.css'`.

   Why: prevents silent visual regressions on existing projects while
   making fresh installs zero-friction.

6. **Extend the foundation reference doc.** Edit
   `plugins/acss-kit/skills/components/references/components/foundation.md`
   (the existing UI primitive doc) — do **not** create a separate
   `foundation-css.md`. Add a top-level `## CSS Layer` section after the
   existing UI content covering:

   - Vendored upstream files + the four project patches (P1–P4) cross-linking
     to `SOURCE.md`.
   - The `@layer` order from step 4.
   - The `/kit-add` install matrix from step 5.
   - The manual revert path (delete `foundation.css` + remove the import).
   - A small verification table for the foundation (separate from the
     component verification table in `catalog.md`).

   Update `catalog.md`'s narrative to reference foundation only for
   discovery — do **not** add a row to the component verification table.

7. **Audit and integrate `kit-sync` manifest tracking.** Before editing
   `kit-sync`:

   - Read the `acss-kit:kit-sync` skill source and locate the
     `.acss-kit/manifest.json` schema (its install/sync logic).
   - Confirm the manifest tracks per-file metadata (path + checksum + version)
     so `foundation.css` and the `sass/` tree can be added without breaking
     existing entries.

   Then update `kit-sync` so:
   - Every existing install path that copies `ui.tsx` also copies the
     foundation files (mirroring step 5's matrix).
   - The manifest tracks `foundation.css` + each file under
     `foundation/sass/` for safe future updates.

   Why: keeps `/kit-sync` and `/kit-add` symmetric; the manifest audit
   was implicit in the original plan and risks rework otherwise.

8. **Extend `validate_theme.py` and theme-related scripts** to:

   - Add focus-on-surface pairings to `PAIRS`:
     `--color-focus-ring` × `--color-surface` (3:1) and
     `--color-focus-ring` × `--color-surface-raised` (3:1).
   - On every `/theme-create`, `/theme-brand`, `/theme-update`,
     `/theme-extract`, fail validation if either pair drops below threshold.

   Why: WCAG 1.4.11 requires focus indicators with 3:1 contrast against
   adjacent backgrounds; foundation introduces focus on surface elements
   (cards, popovers) the existing pair list doesn't cover.

9. **Bump version + changelog.** `plugins/acss-kit/.claude-plugin/plugin.json`
   minor bump. `plugins/acss-kit/CHANGELOG.md` must include both:

   - `### Added` — `foundation.css` + SCSS sources, `/kit-add` foundation
     install matrix, foundation install prompt for existing projects, two
     new `validate_theme.py` focus-on-surface pairings.
   - `### Changed` — `/kit-add` first-run output now copies foundation; CSS
     `@layer` ordering is now the canonical cascade contract for consumer
     projects. Existing projects must opt in via the prompt; no silent
     visual change.

   Run `/release-plugin acss-kit` per the root `CLAUDE.md` checklist.

10. **Test coverage** (extends `tests/run.sh` and `tests/e2e.sh`):

    **Structural (in `tests/run.sh`):**
    - `assets/foundation/foundation.css` exists and parses with `tinycss2`.
    - It does **not** redeclare any `--color-*` role in
      `assets/theme.schema.json` `$defs/palette` (enforces P1).
    - It contains the `@layer foundation { … }` wrapper (enforces P4).
    - It contains the `prefers-reduced-motion` media query (enforces P3).
    - The compiled CSS is byte-reproducible from the SCSS sources at the
      documented `sass` version (compile-and-diff in CI).
    - `SOURCE.md` lists patches P1–P4.

    **Render-level (in `tests/e2e.sh`, scaffold first):**
    - **Scaffold:** extend `tests/sandbox/` to load CSS files into jsdom
      (add a tiny harness that injects `foundation.css` + `light.css` into
      a `<style>` tag before rendering). Today's sandbox has no CSS
      pipeline — without this, the rest of the section is unimplementable.
    - Smoke test **3 representative components** (Button, Card, Input):
      render each with and without `foundation.css` loaded; capture
      `getComputedStyle()` snapshots for spacing, typography, and focus
      properties; flag unexpected deltas. Patch component `.scss` files
      whose visuals shift in ways that conflict with foundation defaults.
    - axe-core landmark check on a sample page combining the foundation +
      a layout: assert `main`/`navigation`/`region` roles are detectable
      and there are no new axe violations vs. the without-foundation
      baseline.

    Why: the test contract has to be implementable. Round 3 chose the
    "smoke 3 components" depth; the sandbox scaffolding is a prerequisite
    that the original plan glossed over.

## Critical files

- **Create:**
  - `plugins/acss-kit/assets/foundation/foundation.css` (compiled barrel)
  - `plugins/acss-kit/assets/foundation/sass/**` (vendored + project-authored
    sources)
  - `plugins/acss-kit/assets/foundation/SOURCE.md` (pin + patches P1–P4 +
    manual refresh commands)
- **Modify:**
  - `plugins/acss-kit/skills/components/references/components/foundation.md`
    (extended with `## CSS Layer` section — single doc, not split)
  - `plugins/acss-kit/commands/kit-add.md` (install matrix + prompt)
  - `plugins/acss-kit/skills/components/SKILL.md` (workflow + `@layer` order)
  - `plugins/acss-kit/skills/styles/SKILL.md` (`@layer` order documented)
  - `plugins/acss-kit/scripts/validate_theme.py` (extend `PAIRS`)
  - `plugins/acss-kit/.claude-plugin/plugin.json` (minor bump)
  - `plugins/acss-kit/CHANGELOG.md` (`Added` + `Changed`)
  - The `kit-sync` skill + `.acss-kit/manifest.json` schema (per step 7)
  - `tests/run.sh`, `tests/e2e.sh`, and `tests/sandbox/` (per step 10)

## Reuse / existing utilities

- `assets/foundation/ui.tsx` and its existing `foundation.md` reference —
  same file is *extended*, not duplicated.
- `scripts/validate_theme.py:PAIRS` — extend; do not fork.
- `tests/run.sh` + helpers in `tests/lib/` (already use `tinycss2`) —
  extend; do not introduce a new test runner.
- `acss-utilities` token-bridge convention — utilities must declare into
  `@layer utilities` to honor step 4's ordering.

## Alternatives considered

- **Embedded-markdown for each foundation module.** Rejected: foundation is
  upstream-owned and rarely customized; vendoring matches the `ui.tsx`
  precedent and keeps refresh trivial.
- **Single hand-authored `foundation.css`.** Rejected: drifts from upstream
  immediately and forfeits refresh.
- **Source-only ship (consumer compiles).** Rejected: breaks consumers
  without a SCSS toolchain.
- **No `@layer`, document import order only.** Rejected: too fragile when
  consumers reorder imports or use bundlers that hoist CSS.

## Verification

1. `tests/run.sh` is green (extends step 10).
2. `tests/e2e.sh` axe-core run reports no new violations on the rendered
   sandbox page; computed-style snapshots for Button/Card/Input show only
   intentional deltas.
3. Local install: `claude --plugin-dir ./plugins/acss-kit`. In a fresh
   React + sass project, run `/kit-add button`. Confirm:
   - `foundation.css` and the `sass/` tree are copied alongside `ui.tsx`,
   - the import hint is printed,
   - re-running `/kit-add card` does **not** re-copy or re-prompt.
4. In a *separate* scratch project that already has `ui.tsx` but no
   `foundation.css` (simulate an existing install), run `/kit-add card`.
   Confirm the existing-install prompt fires and copies only on confirm.
5. Render the resulting Button + Card + Input in a minimal Vite app with
   `foundation.css` + `light.css` loaded; confirm DevTools shows base
   typography active for `<h1>`/`<p>`/`<ul>`/`<a>`, focus ring renders on
   surfaces, `--color-*` values still come from `light.css`.
6. Toggle `prefers-reduced-motion` in DevTools; confirm motion duration
   tokens collapse to zero.

## Next Steps (out of scope)

- **Catalog cleanup.** `references/components/catalog.md` documents Tag,
  Badge, Heading, Text, Details, Progress with full Generation Contracts,
  but their SCSS isn't shipped. Move these into a clearly-labelled
  "Specifications (not yet shipped)" section, OR ship the missing SCSS, so
  `/kit-add badge` doesn't generate broken output.
- Layout primitives missing from acss-kit references: Box, Stack, Cluster,
  Grid, Flex, Landmarks — author embedded-markdown reference docs.
- Components missing entirely: Breadcrumbs, Title, TextToSpeech.
- Add a `foundation-refresh` maintainer skill that re-vendors from a
  sibling `acss/` clone at a chosen tag, recompiles, and updates
  `SOURCE.md`.
- `brand-template.css`: add commented-out hints for non-color brand
  overrides (motion duration, shadow tone) so brands can tune the new
  Tier-2 surface.

## Unresolved Questions

_None — all open questions resolved during the plan-interview stress
test (see Interview Summary)._

---

## Interview Summary

Stress-tested via `/plan-interview:plan-interview` on 2026-05-07. The
canonical record is below; steps 1–10 above already reflect every
decision.

### Plan Naming
| Element | Current → New | Issue |
|---|---|---|
| Filename | `some-of-the-styles-transient-noodle.md` → `vendor-fpkit-foundation-css.md` | Random adjective-noun pattern, unrelated to content. **Renamed** with user approval. |
| H1 Heading | `# Vendor fpkit foundation CSS into acss-kit` | Already descriptive — no change. |

### Key Decisions Confirmed

- **Token reconciliation:** Drop `tokens/_color-semantic.scss` from the
  index; theme files own every `--color-*` role (P1).
- **Compile mode:** Pre-compiled `foundation.css` **and** SCSS sources
  copied to consumer projects.
- **Backward compatibility:** Detect-and-prompt when an existing install
  (`ui.tsx` present, `foundation.css` absent) hits `/kit-add`. Never
  silent.
- **Visual reset opt-out:** Single barrel, no opt-out toggle. Closes the
  open question in the original plan.
- **Layer precedence:** Use CSS `@layer` (`foundation, components,
  utilities, theme`) so theme always wins; utilities beat foundation;
  components beat foundation. Documented load order alone is too fragile.
- **Reduced motion:** Token-level — project-authored
  `@media (prefers-reduced-motion: reduce) { :root { --transition: none; --tran-all: none; } }`
  block appended to `foundation.css` (P3).
- **Visual regression strategy:** Smoke-test 3 representative components
  (Button, Card, Input) for computed-style deltas; manual side-by-side
  audit; patch component `.scss` files where conflicts surface.
- **Focus styling:** Foundation `_globals.scss` ships a base `:focus-visible`
  using `--color-focus-ring`; components override per-element.
- **Heading color:** Patch `_type.scss` to use
  `color: var(--color-text, #212529)` per
  `.claude/rules/scss-conventions.md` (P2).
- **Landmark a11y:** axe-core landmark check in `tests/e2e.sh`.
- **Focus contrast:** Extend `validate_theme.py:PAIRS` with
  focus-on-surface and focus-on-surface-raised pairings.
- **kit-sync integration:** Audit and integrate fully in this PR, not
  deferred.
- **Refresh workflow:** Manual — documented `gh api` / `cp` / `sass`
  commands in `SOURCE.md`. No new script or skill in this PR.
- **Versioning:** Minor bump with both `### Added` and `### Changed`
  CHANGELOG entries.

### Open Risks & Concerns

- **Phantom components in `catalog.md`.** Tag/Badge/Heading/Text/Details/
  Progress are documented but unshipped. Surfaced in Next Steps; not
  addressed in this PR.
- **`tests/sandbox/` lacks a CSS pipeline.** Step 10 includes scaffolding
  work to inject CSS into jsdom; without it, render-level tests are
  unimplementable.
- **Patch surface = 4 project-authored modifications** (P1–P4). The
  framing is now "vendored with documented patches," not "verbatim."
  `SOURCE.md` enumerates each.
- **No automated rollback path.** Documented manual revert (delete file +
  remove import) is sufficient for v1.
- **Heading verification table location.** Foundation gets its own
  verification table inside `foundation.md`'s new `## CSS Layer` section,
  not a row in `catalog.md`'s component table.

### Recommended Next Steps (folded into the plan above)

1. ✅ Single foundation reference doc — `foundation.md` extended, not split.
2. ✅ kit-sync audit before integration — explicit step 7 prerequisite.
3. ✅ `tests/sandbox/` CSS pipeline scaffolding — explicit in step 10.
4. ✅ `@layer` wrapping documented in step 4.
5. ✅ `SOURCE.md` enumerates patches P1–P4 — explicit in step 1.
6. ✅ CHANGELOG `Added` + `Changed` — explicit in step 9.
7. ✅ `catalog.md` cleanup — added to Next Steps.

### Simplification Opportunities Adopted

- **Single foundation reference doc** (extend `foundation.md`).
- **Flat directory was considered** for `assets/foundation/sass/`; nested
  layout retained because it makes refresh-via-`cp` trivial. Trade-off
  documented in Alternatives considered.
