---
status: in-progress
type: refactor
created: 2026-05-21
repo-name: acss-plugins
---

# Plan: Split acss-kit components into per-component skills

> **Filename rename pending**: this plan will be renamed to `split-acss-kit-components-into-skills.md` as commit 1 of execution (`git mv` to preserve history). Plan-mode forbade the move during stress-test.

## Context

`plugins/acss-kit/skills/components/SKILL.md` is a 1,383-line monolith that handles every component via reference docs under `skills/components/references/components/`. A single skill description triggers for *any* component request, the reference docs are inert markdown, and adding a new component means editing both `references/components/<name>.md` and `catalog.md`.

The user wants each component to be its own skill so:

- **Auto-triggering becomes precise** — a "create a dialog" prompt fires `component-dialog`, not a generic match against the whole catalog.
- **Components are extensible by drop-in** — adding a new component is "scaffold a new skill directory," not "edit a monolith + a catalog row."
- **Developers using and authoring components see the same unit of work** — a skill folder.

Decisions locked in via stress-test interview: **full skill dirs** (content moves into the skill folder); **all 15 documented components** (alert, button, card, checkbox, dialog, field, icon, icon-button, img, input, link, list, nav, popover, table) — inline-only catalog entries (Badge, Tag, Heading, Text, Details, Progress) stay separate; **modes stay centralized** in `kit-core/` (Creator, Form, HTML Target, Style-Tune); **inline reference delegation** (no skill-to-skill invocation — each per-component SKILL.md carries its own short workflow and references `kit-core/references/` for shared constraints); **POC-first migration** (PR 1 = kit-core + component-button alone alongside the existing layout; PR 2 = bulk-migrate remaining 14).

## Objective

Restructure `plugins/acss-kit/skills/` so each component lives in its own `component-<name>/` skill directory with its own `SKILL.md` and `reference.md`, while orchestration and cross-cutting modes live in a renamed `kit-core/` skill — landing in two coordinated PRs.

## PR 1 — Foundation: kit-core extraction + component-button POC

1. **Pre-flight repo grep.** Run `grep -rn "references/components\|skills/components" plugins/ .claude/ tests/ docs/` and capture every match as a checklist of paths needing update. Document the full list inside this plan file under a new `## Coupling Sites` section before any move happens. Audit must include: `.claude/rules/fpkit-references.md` glob, the `component-reference-reviewer` agent path resolution, `/prompt-book` example prompts, sibling plugins (`acss-utilities`, `style-agent`), and any docs under `plugins/acss-kit/docs/`.
   - *Why:* `references/components/` is referenced from at least five places outside the components skill itself. Surfacing them upfront eliminates the "we moved the directory and three things silently broke" failure mode.
   - *Verify:* `## Coupling Sites` section exists in this plan, listing every match with file + line. Re-running the grep on the new layout (after PR 2) returns zero hits.

2. **Capture golden-output baseline for `component-button` against the current layout.** Run `/kit-add button` against a clean `tests/sandbox/` from current `main`. Copy generated `ui/Button.tsx` and `Button.module.scss` into `tests/fixtures/golden/component-button/`. Add a new `tests/run.sh` step (numbered after the existing TSX validator) that runs `/kit-add button` against a fresh sandbox and diffs against the golden. Failing this check blocks the PR.
   - *Why:* The whole refactor's premise is that templates move byte-identically. A golden test makes that premise mechanical, not aspirational, and catches whitespace/encoding drift that visual review misses.
   - *Verify:* `tests/fixtures/golden/component-button/Button.tsx` and `Button.module.scss` exist. `tests/run.sh` includes the new diff step. On `main` (before any move), the check passes; on the PR 1 branch (after the move), the check still passes.

3. **Carve out `skills/kit-core/` from the current `skills/components/`.** Rename the directory to `kit-core/`. Strip the per-component lookup (current SKILL.md Step B1, L160-170) and the dispatch table to `references/components/<name>.md`. Keep Step A (foundation init), Steps C–G (file characteristics, accessibility patterns, SCSS rules, summary, `verify_integration.py`), Creator Mode (L634-898), Form Mode (L902-1220), Style-Tune delegation (L1224-1265), and HTML Target pipeline (L1269-1383). Move shared reference docs `architecture.md`, `accessibility.md`, `css-variables.md`, `composition.md`, `foundation.md` up one level into `kit-core/references/` (no longer nested under `components/`). **Rewrite the SKILL.md `description:`** to: *"Internal orchestrator for /kit-create, /kit-list, /kit-sync, /kit-update and Form/HTML/Style-Tune modes. Per-component generation lives in component-<name> skills; do not auto-trigger for component requests."* Update internal cross-references in the moved docs. **Leave `references/components/` in place** with the 14 other component docs untouched — PR 1 is a coexistence state.
   - *Why:* `kit-core` is the only place that needs to know how to "do" generation; per-component skills should be data + trigger, not workflow. The narrow description prevents router collision with per-component descriptions.
   - *Verify:* `plugins/acss-kit/skills/kit-core/SKILL.md` exists with the narrowed description (grep for "do not auto-trigger" returns 1 hit). `plugins/acss-kit/skills/components/` no longer exists. `plugins/acss-kit/skills/kit-core/references/components/` still exists and contains the 14 non-button component docs (button.md moved out in Step 4). Cross-links in shared refs resolve.

4. **Create `skills/component-button/`.** New directory containing `SKILL.md` and `reference.md`. `reference.md` is the verbatim move of `references/components/button.md` with verification banner, Generation Contract, Props Interface, TSX Template, CSS Variables, SCSS Template, Accessibility, Usage Examples — links to architecture/accessibility/etc. updated to `../kit-core/references/<sibling>.md`. `SKILL.md` is small: `name: component-button`, a precise `description:` under 160 chars (format: *"Use when the user asks to generate, create, or scaffold a Button — accessible TSX or HTML+JS, with variants and a11y."*), and a five-step workflow:
   1. Read `reference.md` for templates and dep list.
   2. Run `detect_target.py`; if foundation missing, run `foundation_init.py` (kit-core owns the scripts).
   3. For each dependency in the Generation Contract, recursively run `/kit-add <dep>` (no skill-to-skill orchestration — just a slash-command call the user/agent already runs).
   4. Apply the Generation Contract from `reference.md` to produce `ui/Button.tsx` + `Button.module.scss`.
   5. Run `verify_integration.py` and print summary.
   - *Why:* Inline workflow avoids the unsupported "skill calls skill mid-flow" pattern. Foundation init via script-return is the simplest idempotent check. Button is the dep-leaf for many other components, so its POC informs dep-aware migration in PR 2.
   - *Verify:* `head -10 plugins/acss-kit/skills/component-button/SKILL.md` shows the narrowed description under 160 chars. `wc -l SKILL.md` is under 100 (no embedded TSX/SCSS). `reference.md` contains a fenced ```tsx``` block. `references/components/button.md` no longer exists. Running `/kit-add button` against a sandbox produces output byte-identical to the golden from Step 2.

5. **Rewire `/kit-add` to prefer per-component skills when present, fall back to `kit-core` otherwise.** Update `commands/kit-add.md` (the slash command body) and the routing notes so `/kit-add button` routes to `component-button/SKILL.md`, while `/kit-add dialog` (still in the old location during PR 1) continues to route into kit-core which reads `references/components/dialog.md`. This is a *transitional* dispatch — PR 2 removes the fallback. Likewise update `commands/kit-list.md` to glob both `skills/component-*/SKILL.md` AND `references/components/*.md` for the duration of PR 1, and lowercase its argument before lookup. `/kit-sync`, `/kit-update`, `/kit-create` continue routing into kit-core unchanged.
   - *Why:* PR 1 must work for all 15 components, not just button. A transitional fallback dispatch keeps the other 14 working through the old path until PR 2 migrates them.
   - *Verify:* `/kit-add button` against a fresh sandbox routes through `component-button` (trace shows that skill name). `/kit-add dialog` routes through kit-core and produces working dialog output. `/kit-list` enumerates all 15. `/kit-list Button` (capitalized) succeeds — lowercase normalization works.

6. **Rewire `tests/validate_extracted_tsx.mjs` and SCSS validator to scan both roots during the transitional state.** The hard-coded `REFS_DIR = plugins/acss-kit/skills/components/references/components` becomes a two-root walker: collects `plugins/acss-kit/skills/kit-core/references/components/*.md` AND `plugins/acss-kit/skills/component-*/reference.md`. `COMPONENTS_WITHOUT_SCSS` allow-list keeps `icon` and updates to drop `foundation`/`form` references. The known-bad fixture in `tests/fixtures/known-bad/` keeps working unchanged.
   - *Why:* During PR 1, button's content lives in the new skill dir and the other 14 stay in `kit-core/references/components/`. The validator must check both or it goes vacuously green.
   - *Verify:* `tests/run.sh` step 2 output reports 15 component files validated (1 from `component-button/`, 14 from `kit-core/references/components/`). Intentionally break button's TSX in `component-button/reference.md` on a throwaway commit and confirm step 2 fails; revert.

## PR 2 — Bulk migration of remaining 14 components + cleanup

7. **Bulk-create the remaining 14 component skill directories.** For each of: alert, card, checkbox, dialog, field, icon, icon-button, img, input, link, list, nav, popover, table — create `plugins/acss-kit/skills/component-<name>/` containing `SKILL.md` + `reference.md`. `reference.md` moves verbatim from `kit-core/references/components/<name>.md` with sibling links updated to `../kit-core/references/<sibling>.md`. `SKILL.md` mirrors the component-button shape from Step 4 (description, 5-step workflow). After all moves, `kit-core/references/components/` is empty and removed.
   - *Why:* PR 1 validated the pattern on button; PR 2 applies it uniformly. Doing this as one bulk operation rather than 14 separate PRs avoids 14× the review overhead.
   - *Verify:* `ls plugins/acss-kit/skills/component-*/SKILL.md | wc -l` returns 15. `ls plugins/acss-kit/skills/kit-core/references/components/ 2>/dev/null` returns no output (directory gone). Each `component-<name>/SKILL.md` has `head -10` showing the narrowed description.

8. **Author all 14 remaining skill descriptions in one pass.** Each description follows the format *"Use when the user asks to generate, create, or scaffold a `<Component>` — `<one-line of what makes it distinct>`."* under 160 chars. Cross-check the full set side-by-side to ensure trigger phrases don't overlap (e.g. `icon-button` mentions "icon-only button" explicitly so router doesn't pick `component-button` for "icon button"). Run the `skill-reviewer:check-description` validator on each.
   - *Why:* 15 × 160 chars = ~2.4 KB of carefully-crafted routing logic. Writing them in a batch (rather than scattered across 15 separate commits) prevents subtle drift in style and overlap in trigger phrases.
   - *Verify:* `skill-reviewer:check-description` returns clean for all 15 component skill files. Manual side-by-side review of the 15 descriptions shows distinct trigger phrasing per component. No description exceeds 160 chars (validator enforced).

9. **Remove `/kit-add` fallback dispatch; convert `/kit-list`, `/kit-sync`, `/kit-create` to skill-dir-glob only.** Drop the transitional `references/components/*.md` lookup from `commands/kit-add.md`. `commands/kit-list.md` (no args) globs `skills/component-*/SKILL.md` and reads frontmatter — no longer scans `kit-core/references/components/`. `commands/kit-create.md` Creator Mode's dispatch table updates its phrase→path map to `skills/component-<name>/reference.md`. `skills/kit-sync/SKILL.md` Step S2 replaces the catalog.md enumeration with a glob over `skills/component-*/`. `/kit-sync` reads each component's Generation Contract dependencies and **topologically sorts** before iterating, so dialog generates after button regardless of glob order.
   - *Why:* Once all 15 components live in per-component skills, the transitional fallback is dead code that masks bugs. Topological sort future-proofs `/kit-sync` against new components with unusual dep trees.
   - *Verify:* `grep -r "references/components/" plugins/acss-kit/commands plugins/acss-kit/skills` returns no hits. `/kit-list` against a fresh install lists all 15 components. `/kit-sync` against a fresh sandbox installs all 15 in topologically-valid order (button before dialog, input before field — visible in the generation log).

10. **Update maintainer skills + the `component-reference-reviewer` agent.** `.claude/skills/acss-kit-component-author/SKILL.md` changes its scaffolder output from "write `references/components/<name>.md` + append catalog.md row" to "create `skills/component-<name>/` containing `SKILL.md` (frontmatter + thin workflow, description left as a `TODO:` placeholder for the author) + `reference.md` (the canonical 9-section template)." Pre-flight conflict check refuses if the skill directory exists. `.claude/skills/acss-kit-component-update/SKILL.md` updates its diff target from `references/components/<name>.md` to `skills/component-<name>/reference.md`. **The `component-reference-reviewer` agent's path resolution** updates to scan `skills/component-*/reference.md` instead of the old location.
    - *Why:* Author/update/review tooling must evolve in lockstep — leaving any of them pointed at the old path silently breaks the next maintainer workflow.
    - *Verify:* Dry-run `/acss-kit-component-author test-component` against a scratch worktree and confirm it creates `skills/component-test-component/SKILL.md` + `reference.md`, no catalog edit. Run the `component-reference-reviewer` agent on a per-component reference and confirm it reads the new path. Delete scratch artifacts.

11. **Update path-coupled rules and update sibling files.** `.claude/rules/fpkit-references.md` `paths:` glob updates from `plugins/*/skills/*/references/**` to also include `plugins/*/skills/component-*/reference.md`. Update every entry in the Step 1 grep checklist that hasn't already been touched. Spot-check `/prompt-book` example prompts for any reference doc paths. Confirm sibling plugins (`acss-utilities`, `style-agent`) have no path coupling to the old layout.
    - *Why:* Path-coupled rules silently lose enforcement when content moves. A glob that matches zero files generates zero advisory context but also zero warnings.
    - *Verify:* `grep -l "references/components/" .claude/rules` returns no hits (or only archival files). Editing a `component-<name>/reference.md` fires the `fpkit-references` rule advisory (confirm by triggering an edit and inspecting the loaded context). Re-running the Step 1 grep returns zero hits across `plugins/`, `.claude/`, `tests/`, `docs/`.

12. **Migrate inline-only catalog entries; drop `catalog.md` and skip the regen script.** The six inline-only entries from the old `catalog.md` (Badge, Tag, Heading, Text/Paragraph, Details, Progress) move into a new `kit-core/references/inline-components.md`, preserving their existing prose. The old `catalog.md` (formerly at `references/components/catalog.md`, now under `kit-core/references/`) is **deleted**, not regenerated — `/kit-list` is the authoritative live listing, and a regenerated doc with no command reading it is dead documentation that would drift. No `regenerate_catalog.py` script is created.
    - *Why:* Originally the plan kept catalog.md as a regenerated artifact, but the stress-test surfaced that no command consumes it after the refactor. Removing it eliminates a script, an artifact, and the "when does regen run?" question in one cut.
    - *Verify:* `find plugins/acss-kit/skills -name "catalog.md"` returns no hits. `kit-core/references/inline-components.md` exists and contains the six historical entries. No `regenerate_catalog.py` exists under `plugins/acss-kit/scripts/`.

13. **Update plugin docs and bump version.** `plugins/acss-kit/README.md` Component list section reflects the "each component is a skill" model. `plugins/acss-kit/CHANGELOG.md` records the refactor as a breaking-internal-structure change (no user-facing slash command behavior change). `plugins/acss-kit/.claude-plugin/plugin.json` version bumps. `CLAUDE.md` "Plugin structure" section updates to show `kit-core/` + `component-*/` layout.
    - *Why:* Manifest, README, and changelog are the user's source of truth for what changed; CLAUDE.md is Claude's session context.
    - *Verify:* `tests/run.sh` still green end-to-end. `cat plugins/acss-kit/.claude-plugin/plugin.json | jq .version` shows the bumped version. CLAUDE.md diff shows the new layout in the Plugin structure section.

## Acceptance Criteria

- [ ] `plugins/acss-kit/skills/component-<name>/` directories exist for all 15 documented components, each containing `SKILL.md` + `reference.md`.
- [ ] `plugins/acss-kit/skills/components/` and `plugins/acss-kit/skills/kit-core/references/components/` no longer exist; shared references live at `plugins/acss-kit/skills/kit-core/references/`.
- [ ] `kit-core/SKILL.md` description explicitly says "do not auto-trigger for component requests" — router prefers per-component skills.
- [ ] `/kit-add button` produces TSX+SCSS byte-identical to the captured golden in `tests/fixtures/golden/component-button/`.
- [ ] `/kit-list` enumerates 15 components by globbing `skills/component-*/SKILL.md`; `/kit-list Button` (capitalized) succeeds.
- [ ] `/kit-create "a destructive confirmation modal"` matches `component-dialog` (or `component-alert`) via the rewired Creator Mode dispatch.
- [ ] `/kit-sync` installs all 15 components in topologically-sorted dep order (button before dialog, input before field).
- [ ] `tests/run.sh` is green; TSX validator step reports 15 component files validated; golden-output diff for button passes.
- [ ] `/acss-kit-component-author test-foo` creates `skills/component-test-foo/` and does not touch `catalog.md` or the old `references/components/`.
- [ ] `component-reference-reviewer` agent reads from `skills/component-*/reference.md`.
- [ ] Six inline-only catalog entries (Badge, Tag, Heading, Text, Details, Progress) preserved in `kit-core/references/inline-components.md`. `catalog.md` and `regenerate_catalog.py` do not exist.
- [ ] `.claude/rules/fpkit-references.md` glob covers the new layout.
- [ ] `plugins/acss-kit/.claude-plugin/plugin.json` version is bumped; `CHANGELOG.md` documents the restructure.
- [ ] Repo-wide `grep "references/components/"` returns zero hits.

## Verification

End-to-end after PR 2 merges: from a clean checkout, run `tests/run.sh` and confirm green. Then `claude --plugin-dir ./plugins/acss-kit` against `tests/sandbox/` and exercise:

1. `/kit-list` — confirm 15 entries with distinct descriptions sourced from skill frontmatter (compare against `head -10 plugins/acss-kit/skills/component-*/SKILL.md`).
2. `/kit-list Button` — confirm case-insensitive lookup succeeds.
3. `/kit-add button` — confirm routing through `component-button`, byte-identical match against golden fixture.
4. `/kit-add dialog field input` — confirm dep resolution works across per-component skills (dialog→button, field→input).
5. `/kit-create "a card with an icon header and a button footer"` — confirm Creator Mode in kit-core dispatches via `skills/component-card/reference.md`.
6. `/kit-sync` against a fresh sandbox — confirm 15 component file groups generated, manifest.json populated, topological order in the log.
7. `/acss-kit-component-author scratch-skill` in a worktree — confirm new scaffolder shape; delete scratch.
8. Auto-trigger smoke: in a fresh session, prompt "I need a modal for delete confirmation" with no slash command and confirm `component-dialog` triggers (not `kit-core`) by checking the routing trace.
9. Trigger smoke negative: prompt "what fpkit components exist?" and confirm `kit-core` triggers (or no skill triggers), not a random per-component skill.

## Coupling Sites

Live-repo files containing references to `references/components` or `skills/components` (excludes `.claude/worktrees/` scratch). Checked = addressed in PR 1; unchecked = PR 2.

**Commands + skills (PR 1 — done):**
- [x] `plugins/acss-kit/commands/kit-add.md`
- [x] `plugins/acss-kit/commands/kit-list.md`
- [x] `plugins/acss-kit/commands/kit-create.md`
- [x] `plugins/acss-kit/skills/kit-sync/SKILL.md` (Step S2 catalog path)

**Tests + scripts (PR 1 — done):**
- [x] `tests/validate_extracted_tsx.mjs` (REFS_DIR → two-root walker)
- [x] `tests/lib/resolve_deps.mjs` (REFS_DIR_REL → dual-path lookup)
- [x] `plugins/acss-kit/scripts/lib/extract.mjs` (extractFromFile name derivation)

**Maintainer skills + agents (PR 2 — Step 10):**
- [ ] `.claude/agents/component-reference-reviewer.md`
- [ ] `.claude/commands/review-component.md`
- [ ] `.claude/skills/acss-kit-component-author/SKILL.md`
- [ ] `.claude/skills/acss-kit-component-update/SKILL.md`
- [ ] `.claude/skills/acss-kit-test-component/SKILL.md`
- [ ] `.claude/skills/validate-plugins/SKILL.md`
- [ ] `.claude/agents/README.md`, `.claude/skills/README.md`

**Rules (PR 2 — Step 11):**
- [ ] `.claude/rules/fpkit-references.md` (paths glob update)

**Docs (PR 2 — Step 13):**
- [ ] `plugins/acss-kit/docs/architecture.md`
- [ ] `plugins/acss-kit/docs/concepts.md`
- [ ] `plugins/acss-kit/docs/recipes.md`
- [ ] `plugins/acss-kit/docs/troubleshooting.md`
- [ ] `plugins/acss-kit/docs/tutorial.md`
- [ ] `plugins/acss-kit/docs/visual-guide.md`
- [ ] `plugins/acss-kit/docs/README.md`
- [ ] `plugins/acss-kit/README.md`
- [ ] `plugins/acss-kit/CHANGELOG.md`
- [ ] `.claude/commands.md` (meta-index)

## Next Steps *(optional)*

- Promote the six inline-only catalog entries to skills:

  ```text
  Read plugins/acss-kit/skills/kit-core/references/inline-components.md and
  the upstream fpkit source for each of Badge, Tag, Heading, Text/Paragraph,
  Details, and Progress (https://github.com/shawn-sandy/acss/blob/main/packages/
  fpkit/src/components/). For each, run /acss-kit-component-author <name> in a
  worktree to scaffold a new skills/component-<name>/ skill, then fill in the
  TSX Template, SCSS Template, Props Interface, CSS Variables, Accessibility,
  and Usage Examples sections from the fpkit source. Verify with tests/run.sh
  after each addition. Open one PR per component.
  ```

- Normalize the legacy-shape components after migration:

  ```text
  Audit plugins/acss-kit/skills/component-nav/reference.md and
  plugins/acss-kit/skills/component-form/reference.md (if form gets promoted)
  against the canonical 9-section embedded-markdown shape documented in
  .claude/skills/acss-kit-component-author/SKILL.md. Both were flagged "legacy
  shape" in the previous SKILL.md. Update them to the canonical shape without
  changing the underlying TSX or SCSS templates. Use the
  component-reference-reviewer agent to verify alignment.
  ```

- Wire a path rule for the new layout:

  ```text
  Add a new rule at .claude/rules/component-skills.md with paths:
  ['plugins/acss-kit/skills/component-*/SKILL.md',
   'plugins/acss-kit/skills/component-*/reference.md']
  that reminds authors of: (a) the canonical 9-section embedded-markdown shape
  for reference.md, (b) the 160-char description budget for SKILL.md
  frontmatter, (c) the rule that SKILL.md must not contain TSX or SCSS fenced
  blocks (those live only in reference.md). Add a row to .claude/rules/README.md.
  ```

## Unresolved Questions *(optional)*

- Semver bump magnitude:

  ```text
  Decide whether the per-component-skill refactor in
  docs/plans/split-acss-kit-components-into-skills.md warrants a major
  (2.0.0) or minor (1.1.0) version bump on
  plugins/acss-kit/.claude-plugin/plugin.json. Arguments for major:
  skills/components/ directory removed, anyone with a project-level skill or
  rule referencing plugins/acss-kit/skills/components/references/components/
  <name>.md breaks. Arguments for minor: user-facing slash commands
  (/kit-add, /kit-create, /kit-list, /kit-sync, /kit-update) behave
  identically, .acss-kit/manifest.json schema unchanged, generated TSX/SCSS
  output byte-identical (proven by golden fixture). Recommend one with reasoning.
  ```

- Consumer migration risk via `.acss-kit/manifest.json`:

  ```text
  Read plugins/acss-kit/scripts/manifest_write.py and manifest_read.py to
  confirm the manifest schema only stores target-project relative paths
  (Button.tsx, ui/theme.css) and never plugin-internal paths. If any
  plugin-internal path leaks into the manifest, propose a migration step for
  existing installs. If not, document explicitly in CHANGELOG that no
  consumer-side migration is needed.
  ```

---

## Interview Summary

_Appended from `/plan-interview` stress-test on 2026-05-21._

### Key Decisions Confirmed

- **Skill shape**: full skill dirs (`skills/component-<name>/SKILL.md` + `reference.md` co-located), content moves into the skill folder.
- **Scope**: all 15 documented components in first wave; inline-only catalog entries preserved separately.
- **Modes** stay centralized in `kit-core/`.
- **Delegation mechanic**: **inline reference** — no skill-to-skill invocation. Each per-component SKILL.md carries its own ~5-step workflow referencing `kit-core/references/` for shared constraints.
- **Trigger collision avoidance**: `kit-core`'s description rewritten as "Internal orchestrator…; do not auto-trigger for component requests."
- **Migration**: **POC first, then bulk** — PR 1 ships kit-core + `component-button` alongside the existing layout; PR 2 migrates remaining 14.
- **External breakage policy**: audit + fix in this PR; marketplace plugins have no semver guarantee on internal paths.
- **`/kit-sync` ordering**: topological sort on Generation Contract deps, not alphabetical glob order.
- **Foundation init**: kit-core owns the scripts; per-component skills run `detect_target.py` first and conditionally run `foundation_init.py`.
- **Regression test**: golden-output fixture for `component-button` captures byte-level template fidelity.
- **Simplification accepted**: `catalog.md` dropped entirely, `regenerate_catalog.py` not created (no command consumes the artifact).

### Plan Naming

| Element | Current | Issue | Suggested |
|---------|---------|-------|-----------|
| Filename | `i-want-each-acss-fancy-wadler.md` | Random adjective-noun, violates global `plan-mode.md` `verb-target` rule | `split-acss-kit-components-into-skills.md` |
| H1 Heading | `# Plan: Split acss-kit components into per-component skills` | Pass | _(no change)_ |

User accepted rename. Deferred to commit 1 of execution because `mv` is non-readonly and prohibited in plan mode.

### Open Risks & Concerns

- 15 distinct 160-char descriptions need careful crafting; Step 8 now budgets for this explicitly.
- `fpkit-references.md` rule glob and `component-reference-reviewer` agent both have hardcoded paths; Steps 10–11 now touch them.
- `/kit-list` case sensitivity — Step 5 lowercases its argument.
- Sibling plugins (`acss-utilities`, `style-agent`) coupling unverified — Step 11 audits.
- Consumer migration via `.acss-kit/manifest.json` still open (see Unresolved Questions).
- Semver magnitude still open (see Unresolved Questions).

### Recommended Next Steps (folded into plan body)

1. ~~Pre-flight grep step inserted~~ — done as Step 1.
2. ~~2-PR structure adopted~~ — plan reorganized into PR 1 (Steps 1–6) and PR 2 (Steps 7–13).
3. ~~Description-authoring step added~~ — Step 8.
4. ~~Golden-output baseline added~~ — Step 2.
5. ~~Maintainer skills + `component-reference-reviewer` agent updates~~ — Step 10.
6. ~~`fpkit-references.md` glob update made explicit~~ — Step 11.
7. ~~`/kit-list` case-insensitivity~~ — Step 5.
8. ~~Naming-convention unresolved question pruned~~ — answered by skill-dir layout choice; no longer in Unresolved Questions.

### Simplification Opportunities (applied)

- ~~Drop `catalog.md` and `regenerate_catalog.py` entirely~~ — Step 12 deletes catalog, no regen script created.
- ~~Foundation init via script-return-value, not a docs file~~ — Step 4 uses `detect_target.py` + `foundation_init.py` directly.
