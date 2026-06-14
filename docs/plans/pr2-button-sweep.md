---
status: proposed
type: feature
created: 2026-06-14
repo-name: acss-plugins
---

# Plan: PR 2 — button sweep pilot (Workstream A)

> Executable plan for **roadmap PR 2** of
> [`design-md-token-parity.md`](design-md-token-parity.md). Sweeps
> **`component-button/reference.md`** so its styles consume the
> `--space-*` / `--radius-*` / `--font-*` token homes shipped in PR 1, fixes the
> `--color-primary-dark` debt, and locks the result with a golden test. **In-place
> edit of `reference.md`** — the COMPONENT.md inversion is gated on the generator
> refactor (PR 7) and is **not** in scope here (see the sequencing note in the
> master proposal).

## Context

PR 1 landed the token homes (`--space-*`, `--radius-*`, `--font-*` with
`var(--x, <fallback>)` defaults, validated by `validate_tokens.py`). PR 2 is the
**pilot** that proves the component-sweep pattern on one component before the
bulk pass (PR 3, ~150 sites across 14 components). `button` is the right pilot:
it's the dep-leaf for many components and exercises every token kind.

## The mapping discipline (the crux — this is what the pilot establishes)

The sweep is **not** a blind literal→token find-replace. Three rules:

1. **Value-preserving via fallback.** Every swap keeps the *original literal as
   the `var()` fallback*: `border-radius: var(--radius-md, 0.375rem)`. With **no
   DESIGN.md / token files imported**, the fallback applies → the component
   renders **pixel-identical** to today. With token files present, the value
   intentionally shifts to the theme — that *is* the feature.
2. **Map to the nearest semantic step; don't invent exactness.** Button's radius
   `0.375rem` has no exact scale step (`--radius-sm`=.25, `--radius-md`=.5). Map
   to the nearest semantic role (`--radius-md`) and preserve `0.375rem` as the
   fallback. The fallback guarantees no visual change until themed.
3. **Don't sweep intentional non-scale values.** Leave alone: font-size-relative
   `calc()` (button padding is `calc(var(--btn-fs) * 0.5)` — responsive by
   design), component-local *variant scales* (button's `--btn-size-xs…xl` are a
   size-variant ladder, not semantic typography roles), and structural literals
   (`2px solid currentColor` focus outline, `1px` borders, `999px` pill,
   `100%`/`50%`).

These three rules are the **policy the bulk sweep (PR 3) inherits.**

## Steps

1. **Apply the button swaps** to `component-button/reference.md` — both the
   `## CSS Variables` and `## SCSS Template` sections — per the swap table in the
   appendix. Each swap wraps the existing value in `var(--<token>, <original>)`.
   - *Why:* makes button consume the PR-1 token homes so a DESIGN.md/`/theme-*`
     reskins it, with zero visual change until themed. *Verify:* every swapped
     declaration is `var(--space|radius|font-*, <original-literal>)`; no bare
     swept literal remains; `calc()` paddings and variant-scale sizes untouched.

2. **Fix the `--color-primary-dark` debt.** `--btn-primary-hover-bg:
   var(--color-primary-dark, #0052a3)` references a role that is **not** one of
   the 18 canonical roles (the schema defines `--color-primary-hover`). Repoint
   to `var(--color-primary-hover, #0052a3)`.
   - *Why:* a live bug — button's themed hover silently falls back today.
     *Verify:* `grep -rn 'color-primary-dark' plugins/acss-kit` returns nothing;
     the hover declaration references `--color-primary-hover`.

3. **Value-preservation check (one-time).** Extract the button SCSS from
   `reference.md` before and after the sweep; compile each with **no token files
   present**; assert the computed declarations are identical (the fallbacks
   reproduce the originals).
   - *Why:* proves rule 1 — the no-DESIGN.md path is byte-for-pixel unchanged.
     *Verify:* a diff of the two compiled outputs is empty (modulo the
     intentional `--color-primary-dark` → `--color-primary-hover` fallback hex,
     which is identical `#0052a3`).

4. **Golden snapshot + `tests/run.sh` guard.** Capture the **post-sweep** output
   `/kit-add button` produces (`button.tsx` + `button.scss`) into
   `tests/fixtures/golden/component-button/`, and add a `run.sh` step that
   extracts button from `reference.md` and diffs against the golden.
   - *Why:* locks the swept output so future edits can't silently regress it
     (the same golden discipline used for the component-skill split). *Verify:*
     the new `run.sh` step is green on this branch; intentionally perturbing
     `button.scss` on a throwaway commit makes it fail; revert.

5. **Pre-submit.** `tests/run.sh` green; bump `acss-kit` (minor — generated
   button output is now token-aware) via `/release-plugin acss-kit`; CHANGELOG
   entry under Added/Changed.
   - *Verify:* `tests/run.sh` exits 0; `plugin.json` bumped; CHANGELOG dated
     entry present; `marketplace.json` unchanged (no behavior surface change).

## Out of scope

- **The other 14 components** — PR 3 (bulk sweep), which applies this exact
  mapping discipline.
- **`alert` state-color wiring** — PR 3.
- **`reference.md` → `COMPONENT.md` inversion** — gated on the generator refactor
  (PR 7); PR 2 edits `reference.md` in place.

## Appendix — button swap table

From `component-button/reference.md` (`## CSS Variables` + `## SCSS Template`):

| Current | Action | Becomes | Note |
|---|---|---|---|
| `--btn-gap: 0.5rem` | swap | `var(--space-sm, 0.5rem)` | exact step match |
| `--btn-radius: 0.375rem` | swap | `var(--radius-md, 0.375rem)` | nearest step; fallback preserves |
| `--btn-fw: 500` | swap | `var(--font-label-md-weight, 500)` | button label ≈ label-md |
| `--btn-primary-hover-bg: var(--color-primary-dark, #0052a3)` | **fix** | `var(--color-primary-hover, #0052a3)` | non-canonical role bug |
| `--btn-padding-block/inline: calc(var(--btn-fs) * …)` | **keep** | — | fs-relative by design (rule 3) |
| `--btn-size-xs…xl` | **keep** | — | component-local variant scale, not a semantic role (rule 3) |
| `--btn-fs: var(--btn-size-md, 0.9375rem)` | **keep** | — | resolves through the variant scale |
| `--btn-focus-outline: 2px solid currentColor` | **keep** | — | structural, not a scale token |
| `border-radius: 999px` (pill), `50%` (icon) | **keep** | — | structural shape literals |
| `--btn-primary-bg: var(--color-primary, …)` etc. | **keep** | — | already role-based |

Net for button: **3 swaps + 1 fix.** The deliberately-small set is the point —
the pilot proves the *discipline* (fallback-preserving, nearest-step, skip
intentional non-scale), which the ~150-site bulk sweep then applies at scale.
