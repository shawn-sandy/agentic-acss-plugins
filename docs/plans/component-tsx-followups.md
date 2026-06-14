---
status: proposed
type: fix
created: 2026-06-14
repo-name: acss-plugins
---

# Plan: component TSX follow-ups (deferred from PR #89)

> Surfaced by CodeRabbit review on **PR #89** (the spacing/radius token sweep).
> PR 3 is an **SCSS** sweep, so its golden guard was scoped to SCSS and the
> `.tsx` golden fixtures were dropped — they dragged pre-existing TSX-template
> and test-extractor issues into review. Those genuine issues are tracked here.
> None are caused by the token sweep.

## Items

1. **`extract_full.mjs` dedup gap — duplicate type aliases (Critical).**
   `dedupeExportedTypes()` only dedupes brace-object declarations
   (`export type X = {`). Union/intersection aliases declared in **both** the
   `## Props Interface` and `## TSX Template` sections are emitted twice, so the
   extracted TSX for `list` (`ListType`, `ListItemType`), `icon` (`IconName`),
   and `icon-button` (`WithAriaLabel`, `WithAriaLabelledBy`, `IconButtonProps`)
   contains duplicate identifiers that `tsc` rejects. `tests/run.sh` only
   syntax-parses (not type-checks), so it stays green; `tests/e2e.sh` (`tsc
   --noEmit`) would catch it.
   - *Fix:* extend `dedupeExportedTypes` to track **any** `export type <Name> =`
     (union/intersection/conditional), dropping subsequent re-declarations,
     handling multi-line declarations until the type terminates.
   - *Verify:* `tests/e2e.sh` type-checks all extracted components clean.
   - *Then:* reintroduce `.tsx` golden fixtures (now valid TS) — ideally during
     the COMPONENT.md inversion (roadmap PR 7).

2. **`dialog`: `description` not linked via `aria-describedby` (Major, a11y).**
   The TSX template renders the description but never wires
   `aria-describedby`/the description id, so the prop contract is unmet.
   - *Fix:* in `component-dialog/reference.md` TSX, generate a `descriptionId`
     when `description` is set (mirroring `titleId`), apply it to the description
     element, and add `aria-describedby={descriptionId}` to the dialog.

3. **`popover`: `renderTrigger` clones without `isValidElement` guard (Major).**
   `trigger` is typed `React.ReactNode` but `React.cloneElement` is called
   unguarded — a string/number trigger crashes at runtime.
   - *Fix:* guard with `React.isValidElement(trigger)` (or type `trigger` as
     `React.ReactElement`).

4. **`input`: `onEnter` fires before `onKeyDown` (Minor).**
   Inverted order vs. the declared behavior.
   - *Fix:* call `onKeyDown?.(e)` first, then
     `if (!e.defaultPrevented && e.key === 'Enter') onEnter?.(e)`.

## Decided non-issues (skipped, not tracked)

- **`currentColor` → `currentcolor`** (popover.scss, etc.) — valid CSS, used
  consistently kit-wide; a stylelint-casing preference, not a repo standard.
- **`clip` → `clip-path`** (icon-button sr-only) — the classic visually-hidden
  pattern; broad support, pre-existing.
- **`card.tsx` "imports after types"** — false positive; ES module imports are
  hoisted, so a type alias above an `import` is legal and `tsc`-clean. The golden
  guard was green (no drift).

## Sequencing

Item 1 is a prerequisite for reintroducing `.tsx` goldens. Items 2–4 are small
source-template fixes that change generated component behavior, so they suit a
focused "component-template fixes" PR (each with a regenerated golden once the
extractor dedup lands).
