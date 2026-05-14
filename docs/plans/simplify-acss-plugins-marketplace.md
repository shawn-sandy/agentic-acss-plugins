# Plan: Simplify and de-duplicate the acss-plugins marketplace

## Context

The three plugins in this repo (`acss-kit`, `acss-utilities`, `style-agent`) have accreted bloat and duplication along five axes:

1. **Pilot skills duplicate parent skills.** `component-creator` (648 lines) and `component-form` (462 lines) both read the same `references/components/*.md` that `components` (629 lines) already owns. `style-tune` (356 lines) straddles `styles` and `components`. Roughly 1500 of these lines are duplicated workflow text.
2. **The React/HTML target split is duplicated at four layers.** `kit-add` vs `kit-add-html`, `components/` vs `components-html/`, `detect_target.py` vs `detect_html_target.py`, `verify_integration.py` vs `verify_html_integration.py` — a single `--target=react|html` parameter would collapse all of it.
3. **`acss-utilities` shells into `acss-kit` via relative paths** (`../acss-kit/scripts/detect_stack.py`, `verify_integration.py`) and `detect_utility_target.py` re-implements `acss-kit/scripts/detect_target.py`. `token-bridge.css` hardcodes hex fallbacks copied from `generate_palette.py` with no hook to keep them in sync — every theme regen silently invalidates the bridge.
4. **Five theme commands are 21-line stubs** delegating to one skill. The same pattern repeats for the four `/utility-*` commands.
5. **Six of twelve project-level maintainer skills are acss-kit-specific** (`component-author`, `component-update`, `style-author`, `style-update`, `test-component`, `changelog-entry`) and three more form a redundant validation cake (`validate-plugin` ⇄ `verify-plugins` ⇄ `plugin-health`).

**Intended outcome:** simpler installs, one canonical source for every role-name and project-detection concept, fewer thin-wrapper commands, and maintainer skills that live in the plugin they describe.

## Objective

Reduce the marketplace from 3 plugins / 12+13 skills / 23 scripts / 19 commands to **2 plugins** (`acss-kit`, `style-agent`) with consolidated skills, parametrized React/HTML paths, a shared script library, and project-level maintainer tooling that is genuinely cross-plugin. Land changes across **five sequenced phases** so each phase ships as one PR / one version bump and `tests/run.sh` stays green throughout.

## Steps

<ol>

<li>

**Phase 1 — Documentation, maintainer skills, and hook hygiene (lowest risk, no user-facing API change).**

  <ol>
    <li>**Fix the top-level `README.md` version table and add the missing `style-agent` row.** Currently lists acss-kit @ 0.7.0 / acss-utilities @ 0.4.0; actual `plugin.json` values are 0.11.2 / 0.5.0. Style-agent is omitted from the plugin table entirely. *Why:* the README is the first thing users see and it is meaningfully stale. *Verify:* `grep -E '0\.(11|5|2)\.' README.md` returns the three current versions; `grep style-agent README.md` finds the new row.</li>

    <li>**Tag the six acss-kit-specific project skills as maintainer-only in `.claude/skills/`** (`component-author`, `component-update`, `style-author`, `style-update`, `test-component`, `changelog-entry`). Keep them at `.claude/skills/` (which is already the repo-only slot, outside any published plugin) but rename their `name:` to `acss-kit-<original>` and prepend `[Maintainer]` to their `description:`. Update the maintainer-tooling table in `CLAUDE.md`. *Why:* moving them inside `plugins/acss-kit/skills/` would ship them to every user that installs acss-kit (`_` prefix is not a Claude Code privacy convention). Tagging in place keeps them out of user installs while still distinguishing them from genuinely cross-plugin skills. *Verify:* `ls .claude/skills/acss-kit-*` lists all six; `claude --plugin-dir ./plugins/acss-kit` in a fresh dir does NOT surface them; `tests/run.sh` green.</li>

    <li>**Merge `validate-plugin` + `verify-plugins` + `plugin-health` into one skill** at `.claude/skills/validate-plugins/` with a `--scope=plugin|all|health` flag. Delete the other two skill dirs. *Why:* three skills doing the same structural validation at different scopes is the most concentrated bloat in maintainer tooling. *Verify:* `validate-plugins --scope=all` reproduces the previous `verify-plugins` output; `--scope=health` reproduces the previous `plugin-health` checklist; tests/run.sh green.</li>

    <li>**Merge `release-plugin` + `release-check` into one skill** with a `--check` mode that runs paperwork audit only. *Why:* they pair in workflow but ship as two skills. *Verify:* `release-plugin acss-kit --check` produces the old `release-check` report; without `--check` it produces the version bump.</li>

    <li>**Document the two undocumented hooks (WCAG + utility-CSS) in `.claude/hooks.md`; keep all existing hooks.** The two front-matter warning hooks (SKILL.md, command-frontmatter) provide *real-time* feedback on every Write/Edit that `validate-plugin` only gives in batch — keep them. *Why:* the audit flagged them as duplicative with `validate-plugin` but the trigger surface is genuinely different (continuous vs. on-demand). Documentation parity is the actual fix. *Verify:* `.claude/hooks.md` lists all 6 PostToolUse + 1 PreToolUse hooks; `tests/run.sh` green.</li>

    <li>**Strip the script inventory out of `.claude/rules/python-scripts.md`** — keep the stdlib-only contract and detector-vs-generator distinction, drop the per-script listing that rots every time a script is added. *Why:* the rule injects ~7 KB into context on every script edit and the inventory is the rot-prone part. *Verify:* `.claude/rules/python-scripts.md` is under 2 KB and contains only the contract.</li>

    <li>**Decide between `plugins/acss-kit/docs/commands.md` and `plugins/acss-kit/docs/prompt-book.md`** — keep the prompt book (already exposed as a skill), delete the standalone `commands.md` (duplicates command file front-matter). Same review for `plugins/acss-utilities/docs/commands.md`. *Why:* three places to maintain the same command catalogue. *Verify:* each plugin's docs index links to one command reference, not two.</li>
  </ol>

  Phase-1 exit: one PR, plugin versions un-bumped (no user-facing change), `tests/run.sh` green.

</li>

<li>

**Phase 2 — Absorb pilot skills and collapse stub commands inside `acss-kit`** (one PR, minor version bump per plugin).

  <ol>
    <li>**Prerequisite: apply `docs/plans/raise-skilllistingbudgetfraction-current-jiggly-pie.md` before this phase.** That plan raises `skillListingBudgetFraction` from 0.01 → 0.05 in `.claude/settings.json`, giving each of ~193 installed skills ~207 chars of description budget (up from ~41). The 160-char target is a guideline, not a hard validator — at 0.05 the merged descriptions for `components/SKILL.md` and `styles/SKILL.md` can safely run to ~200 chars without truncation. *Why:* Q2 resolved — the budget is a context-window allocation constraint, not a per-skill enforcement rule; raising it before absorbing pilots removes the trigger-truncation risk entirely. *Verify:* `jq '.skillListingBudgetFraction' .claude/settings.json` returns `0.05` before proceeding with step 2.2.</li>

    <li>**Draft and validate merged descriptions before absorbing any pilot.** Write the proposed `components/SKILL.md` description (covering standard, creator, and form triggers) and `styles/SKILL.md` description (covering theme, brand, color-scale triggers) and confirm each fits within 200 chars. *Why:* the pilots earned promotion because their distinct descriptions auto-trigger reliably; collapsing them requires the parent description to absorb those trigger phrases without losing specificity. *Verify:* both proposed descriptions are ≤200 chars and manually confirmed to include the key trigger phrases from both pilots.</li>

    <li>**Fold `component-creator` into `skills/components/SKILL.md`** as a "Creator mode (natural-language)" section. Update `commands/kit-create.md` to point at `skills/components/SKILL.md#creator-mode`. Delete `skills/component-creator/`. *Why:* the pilot is a thin natural-language adapter on top of the same ref docs the parent already reads. *Verify:* `/kit-create "primary pill button labelled Buy"` still produces a button TSX file; auto-trigger fires on a bare "create a primary button" prompt; `tests/run.sh` green.</li>

    <li>**Fold `component-form` into `skills/components/SKILL.md`** as a "Form scaffolding" section. Delete `skills/component-form/`. *Why:* per-component pilot for a single ref doc; clearest absorb candidate. *Verify:* a "create a signup form with email + password" prompt still scaffolds the same TSX; auto-trigger fires on "build a contact form"; `tests/run.sh` green.</li>

    <li>**Keep `style-tune` as a thin router skill; delete its workflow body, not the skill.** The workflow content moves into `skills/styles/SKILL.md` (theme-role tunes) and `skills/components/SKILL.md` (component-token tunes); `skills/style-tune/SKILL.md` shrinks to a ~30-line router that classifies the prompt and delegates. *Why:* putting "Tune" sections in *both* parent skills creates competing auto-trigger surfaces for the same prompts ("warmer button" matches both `components/` and `styles/`); a dedicated router resolves the ambiguity and was the pilot's unique contribution. *Verify:* `/style-tune "warmer button"` routes to components and edits `--btn-*`; `/style-tune "deeper primary"` routes to styles, edits the role, and triggers WCAG re-validation; only `style-tune/SKILL.md` matches "tune the primary".</li>

    <li>**Confirm the subcommand convention exists, then collapse five theme commands.** First: `grep -l '$ARGUMENTS' plugins/*/commands/*.md` and check whether any existing command parses `$ARGUMENTS` for a leading subcommand verb. If yes, collapse into one `/theme <action>` whose body routes via the verb. If no, keep five thin command files but point them all at one consolidated `skills/styles/SKILL.md` section per action (the duplication is in skills, not commands). Either way: keep `theme-create.md`, `theme-extract.md`, `theme-brand.md`, `theme-update.md`, `color-scale.md` as deprecation aliases for one minor-version window before deletion. *Why:* slash commands in Claude Code take a single `$ARGUMENTS` string; subcommand routing is a convention, not a primitive — confirm it's used here before relying on it. *Verify:* either `/theme create #336699` routes correctly via $ARGUMENTS parsing, OR the five separate command files all point at the same skill section without divergent boilerplate; alias stubs print the deprecation hint when invoked.</li>

    <li>**Collapse `/kit-sync` and `/kit-update`** following the same convention chosen above (either `/kit <action>` or two thin commands pointing at one skill). Both already share `skills/kit-sync/SKILL.md`. *Why:* one skill, two commands is gratuitous regardless of which surface convention you pick. *Verify:* both old workflows still reachable; `tests/run.sh` green.</li>

    <li>**Refresh the `prompt-book` skill** to reflect all command renames made in this phase (theme-* aliases, kit-sync/kit-update collapse). *Why:* the prompt book catalogues "every shipped slash command" and ships as a user-facing skill; stale entries undermine usability (Q5 resolved: per-phase refresh so each phase is independently shippable). *Verify:* `/prompt-book` output lists the new command surface; no old command names appear without a "(deprecated)" note.</li>

    <li>**Update `plugins/acss-kit/CHANGELOG.md`** with a "Consolidated skills" entry; bump `plugin.json` minor version. *Why:* this is a user-visible surface change (command rename / skill removal) that warrants a minor bump. *Verify:* `/release-plugin acss-kit --check` reports clean paperwork.</li>
  </ol>

  Phase-2 exit: one PR, `acss-kit` minor version bump, 9 skills → 5, 12 commands → ~7, `tests/run.sh` green.

</li>

<li>

**Phase 3 — Parametrize the React/HTML target split** (one PR, minor version bump on `acss-kit`).

  <ol>
    <li>**Pre-flight read-pass — confirm three assumptions before touching any code.** (a) Open one reference doc (`skills/components/references/components/button.md`) and confirm whether it carries an HTML template alongside the TSX, or whether `components-html/` derives HTML from TSX at generation time — the merge strategy depends on the answer. (b) Run `tests/e2e.sh` and confirm whether it exercises the HTML target; if not, add a `--target=html` smoke fixture before any merge. (c) Grep `.claude/settings.json` for hook commands that invoke scripts by absolute path; record which scripts are referenced so script renames in steps 3.4/3.5 don't silently break hooks. *Why:* this phase's biggest risk is assuming the React/HTML split is a thin parametrization when it may be two genuinely different code paths. *Verify:* a short read-pass note appended to this plan or a checklist file under `docs/plans/` records the answers to (a), (b), (c).</li>

    <li>**Merge `skills/components-html/SKILL.md` into `skills/components/SKILL.md`** under a "Target: HTML" subsection. The skill detects target by reading `.acss-target.json#target` (default `react`). If pre-flight (a) found that HTML is derived from TSX at generation time, keep that derivation logic intact inside the merged skill — don't try to flatten it. *Why:* the two skills share 80% of their content; the only real difference is the emitted file extension and the JS pattern. *Verify:* generating a button with `target: react` produces TSX+SCSS; with `target: html` produces HTML+SCSS+JS. Both pass `tests/e2e.sh` (now exercising both targets after step 3.0(b)).</li>

    <li>**Replace `commands/kit-add-html.md` with a deprecation alias** that calls `/kit-add --target=html`. Remove after one minor version. *Why:* preserve user muscle memory without keeping the duplicate path live. *Verify:* `/kit-add-html button` prints deprecation hint and routes to the new path.</li>

    <li>**Add `_target.py` shared library — vendor pattern, not package.** Create `plugins/acss-kit/scripts/_target.py` hosting the common detection, manifest, and CSS-entry probes. Each caller script imports it with a small `sys.path` shim at the top (`sys.path.insert(0, os.path.dirname(__file__))`) so scripts stay standalone-runnable per `.claude/rules/python-scripts.md`. **Do not** convert `scripts/` into a Python package — that would cascade through hook script paths (recorded in step 3.0(c)) and break the stdlib-only standalone contract. *Why:* the script contract requires each script to be runnable directly with `python3 path/to/script.py`; package imports break that. The `sys.path` shim is the minimum-invasive option. *Verify:* `python3 plugins/acss-kit/scripts/_target.py --self-test` passes when run directly; calling scripts still pass their own `--self-test`s; hook command lines in `.claude/settings.json` need no changes.</li>

    <li>**Replace `detect_target.py` + `detect_html_target.py` with a single `detect_target.py --target=react|html`** that imports from `_target.py`. Delete `detect_html_target.py`. *Why:* the two scripts differ mainly by stack signature; collapse with a flag. *Verify:* both old call sites resolve correctly; existing `tests/sandbox/` fixtures still detect the right directory.</li>

    <li>**Replace `verify_integration.py` + `verify_html_integration.py` with a single `verify_integration.py --target=react|html`.** Delete the `_html_` script. *Why:* same shape, different stack. *Verify:* `tests/e2e.sh` (which exercises both paths) passes.</li>

    <li>**Refresh the `prompt-book` skill** to reflect the `/kit-add --target=html` surface and the removal of `/kit-add-html`. *Why:* per-phase refresh keeps each phase independently shippable (Q5). *Verify:* `/prompt-book` lists `/kit-add` with `--target` note; `/kit-add-html` entry shows "(deprecated)".</li>

    <li>**Bump `acss-kit` minor version; CHANGELOG entry.** *Verify:* `release-plugin acss-kit --check` reports clean.</li>
  </ol>

  Phase-3 exit: 4 commands → 1, 4 scripts → 2, 2 skill dirs → 1, ~700 lines deleted, `tests/run.sh` + `tests/e2e.sh` green.

</li>

<li>

**Phase 4 — Merge `acss-utilities` into `acss-kit` with a clean deprecation path** (one PR, major-version bump on `acss-kit`, terminal release of `acss-utilities`).

  <ol>
    <li>**Copy `plugins/acss-utilities/skills/utilities/` to `plugins/acss-kit/skills/utilities/`** verbatim. Move `commands/utility-*.md` files into `plugins/acss-kit/commands/` (or collapse the four into one `/utility <action>` first — same pattern as `/theme`). *Why:* the utilities flow is small (171 lines + 4 thin commands) and tightly coupled to acss-kit's role catalogue. *Verify:* `/utility add` in a fresh sandbox copies `utilities.css` + `token-bridge.css` correctly; `tests/run.sh` utility checks pass.</li>

    <li>**Resolve the acss-kit vs fpkit vocabulary conflict via an explicit mapping file — do not rename utility classes.** acss-kit uses `--color-danger` / `--color-surface-raised`; utility classes use `bg-error` / `bg-surface-secondary` (fpkit vocabulary). Add `plugins/acss-kit/assets/utilities/vocab.json` mapping `{"error": "danger", "surface-secondary": "surface-raised", …}` — one canonical translation table. Move `utilities.tokens.json`, `utilities.css`, `token-bridge.css` under `plugins/acss-kit/assets/utilities/`. Rewrite `utilities.tokens.json` so it consumes `ROLE_GROUPS` + `vocab.json` and emits the fpkit-flavoured role names utilities expect. *Why:* renaming utility classes (`bg-error` → `bg-danger`) would break every user's existing `class="bg-error"` markup. An explicit mapping file is a thin replacement for today's hand-written `token-bridge.css` but with one source of truth for the vocabulary delta. *Verify:* add a synthetic role to `ROLE_GROUPS` with a `vocab.json` entry; regenerate; confirm utilities.css picks it up; existing `class="bg-error"` still resolves to acss-kit's danger role at runtime.</li>

    <li>**Replace `acss-utilities/scripts/detect_utility_target.py` with a thin call to `acss-kit/scripts/_target.py`** (introduced in Phase 3) parametrized for `--what=utilities`. Move `generate_utilities.py`, `migrate_classnames.py`, `validate_utilities.py` to `acss-kit/scripts/`. *Why:* `detect_utility_target.py` openly admits it mirrors `detect_target.py`; once they share a lib the duplicate disappears. *Verify:* utility-target detection in a fresh sandbox still resolves to the right directory.</li>

    <li>**Make `token-bridge.css` a generated artifact, not a static file.** Generate the bridge from the active theme at `/theme create` and `/theme update` time using `vocab.json` (introduced in step 4.2). Remove the hand-written hex fallbacks; rely on the bridge being emitted after the theme files in the cascade. Update `skills/styles/SKILL.md` to add a "Regenerate bridge" sub-step to both `/theme create` and `/theme update` flows. *Why:* hex fallbacks drift the moment `generate_palette.py` changes; making the bridge a derived artifact eliminates the drift class entirely. *Verify:* run `/theme update --role primary --to #ff0000`; confirm `token-bridge.css` is regenerated automatically; confirm `color-mix(in oklch, var(--color-primary), …)` resolves at runtime in a sandbox HTML page.</li>

    <li>**Write `plugins/acss-kit/docs/migration-v1.md`** covering: (a) command renames (`/theme-create` → `/theme create`, `/kit-add-html` → `/kit-add --target=html`, `/utility-*` → `/utility *` if subcommands chosen, else table of new command paths); (b) the acss-utilities plugin merge — what users need to do (uninstall acss-utilities, ensure acss-kit ≥ v1); (c) the vocabulary outcome (utility class names unchanged, but theme role names are canonical inside `vocab.json`); (d) `token-bridge.css` now regenerated automatically; (e) a one-line "rollback if needed" pointer (pin to acss-kit v0.x). Link the doc from `marketplace.json` and the top-level README. *Why:* this is the largest user-facing change in the series and a centralized migration doc is friendlier than scattered CHANGELOG entries. *Verify:* `migration-v1.md` exists; both READMEs link to it; a fresh user following only the doc can complete the migration without reading any CHANGELOG.</li>

    <li>**Refresh the `prompt-book` skill** to reflect the full v1.0.0 command surface: utility commands now in acss-kit, acss-utilities tombstoned, new `/theme` and `/kit` surfaces. *Why:* per-phase refresh (Q5); this is the largest surface change in the series. *Verify:* `/prompt-book` output covers all commands across acss-kit v1.0.0; no acss-utilities-specific entries remain.</li>

    <li>**Add a final terminal release of `plugins/acss-utilities/`** — v1.0.0 with `CHANGELOG.md` "Migrated into acss-kit. Install acss-kit v1+ for utilities. See migration-v1.md." Strip all skills/scripts to a single `README.md` deprecation notice pointing at the migration doc. Keep the manifest entry so existing installs don't 404. *Why:* a graceful tombstone is friendlier than a hard removal. *Verify:* `/plugin update acss-utilities` produces a clear deprecation message pointing at the migration doc.</li>

    <li>**Bump `acss-kit` to v1.0.0** with a CHANGELOG entry titled "Utilities and CSS authoring now live in acss-kit." Update `marketplace.json` description to ≤200 chars (treat `plugin.json#description` as canonical; do not duplicate the command list) and update the top-level README. *Why:* the audit found marketplace.json's acss-kit description was ~1.5 KB while plugin.json's is one sentence — constrain the marketplace copy to prevent description drift returning. Major version signals migration. *Verify:* `wc -c < <(jq -r '.plugins[] | select(.name=="acss-kit") | .description' .claude-plugin/marketplace.json)` returns < 200; fresh install of `acss-kit` exposes utility commands; install of `acss-utilities` still works and prints the deprecation notice.</li>
  </ol>

  Phase-4 exit: 3 plugins → 2, role-name vocabulary asserted in one place, no cross-plugin shell-out.

</li>

<li>

**Phase 5 — Targeted test hygiene and token-module safety** (one PR, no version bump needed — internal only). *Scope narrowed per Q6 resolution (c): cherry-pick only the two highest-payoff steps; defer `detect_*` merge, `manifest_*` merge, and rule update to next-steps where they belong.*

  <ol>
    <li>**Extract a shared `_tokens.py` module** hosting common JSON↔CSS variable logic used by both `tokens_to_css.py` and `css_to_tokens.py` (315 lines combined; explicit inverses). Keep both entry-point scripts but have them import the shared module via the `sys.path` shim pattern. *Why:* inverse-pair scripts that don't share a module always drift; this is the highest-payoff script consolidation with the lowest cascade risk. *Verify:* round-trip JSON → CSS → JSON on a fixture theme produces an identical JSON; both entry scripts still pass `python3 script.py --self-test`.</li>

    <li>**Rename `tests/validate_components.mjs` → `validate_extracted_tsx.mjs` and `tests/validate_components.py` → `validate_extracted_scss.py`.** Update `tests/run.sh` callsites and references in `tests/README.md`. *Why:* "validate_components" appears twice with different languages and different output coverage; the names obscure what each actually validates. *Verify:* `tests/run.sh` green; `tests/README.md` uses the new names.</li>
  </ol>

  Phase-5 exit: 2 files renamed, 1 shared module extracted, `tests/run.sh` green, no user-facing change.

</li>

</ol>

## Verification (end-to-end)

After each phase ships:

- `tests/run.sh` green from a clean checkout (one-time install: `npm --prefix tests ci && pip3 install --user tinycss2`).
- `tests/e2e.sh` green after **every phase that touches a command, skill, or script** — that is Phases 2 through 5 (not only 3 and 4 as the audit assumed). Phase 3 step 3.0(b) extends `e2e.sh` to exercise both React and HTML targets; that extension must stay green from then on.
- Fresh local install via `claude --plugin-dir ./plugins/acss-kit` exposes the expected commands for that phase: Phase 2 → theme + kit actions all reachable under whichever surface convention was confirmed in step 2.4; Phase 3 → `/kit-add --target=html` produces the right HTML+SCSS+JS triple; Phase 4 → utility commands and the role-name pipeline regenerate the bridge without manual hex edits; Phase 5 → all detect/manifest subcommands resolve.
- After Phase 4: install `acss-utilities` from the marketplace and confirm the deprecation notice points at the migration doc; install acss-kit v1.0.0 and confirm utility commands work; `wc -c < marketplace.json description for acss-kit` < 200.
- After Phase 5: round-trip a theme through `tokens_to_css.py` → `css_to_tokens.py` and confirm the JSON is byte-identical to the input.

**G5 user-flow metric (Q8 resolved):** After Phase 4 ships, a new user should be able to install acss-kit, generate a themed button component, and render it in a browser in **≤ 5 commands** from a fresh project. Baseline measurement: count the commands required with the current 3-plugin setup and record the number here before Phase 1 begins. If the post-Phase-4 count is ≤ 5 (or fewer than baseline), G5 is met. If not, revisit `/setup` (Q4 deferred to next-steps) before declaring the refactor complete.

**PR sequencing:** Phases 1 and 2 ship as independent PRs against `main`. Phase 3 stacks on Phase 2 (depends on consolidated `components/SKILL.md`). Phase 4 waits for Phases 1–3 to merge (depends on `_target.py` from Phase 3 and the absorbed pilots from Phase 2). Phase 5 stands alone and can ship any time after Phase 3 merges. Calendar: expect 2–3 PR cycles — Phases 1+2 can land in parallel review windows, and Phase 5 can interleave with Phase 4 review.

## Next steps (out of scope)

- **`/setup` audit (Q4 deferred):** If the post-Phase-4 G5 metric (≤ 5 commands to first component) is not met, audit `/setup` for friction and trim any prerequisites freed by the merge. This is the first follow-up to action if G5 is missed.
- **`detect_*` family merge (Phase 5.1 deferred):** Merge `detect_stack.py`, `detect_css_entry.py`, `detect_package_manager.py` into a single `detect.py --what=…` entry point (note: `detect_target.py` and `detect_html_target.py` are already merged in Phase 3). Cascade risk through hooks justifies deferral.
- **`manifest_*` family merge (Phase 5.2 deferred):** Merge `manifest_read.py`, `manifest_write.py`, `hash_file.py`, `diff_status.py` into `manifest.py <subcommand>`.
- **`python-scripts.md` shim pattern doc (Phase 5.5 deferred):** Document the `sys.path` shim pattern after Phase 5's `_tokens.py` module is in place and stable.
- **`style-agent` `/utility-extract` (Q7 deferred):** Add a third skill (`/utility-extract` — inverse of `/css-to-class`) to complete the CSS-authoring suite once demand is clearer.
- **Generated `marketplace.json`:** Derive marketplace descriptions from `plugin.json` to eliminate future description drift.
- **`--dry-run` flag:** Add to `/theme create` and `/kit-add` so users can preview the file set before any write.

## Resolved decisions

All eight questions resolved — no open decisions remain before implementation.

| # | Question | Decision | Rationale |
|---|---|---|---|
| Q1 | Tombstone vs. removal of acss-utilities | **Keep in-tree tombstone** — v1.0.0 shell with deprecation notice, manifest entry preserved | Safest for existing users; no 404 on update |
| Q2 | Description-budget hard constraint? | **Not a hard constraint** — it's a context-allocation guideline; raising `skillListingBudgetFraction` to 0.05 (existing plan) gives ~207 chars per skill | Applied as Phase 2 prerequisite (step 2.1) |
| Q3 | One-time bridge regen for v0.5.0 users | **Document as migration step in `migration-v1.md`** — users run `/theme create` (or the new `/theme update --bridge-refresh` action if added) once after upgrading | Covered in Phase 4 step 4.5 |
| Q4 | `/setup` in scope? | **Deferred (option b)** — Phase 4 reduces prerequisites (no separate acss-utilities install); if G5 metric is missed post-Phase 4, `/setup` audit is the first next-step | Added to Next steps |
| Q5 | prompt-book refresh cadence | **Per-phase (option a)** — refresh sub-step added to Phases 2, 3, and 4 | Each phase must be independently shippable |
| Q6 | Phase 5 scope | **Cherry-pick (option c)** — keep `_tokens.py` extraction (5.3) and test-file renames (5.4); defer `detect_*` merge, `manifest_*` merge, and rule update | Steps 5.1, 5.2, 5.5 have no G1–G5 contribution and carry hook/cascade risk |
| Q7 | `/utility-extract` in scope? | **Deferred (option b)** — keep in next-steps until refactor lands | Blast radius; separate feature work |
| Q8 | G5 falsifiable metric? | **Add metric (option a)** — "≤ 5 commands from fresh project to rendered themed button"; baseline measured before Phase 1; gate at Phase 4 exit | Added to Verification section |

## Open risks and mitigations

Findings from a stress-test pass on this plan. Each is keyed back to the step it touches. Findings recorded here even when the step text itself was revised, so the reasoning trail survives the next time this plan is revisited.

### High-severity (addressed inline)

- **S1 — Maintainer-skill pollution.** Originally Phase 1.2 moved six skills *into* `plugins/acss-kit/skills/` where they would ship to every user installing the plugin. **Mitigation:** keep them at `.claude/skills/` and rename with `acss-kit-` prefix + `[Maintainer]` description tag (revised in step 1.2).
- **S2 — Pilot absorption breaks auto-trigger routing.** Original Phase 2.1–2.3 collapsed all three pilots into parents and put "Tune" sections in two parents simultaneously — duplicate trigger surfaces. **Mitigation:** added a pre-flight description-budget audit (step 2.1) and kept `style-tune` as a thin router skill rather than absorbing it (revised 2.3). `component-creator` and `component-form` still absorb.
- **S3 — Subcommand convention not guaranteed.** Original Phase 2.4 assumed `/theme create` parses as command + subcommand. **Mitigation:** added a `grep` confirmation step before the collapse; fallback path is multiple thin command files sharing one skill section (revised 2.4).
- **S4 — HTML ref-doc source-of-truth unknown.** Original Phase 3.1 assumed the React/HTML split was a thin parametrization. **Mitigation:** added Phase 3 step 3.0 — a read-pass that confirms ref-doc structure, e2e.sh coverage, and hook script-path references before any merge.
- **S5 — Script contract break.** Original Phase 3.3 used `python -m` package imports, breaking the standalone-script contract and hook commands. **Mitigation:** revised 3.3 to use a `sys.path` shim (vendor pattern) so scripts stay standalone-runnable; Phase 5.5 documents the convention.
- **S6 — Vocabulary conflict between acss-kit and utilities.** Original Phase 4.2 said "derive utilities.tokens.json from ROLE_GROUPS" without addressing that the two vocabularies use different role names. **Mitigation:** revised 4.2 to introduce an explicit `vocab.json` mapping file as the single source of truth for the rename delta, and explicitly *not* rename utility classes (would break user markup).

### Medium-severity (addressed inline)

- **M1 — Removing real-time front-matter hooks loses authoring feedback.** Reverted: revised 1.5 keeps all existing hooks and just adds documentation parity.
- **M2 — `tests/e2e.sh` may not cover HTML path.** Added to Phase 3 step 3.0(b) and the global verification section.
- **M3 — `token-bridge.css` becomes a generated artifact.** Spelled out in revised 4.4: `/theme create` and `/theme update` both regenerate the bridge.
- **M4 — User migration messaging was scattered.** Added Phase 4 step 4.5 (`migration-v1.md`) as a centralized migration doc.
- **M5 — Marketplace.json description bloat.** Constrained in revised 4.6 to ≤200 chars, plugin.json canonical.
- **M6 — Phase 1.6 and 5.5 both touched python-scripts.md.** Disambiguated: 1.6 strips the inventory, 5.5 documents the `sys.path` shim pattern introduced in Phase 3.

### Low-severity (not patched into steps; track here)

- **L1 — Verify-step granularity.** Some verifies grep coarsely (e.g. version table) and would benefit from structured parsing. Accept as-is unless a regression surfaces.
- **L2 — PR sequencing.** Captured in the Verification section's new "PR sequencing" paragraph.
- **L3 — `tests/run.sh` doesn't cover command-surface changes.** Compensated by extending `tests/e2e.sh` coverage across all phases (revised verification section).
- **L4 — Axes-to-phases mapping.** The five bloat axes in Context map cleanly to phases; recheck after S6's `vocab.json` decision lands to confirm axis 3 (cross-plugin shell-out) is fully closed.
