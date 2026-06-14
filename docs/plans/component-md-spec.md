---
status: proposed
type: feature
created: 2026-06-14
repo-name: acss-plugins
---

# Plan: COMPONENT.md spec (Workstream B)

> Execution plan for **roadmap PR 0** of
> [`design-md-spec-alignment.md`](design-md-spec-alignment.md). Authors a
> documented, versioned **COMPONENT.md** format — the implementation-layer
> sibling to Google Labs' DESIGN.md token layer — and houses it in the
> framework-agnostic `style-agent` plugin. **Docs-only; no code, no component
> rewrites.** Decisions from the 2026-06-14 review are assumed: `COMPONENT.md`
> is owned by `style-agent`; it references **primitive** DESIGN.md token groups
> (`{colors.*}`, `{spacing.*}`, `{rounded.*}`, `{typography.*}`), not
> `components.*`.

## Context

DESIGN.md is published as a portable spec (`docs/spec.md`, `version: alpha`, a
consumer-behavior table, a lint-rules contract). Our equivalent for *components*
— the 9-section embedded-markdown shape in
`plugins/acss-kit/skills/component-*/reference.md` — is equally rigorous but
only encoded implicitly inside the `acss-kit-component-author` maintainer skill
and `kit-core`'s Step B. Nothing documents it as a standalone, conformance-
checkable format.

This plan extracts that shape into a **COMPONENT.md spec** that:

- mirrors DESIGN.md's bipartite form (YAML front-matter + markdown body);
- carries a `{token.path}` reference syntax that points **into** a sibling
  DESIGN.md, making the two a **two-file design system** (tokens + components);
- lives in `style-agent` so it is framework-neutral and publishable —
  `acss-kit`'s `reference.md` docs *conform to* it rather than own it.

The format is **one file per component** (`<name>.component.md`), matching how
`reference.md` is one-per-component; the spec describing the format is a single
`spec.md`, exactly as DESIGN.md ships `DESIGN.md` instances plus `docs/spec.md`.

## Objective

Land a single docs-only PR in `style-agent` that adds the COMPONENT.md `spec.md`,
one worked example, an advisory rule, doc/changelog updates, and a version bump —
with `tests/run.sh` green and no behavior change to any existing plugin.

## Coupling sites (audit before writing)

Run `grep -rn "reference.md\|embedded-markdown\|Generation Contract" .claude/ plugins/acss-kit/skills/acss-kit-component-author plugins/acss-kit/skills/kit-core docs/` and capture matches. The spec must **describe the existing shape faithfully** — it is documentation of a real contract, so any divergence between the spec text and what `kit-core` Step B actually consumes is a defect. Known sources of truth to reconcile against:

- `plugins/acss-kit/skills/component-button/reference.md` — canonical instance.
- `.claude/skills/acss-kit-component-author/SKILL.md` — the scaffolder that encodes the shape today.
- `plugins/acss-kit/skills/kit-core/SKILL.md` Step B — the consumer (which sections it requires: Generation Contract, TSX Template, SCSS Template, Accessibility).

*Why:* the spec's authority comes from matching the live contract; an aspirational spec that drifts from `kit-core` would mislead authors. *Verify:* the `## Section order` table in the spec lists exactly the sections `reference.md` uses, and the "required" subset matches what `kit-core` Step B enforces.

## Steps

1. **Create the spec at `plugins/style-agent/docs/component-md/spec.md`.** Mirror DESIGN.md/spec.md's structure. Required content:
   - **Purpose & philosophy** — implementation-layer sibling to DESIGN.md; bipartite (front-matter + prose); humans + agents.
   - **Front-matter schema** — `spec: component.md`, `version: alpha`, `name`, `element`, `verified-against` (the fpkit pin), `tokens` map (values are `{token.path}` refs into DESIGN.md primitives), `variants` map, `props` map (values/required/type/a11y), `a11y` (WCAG criteria list).
   - **Section order** — the 9 body sections (Verification banner, Overview, Generation Contract, Props Interface, TSX Template, CSS Variables, SCSS Template, Accessibility, Usage Examples), marking which are **required** (Generation Contract, TSX Template, SCSS Template, Accessibility — matching `kit-core` Step B) vs. optional.
   - **Token-reference syntax** — `{group.token}` resolving against a project's DESIGN.md; **primitive groups only**; behavior when no DESIGN.md is present (fall back to the CSS-variable `var(--x, <fallback>)` form).
   - **Consumer-behavior table** — unknown section → preserve; **duplicate required section → reject**; missing required section → error; unknown front-matter key → warn. (Aligned with DESIGN.md's table.)
   - **Relationship to DESIGN.md** — the two-file model; COMPONENT.md references primitives, never DESIGN.md `components.*`.
   - **Versioning** — `alpha`, expect change.
   - *Why:* this is the deliverable — a single authoritative document an author or agent reads to produce a conformant `<name>.component.md`. *Verify:* file exists; `grep -c '^## ' spec.md` shows the documented sections; the front-matter schema block and consumer-behavior table are present; no reference to `components.*` as a COMPONENT.md target.

2. **Add a worked example `plugins/style-agent/docs/component-md/examples/button.component.md`.** Promote Appendix E of the proposal into a complete, conformant instance: full front-matter (tokens referencing `{colors.primary}`, `{spacing.sm}`, `{typography.label-md}`, …) plus the 9-section body reusing the existing acss-kit button TSX/SCSS/Accessibility content verbatim.
   - *Why:* a spec without a reference instance is untestable; this doubles as the fixture for any future validator and as copy-paste scaffolding. *Verify:* the example contains every **required** section named in the spec; every `{token.path}` in its `tokens:` block uses a primitive group; a reader can map it 1:1 to `component-button/reference.md`.

3. **Add advisory rule `.claude/rules/component-md.md`.** Front-matter `paths: ["**/*.component.md", "plugins/style-agent/docs/component-md/**"]`. Body: remind of section order, required-section set, `{token.path}` primitive-only syntax, and "conform to `docs/component-md/spec.md`." Add a row to `.claude/rules/README.md`'s status table.
   - *Why:* rules are how this repo keeps a convention present every time a matching file is touched (same pattern as `scss-conventions.md`); it makes the spec self-reinforcing without a hook. *Verify:* rule file has a `paths:` array; `.claude/rules/README.md` table has a new row; opening a `*.component.md` would surface the reminder.

4. **Update `style-agent` docs.** In `plugins/style-agent/docs/README.md` add a short "Specs" section pointing at `docs/component-md/spec.md` and the example. In `plugins/style-agent/README.md` add a one-line mention under a "Specifications" heading (no new command yet).
   - *Why:* discoverability — the developer guide is where contributors look. *Verify:* both files link to `docs/component-md/spec.md`; links resolve.

5. **Bump `style-agent` version and changelog.** In `plugins/style-agent/.claude-plugin/plugin.json` bump `0.4.0 → 0.5.0` (new user-facing artifact, additive → minor). Add a `## [0.5.0]` Keep-a-Changelog entry under **Added**: "COMPONENT.md spec — versioned format for component implementation docs that reference DESIGN.md tokens." Do **not** add a `version` to `marketplace.json`.
   - *Why:* repo convention — `plugin.json` is authoritative; CHANGELOG tracks user-facing change; marketplace omits version. *Verify:* `plugin.json` reads `0.5.0`; CHANGELOG has the dated entry; `marketplace.json` has no `version` key.

6. **Update `marketplace.json` description (if user-facing).** Append a clause to the `style-agent` entry's `description` noting the COMPONENT.md spec, and consider a `component-md` / `design-tokens` tag.
   - *Why:* pre-submit checklist item 4 — keep the marketplace blurb current when behavior/artifacts change. *Verify:* description mentions the spec; entry still has no `version` field.

7. **Run the pre-submit checklist.** `tests/run.sh` green; confirm no SKILL.md/`plugin.json`/command front-matter validations regressed (this PR adds none of those, but the hooks run on any edit). If `tests/run.sh` has no notion of `style-agent` docs, leave it — adding a spec-conformance test step is deferred to the validator PR (Workstream A / a later COMPONENT.md-validate effort), not this docs-only PR.
   - *Why:* the repo's one-command gate must stay green. *Verify:* `tests/run.sh` exits 0.

## Out of scope (deferred to later roadmap PRs)

- **No `validate_component_md.py`** and no `/component-md` command — the spec is docs-only here. A validator + hook is a follow-on (parallels `validate_design_md.py`).
- **No changes to `acss-kit`'s `reference.md` files** — conforming the 15 existing docs to the spec (and the token-reference rewrite) rides with the Workstream A token-homes/sweep PRs (1–3), where the `{token.path}` targets actually exist.
- **No DESIGN.md tooling** — that is Workstream A (PRs 1, 4).

## Pre-submit checklist (from CLAUDE.md)

1. `tests/run.sh` green.
2. `plugin.json` version bumped (`style-agent` 0.4.0 → 0.5.0).
3. No fpkit source references introduced that aren't full GitHub URLs (spec should reference fpkit only via the existing pinned-URL convention if at all).
4. `marketplace.json` description updated.
5. `style-agent` `README.md` + `CHANGELOG.md` updated.
6. No scripts/plugins renamed or removed — no `python-scripts.md` / `settings.json` changes needed.

## Follow-on

After this lands, the next roadmap step is Workstream A: token homes
(`typography.css` / `space-radius.css`, schema growth) in `acss-kit`, then the
`design_md_to_tokens.py` adapter consuming `css-tailwind`. Conforming the 15
`reference.md` docs to this spec happens there, as part of the phased sweep.
