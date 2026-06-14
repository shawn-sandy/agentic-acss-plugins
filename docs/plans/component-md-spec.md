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
> rewrites.** Decisions assumed: `COMPONENT.md` is owned by `style-agent`;
> references **primitive** DESIGN.md token groups (`{colors.*}`, `{spacing.*}`,
> `{rounded.*}`, `{typography.*}`), not `components.*`; and — per
> [`../proposals/component-md-framework-agnostic.md`](../proposals/component-md-framework-agnostic.md)
> — the format is **framework-neutral / neutral-first**: a semantic-HTML source
> of truth with React/HTML/Astro/Angular/Vue/Svelte/web-component as **agent-
> projected targets**, React expressed as the first `## Target:` adapter.

## Context

DESIGN.md is published as a portable spec (`docs/spec.md`, `version: alpha`, a
consumer-behavior table, a lint-rules contract). Our equivalent for *components*
— the embedded-markdown shape in
`plugins/acss-kit/skills/component-*/reference.md` — is equally rigorous but
only encoded implicitly inside the `acss-kit-component-author` maintainer skill
and `kit-core`'s Step B, and it is **React-shaped** (TSX template, TS props).

The framework-agnostic investigation
([`../proposals/component-md-framework-agnostic.md`](../proposals/component-md-framework-agnostic.md))
established that a component's **structure (semantic HTML), styling (CSS +
tokens), and accessibility are framework-neutral** — only template syntax and
reactivity vary. So this plan authors a **neutral-first COMPONENT.md spec**:

- bipartite form (YAML front-matter + markdown body), like DESIGN.md;
- a **neutral contract** as the source of truth — semantic structure + abstract
  props + tokens + accessibility + a behavior spec — with a `## Target:
  <framework>` extension mechanism for idiom hints/templates;
- `{token.path}` references **into** a sibling DESIGN.md (the two-file design
  system: DESIGN.md owns tokens, COMPONENT.md owns components);
- lives in `style-agent`; `acss-kit`'s React docs become one **`## Target: react`**
  adapter that *conforms to* the spec.

The format is **one file per component** (`<name>.component.md`); the spec
describing it is a single `spec.md`, exactly as DESIGN.md ships `DESIGN.md`
instances plus `docs/spec.md`.

## Objective

Land a single docs-only PR in `style-agent` that adds the COMPONENT.md `spec.md`,
one worked example, an advisory rule, doc/changelog updates, and a version bump —
with `tests/run.sh` green and no behavior change to any existing plugin.

## Coupling sites (audit before writing)

Run `grep -rn "reference.md\|embedded-markdown\|Generation Contract" .claude/ plugins/acss-kit/skills/acss-kit-component-author plugins/acss-kit/skills/kit-core docs/` and capture matches. The spec must **describe the existing shape faithfully** — it is documentation of a real contract, so any divergence between the spec text and what `kit-core` Step B actually consumes is a defect. Known sources of truth to reconcile against:

- `plugins/acss-kit/skills/component-button/reference.md` — canonical instance.
- `.claude/skills/acss-kit-component-author/SKILL.md` — the scaffolder that encodes the shape today.
- `plugins/acss-kit/skills/kit-core/SKILL.md` Step B — the consumer (which sections it requires: Generation Contract, TSX Template, SCSS Template, Accessibility).

*Why:* the spec's authority comes from matching the live contract; an aspirational spec that drifts from `kit-core` would mislead authors. Under neutral-first, the React projection lives in the spec's **`## Target: react`** adapter, and *that* adapter must reproduce exactly what `kit-core` Step B consumes (Generation Contract, TSX Template, SCSS Template, Accessibility) — so existing `/kit-add` output is unchanged. *Verify:* the spec's neutral section list + the `## Target: react` adapter together cover every section `reference.md` uses today, and the React adapter's required subset matches `kit-core` Step B.

## Steps

1. **Create the spec at `plugins/style-agent/docs/component-md/spec.md`** (neutral-first). Mirror DESIGN.md/spec.md's structure. Required content:
   - **Purpose & philosophy** — implementation-layer sibling to DESIGN.md; bipartite (front-matter + prose); humans + agents; **framework-neutral, agent-projected**.
   - **Front-matter schema** — `spec: component.md`, `version: alpha`, `name`, `element` (semantic host), `role` (ARIA), `tokens` map (`{token.path}` into DESIGN.md primitives), **`props` map (abstract: values/required/default/`maps-to`/a11y)**, `slots`, `variants` (with `maps-to`), `behavior` (ref to the Behavior section), `a11y` (WCAG list), **`targets`** (`[react, html, astro, angular, vue, svelte, web-component]`).
   - **Neutral body sections** (the source of truth): **Overview · Semantic Structure** (the canonical semantic-HTML template — element tree, `data-*`, ARIA, slot comments) **· Props** (abstract table) **· Tokens & CSS Variables · Styles** (CSS) **· Behavior** (spec: triggers/state/invariants/ARIA effects + a neutral `init(root)` reference) **· Accessibility · Examples** (neutral HTML). Mark the **required** subset (Semantic Structure, Styles, Accessibility, Behavior-if-stateful).
   - **`## Target: <framework>` extension** — the mechanism for per-framework adapters: idiom hints, or a full template where projection needs steering. Specify that the **`react` target** carries the Generation Contract + TSX Template + TS props (so `kit-core` Step B is satisfied), and that purely presentational components need no target blocks (pure agent projection).
   - **Projection model** — agent reads the neutral contract + requested target and generates idiomatic code; `web-component` is a selectable universal target. (Per the framework-agnostic investigation.)
   - **Token-reference syntax** — `{group.token}` resolving against a project's DESIGN.md; **primitive groups only**; fallback to `var(--x, <fallback>)` when no DESIGN.md is present.
   - **Consumer-behavior table** — unknown section → preserve; **duplicate required section → reject**; missing required section → error; unknown front-matter key → warn; **unknown `## Target:` → preserve** (best-effort projection). 
   - **Relationship to DESIGN.md** — two-file model; references primitives, never `components.*`.
   - **Versioning** — `alpha`.
   - *Why:* this is the deliverable — one authoritative document an author or agent reads to produce a conformant, multi-target `<name>.component.md`. *Verify:* file exists; the neutral section list + `## Target:` mechanism are documented; the `react` target's required subset matches `kit-core` Step B; front-matter schema + consumer-behavior table present; no `components.*` target.

2. **Add a worked example `plugins/style-agent/docs/component-md/examples/button.component.md`** (neutral-first). Front-matter with abstract `props`, `tokens` (`{colors.primary}`, `{rounded.md}`, `{spacing.sm}`, `{typography.label-md}`), `slots`, `targets`. Neutral body: Semantic Structure (button's existing HTML Template), Props table, Tokens/CSS Variables, Styles (button.scss), Behavior (the disabled-activation-guard spec + the existing Vanilla-JS `init` as the reference), Accessibility (verbatim), neutral HTML Examples. Then a **`## Target: react`** block carrying the existing TSX Template + Generation Contract + TS `ButtonProps`.
   - *Why:* button is the ideal example — it already has both the neutral (HTML/CSS/JS/a11y) and React layers, so it proves the inversion with zero new authoring. It doubles as the validator fixture and `/kit-add`-parity check. *Verify:* the example has every **required** neutral section; the `## Target: react` block reproduces today's `component-button/reference.md` TSX/Contract byte-for-byte; every `{token.path}` uses a primitive group; an agent could project an Astro/Angular version from the neutral sections alone.

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
- **No changes to `acss-kit`'s `reference.md` files** — the neutral-first
  **inversion** (extracting/normalizing the neutral layers for all 15, adding
  abstract props + behavior specs, demoting TSX to a `## Target: react` block) is
  **gated on the generator refactor** (`/kit-add` reading COMPONENT.md) and ships
  with it (spec-driven generation, roadmap PR 7) — **not** with the Workstream A
  token sweep, which edits `reference.md` in place (PR 2–3). Inverting before the
  generator consumes COMPONENT.md would break generation. This plan only authors
  the spec + one example.
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
