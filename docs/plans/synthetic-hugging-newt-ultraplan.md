# Plan: Simplify and de-duplicate the acss-plugins marketplace [SUPERSEDED]

> **This plan was a discarded alternative.** The canonical Phase 1 implementation is in
> [`simplify-acss-plugins-marketplace.md`](simplify-acss-plugins-marketplace.md).
> Maintainer skills are tagged `acss-kit-*` and kept under `.claude/skills/` — not moved
> into `plugins/acss-kit/skills/_maintainer/` as proposed here. Do not follow this plan.

## Context

Three plugins (`acss-kit 0.11.2`, `acss-utilities 0.5.0`, `style-agent 0.2.0`) have accreted duplication along five axes that make the repo harder to maintain and the plugin surface harder to explain:

1. **Pilot skills duplicate parent skills.** `component-creator` (648 lines), `component-form` (462 lines), and `style-tune` (356 lines) operate on the same reference docs that `components/SKILL.md` (629 lines) already owns. The pilots were scaffolded as experiments; the overlap is now overhead.
2. **React/HTML split at four layers.** `kit-add` vs `kit-add-html`, `components/` vs `components-html/`, `detect_target.py` vs `detect_html_target.py`, `verify_integration.py` vs `verify_html_integration.py` — a `--target` flag would collapse all four.
3. **Cross-plugin coupling via hardcoded relative paths.** `plugins/acss-utilities/skills/utilities/SKILL.md` instructs Claude to run `${CLAUDE_PLUGIN_ROOT}/../acss-kit/scripts/detect_stack.py` and `verify_integration.py`. This works only when both plugins are installed. `detect_utility_target.py` re-implements `detect_target.py`'s ancestor-walk from scratch with no code sharing.
4. **Thin command stubs.** Five theme commands (`theme-create`, `theme-extract`, `theme-brand`, `theme-update`, `color-scale`) are 14–20-line files that all say "read this SKILL.md section." Same for four `/utility-*` commands.
5. **Maintainer skills are mis-scoped.** Six project-level skills (`component-author`, `component-update`, `style-author`, `style-update`, `test-component`, `changelog-entry`) are acss-kit–specific but live at the repo level. Three more (`validate-plugin`, `verify-plugins`, `plugin-health`) do overlapping structural checks at different scopes.

**Factual notes on the current state:**
- README version table is stale: shows acss-kit 0.7.0 (actual 0.11.2), acss-utilities 0.4.0 (actual 0.5.0), omits style-agent 0.2.0 entirely.
- The cross-plugin coupling is in SKILL.md prose (`${CLAUDE_PLUGIN_ROOT}/../acss-kit/scripts/...`), not in Python code. The Python scripts don't shell out across plugins.
- `plugin-health/SKILL.md` already calls `validate-plugin` as a sub-step (line "Invoke the existing validate-plugin skill") — the three are already implicitly layered.
- `/kit-sync` and `/kit-update` already share `skills/kit-sync/SKILL.md`; they're two entry points to one skill.
- style-agent has **2** skills (`css-to-class`, `inline-style-to-class`).

**Intended outcome:** simpler installs, one canonical source per concept, fewer thin wrappers, maintainer skills co-located with the plugin they describe.

---

## Dependency diagram

```
Phase 1 (docs + maintainer tools) — no user-facing API change
    │
    ▼
Phase 2 (absorb pilots, collapse stub commands inside acss-kit)
    │
    ▼
Phase 3 (parametrize React/HTML target split)
    │
    ▼
Phase 4 (merge acss-utilities into acss-kit — major bump)
    │
    ▼
Phase 5 (script-library consolidation inside acss-kit)
```

Each phase is one PR with its own version bump. `tests/run.sh` must stay green after every phase.

---

## Phase 1 — Docs, maintainer skills, hook hygiene
**Scope:** no user-facing API change. Plugin versions un-bumped.

### 1a. Fix the top-level README version table

**File:** `README.md` lines 16–17

Current values are stale (`0.7.0`, `0.4.0`) and omit `style-agent`. Update to:
- acss-kit → `0.11.2`
- acss-utilities → `0.5.0`
- Add style-agent row: `0.2.0`, description from `plugins/style-agent/.claude-plugin/plugin.json`

Verify: `grep -E '0\.11\.2|0\.5\.0|0\.2\.0' README.md` returns three lines.

### 1b. Move six acss-kit–specific maintainer skills into the plugin

Move these six skill directories from `.claude/skills/` to `plugins/acss-kit/skills/_maintainer/`:
- `component-author/`
- `component-update/`
- `style-author/`
- `style-update/`
- `test-component/`
- `changelog-entry/`

Each SKILL.md `name:` front-matter stays as-is. Update the maintainer-tooling table in `CLAUDE.md` to show paths under `plugins/acss-kit/skills/_maintainer/`. Skills under `plugins/` are loaded by Claude Code when the plugin is active, so resolution is unchanged.

Verify: `ls .claude/skills/` no longer contains those six dirs. `tests/run.sh` green.

### 1c. Merge `validate-plugin` + `verify-plugins` + `plugin-health` into one skill

**Target:** `.claude/skills/validate-plugins/SKILL.md` (new, replaces three)

The merged skill routes by `--scope=plugin|all|health`:
- `--scope=plugin <name>` → current `validate-plugin` behavior (deep per-plugin check)
- `--scope=all` → current `verify-plugins` sweep across all plugins
- `--scope=health` → current `plugin-health` dashboard (which already calls validate-plugin internally)

Default with no `--scope` and a name argument: `plugin` scope. Default with no arguments: `all` scope.

Delete: `.claude/skills/validate-plugin/`, `.claude/skills/verify-plugins/`, `.claude/skills/plugin-health/`.

Update `CLAUDE.md` maintainer-tooling table to show `validate-plugins` as the single entry.

Verify: `validate-plugins --scope=all` reproduces the previous `verify-plugins` output format. `--scope=health acss-kit` reproduces the plugin-health dashboard.

### 1d. Merge `release-plugin` + `release-check` into one skill

**Target:** `.claude/skills/release-plugin/SKILL.md` (rewrite in place)

Add a `--check` mode that runs only the paperwork audit (current `release-check` behavior). Without `--check`, perform the version bump (current `release-plugin` behavior). Usage: `release-plugin acss-kit 0.12.0` (bump) or `release-plugin acss-kit --check` (audit).

Delete: `.claude/skills/release-check/`

Update `CLAUDE.md` to show only `release-plugin` in the maintainer-tooling table.

Verify: `release-plugin acss-kit --check` produces the old release-check checklist output. `release-plugin acss-kit 0.12.0` (dry-run inspection, do not actually bump) shows version-bump steps.

### 1e. Trim `.claude/rules/python-scripts.md`

**File:** `.claude/rules/python-scripts.md`

Remove the per-script inventory listing (all lines after "## Internal module contract"). Keep only: front-matter `paths:`, the two contract family definitions (detector vs. generator/validator), and the internal module contract. Target: under 40 lines (from current ~110 lines).

The inventory rots every time a script is added. The contract definitions are the durable, reusable part.

Verify: file is under 40 lines; `wc -l .claude/rules/python-scripts.md` confirms.

### 1f. Remove duplicate `commands.md` docs

**Files:** `plugins/acss-kit/docs/commands.md`, `plugins/acss-utilities/docs/commands.md`

Both duplicate the command front-matter that already lives in `commands/*.md`. The `prompt-book` skill and `docs/prompt-book.md` in acss-kit cover the narrative user-facing angle. Update each plugin's `docs/README.md` index to remove the `commands.md` link.

Verify: each plugin's docs index links to one authoritative command reference, not two.

### Phase 1 exit criteria
- `tests/run.sh` green from a clean checkout
- `ls .claude/skills/` shows: `add-command`, `release-plugin`, `validate-plugins` (seven skills removed, one renamed, two merged)
- `grep '0\.11\.2' README.md` and `grep 'style-agent' README.md` both succeed
- `.claude/rules/python-scripts.md` under 40 lines

---

## Phase 2 — Absorb pilot skills, collapse stub commands (one PR, acss-kit minor bump)

### 2a. Fold `component-creator` into `skills/components/SKILL.md`

Add a "# Creator mode (natural-language input)" section at the end of `skills/components/SKILL.md`. The section title and auto-trigger description from `component-creator/SKILL.md` front-matter become the routing trigger. Repoint `commands/kit-create.md` to `skills/components/SKILL.md#creator-mode`.

Delete `skills/component-creator/`.

Verify: `/kit-create "primary pill button labelled Buy"` still produces TSX.

### 2b. Fold `component-form` into `skills/components/SKILL.md`

Add a "# Form scaffolding" section. Delete `skills/component-form/`.

Verify: "create a signup form with email + password" still produces accessible form TSX.

### 2c. Fold `style-tune` into `skills/styles/SKILL.md` and `skills/components/SKILL.md`

The routing logic ("is this a theme role or a component token?") becomes a two-line prefix in each parent's tuning section. Delete `skills/style-tune/`.

Verify: `/style-tune "warmer button"` edits `--btn-*` tokens; `/style-tune "deeper primary"` edits a theme role and triggers WCAG re-validation.

### 2d. Collapse five theme commands into one `/theme` command

Replace `theme-create.md`, `theme-extract.md`, `theme-brand.md`, `theme-update.md`, `color-scale.md` with a single `commands/theme.md` that routes by sub-action. Keep the old files as one-line deprecation stubs for one minor-version window: "Use `/theme create` instead."

Verify: `/theme create #336699`, `/theme extract <url>`, `/theme brand foo`, `/theme update`, `/theme color-scale` all reach correct SKILL.md sections.

### 2e. Remove `kit-update` command stub

Since `/kit-sync` and `/kit-update` already share `skills/kit-sync/SKILL.md`, consolidate to `/kit-sync --update` or expose both as one `/kit <sync|update>` command. Delete `commands/kit-update.md` after adding `--update` support in `commands/kit-sync.md`.

Verify: old `/kit-update` workflow reachable via new command surface.

### 2f. CHANGELOG + version bump

Update `plugins/acss-kit/CHANGELOG.md` with a "Consolidated skills" entry. Bump `plugin.json` minor version via `release-plugin acss-kit`.

---

## Phase 3 — Parametrize the React/HTML target split (one PR, acss-kit minor bump)

### 3a. Merge `components-html/SKILL.md` into `components/SKILL.md`

Add a "Target: HTML" subsection. Default target is `react`; HTML path activates when `.acss-target.json#target == "html"`. Delete `skills/components-html/`.

### 3b. Replace `kit-add-html.md` with a deprecation alias

`kit-add-html.md` → one-line stub pointing to `/kit-add --target=html`. Remove after next minor version.

### 3c. Add `_target.py` shared module

`plugins/acss-kit/scripts/_target.py` — common ancestor-walk, `.acss-target.json` read/write, CSS-entry probes. Underscore-prefix marks it internal (no CLI, no detector contract).

### 3d. Replace `detect_target.py` + `detect_html_target.py` with one parametrized script

`detect_target.py --target=react|html` (default: `react`). Import from `_target.py`. Delete `detect_html_target.py`.

### 3e. Replace `verify_integration.py` + `verify_html_integration.py` with one parametrized script

`verify_integration.py --target=react|html`. Import from `_target.py`. Delete `verify_html_integration.py`.

### 3f. CHANGELOG + minor bump

Verify: `tests/e2e.sh` green for both target paths.

---

## Phase 4 — Merge `acss-utilities` into `acss-kit` (one PR, acss-kit major bump to v1.0.0)

### 4a. Copy utilities skill and commands into acss-kit

Copy `plugins/acss-utilities/skills/utilities/` → `plugins/acss-kit/skills/utilities/`. Move or collapse `utility-add.md`, `utility-bridge.md`, `utility-list.md`, `utility-tune.md` into `plugins/acss-kit/commands/` (option: collapse to one `/utility <action>` command following the `/theme` pattern from Phase 2).

### 4b. Move assets and eliminate role-name duplication

Move `plugins/acss-utilities/assets/` → `plugins/acss-kit/assets/utilities/`. Rewrite `utilities.tokens.json` so role names are derived from `acss-kit/scripts/tokens_to_css.py#ROLE_GROUPS` rather than asserted independently. Document the sync step so new roles propagate to utilities on next `generate_utilities.py` run.

### 4c. Fix cross-plugin coupling in SKILL.md

Replace the `${CLAUDE_PLUGIN_ROOT}/../acss-kit/scripts/...` references in the utilities skill with `${CLAUDE_PLUGIN_ROOT}/scripts/...` (now that both live in acss-kit). Remove the "skip if acss-kit absent" guard — it's always present.

### 4d. Move acss-utilities scripts into acss-kit

Move `generate_utilities.py`, `migrate_classnames.py`, `validate_utilities.py` to `plugins/acss-kit/scripts/`. Replace `detect_utility_target.py` with a thin wrapper around `_target.py --what=utilities` (created in Phase 3).

### 4e. Eliminate hardcoded hex fallbacks in `token-bridge.css`

Generate the bridge from the active theme at `/theme create` time. Document this as a mandatory post-step when regenerating a theme.

### 4f. Publish terminal release of `acss-utilities`

v1.0.0 CHANGELOG: "Migrated into acss-kit. Install acss-kit v1+ for utilities." Strip all skills/scripts to a README deprecation notice. Keep manifest entry so existing installs don't 404.

### 4g. Bump acss-kit to v1.0.0

Update marketplace.json description and top-level README.

Verify: fresh acss-kit v1.0.0 install exposes `/utility add`; `acss-utilities` install prints deprecation notice pointing at acss-kit.

---

## Phase 5 — Script-library consolidation (one PR, acss-kit minor bump)

### 5a. Merge the `detect_*` family

`detect.py --what=stack|target|css-entry|pm|utilities` replaces five scripts (`detect_stack.py`, `detect_target.py`, `detect_css_entry.py`, `detect_package_manager.py`, plus the utilities wrapper from Phase 4). Shared logic stays in `_target.py`. Delete the five individual files after repointing all SKILL.md callers and command files.

### 5b. Merge manifest scripts

`manifest.py <read|write|diff>` replaces `manifest_read.py`, `manifest_write.py`, `diff_status.py`. Keep `hash_file.py` standalone (it has a distinct hash-normalization contract used independently). Delete the three individual files after repointing callers.

### 5c. Extract `_tokens.py` shared module

Common JSON↔CSS variable logic shared by `tokens_to_css.py` and `css_to_tokens.py` (315 lines combined, explicit inverses). Both scripts import from `_tokens.py`; neither script is deleted (they remain distinct entry points).

Verify: round-trip JSON → CSS → JSON on a fixture theme produces byte-identical JSON.

### 5d. Rename misleading test helpers

`tests/validate_components.mjs` → `tests/validate_extracted_tsx.mjs`
`tests/validate_components.py` → `tests/validate_extracted_scss.py`

Update `tests/run.sh` call sites and `tests/README.md` references.

### 5e. CHANGELOG + minor bump

Verify: `tests/run.sh` green. All previous detect/manifest command invocations in SKILL.md files resolve to the new subcommand form.

---

## End-to-end verification

After each phase:
- `tests/run.sh` green (one-time install: `npm --prefix tests ci && pip3 install --user tinycss2`)
- `tests/e2e.sh` green (after Phase 3 and again after Phase 4)
- Local install `claude --plugin-dir ./plugins/acss-kit` exposes expected commands for that phase

Phase-specific checks:
- **Phase 1**: `ls .claude/skills/` shows 3 skills (add-command, release-plugin, validate-plugins). README shows correct versions. python-scripts.md under 40 lines.
- **Phase 2**: `/theme create #336699` works; `/theme-create #336699` prints deprecation hint. acss-kit skill count: 9 → 5.
- **Phase 3**: `/kit-add --target=html` produces HTML+SCSS+JS; `/kit-add-html` prints deprecation hint. Script count: 19 → 17 (two merged pairs).
- **Phase 4**: Fresh install of acss-kit exposes `/utility add`; `acss-utilities` install prints tombstone notice. Role-name round-trip: add synthetic role to ROLE_GROUPS → regenerate → bridge reflects it.
- **Phase 5**: `python3 plugins/acss-kit/scripts/detect.py --what=stack` produces same JSON as old `detect_stack.py`. Round-trip JSON → CSS → JSON byte-identical.

---

## Critical files per phase

| Phase | Files modified / created / deleted |
|---|---|
| 1 | `README.md`, `.claude/skills/` (7 dirs removed, 2 merged), `CLAUDE.md`, `.claude/rules/python-scripts.md`, `plugins/*/docs/commands.md` |
| 2 | `plugins/acss-kit/skills/components/SKILL.md`, `skills/styles/SKILL.md`, `commands/theme.md` (new), `commands/theme-*.md` (stub), `commands/kit-sync.md`, CHANGELOG, `plugin.json` |
| 3 | `scripts/_target.py` (new), `scripts/detect_target.py`, `scripts/verify_integration.py`, `commands/kit-add.md`, `commands/kit-add-html.md` (stub), CHANGELOG, `plugin.json` |
| 4 | `plugins/acss-kit/skills/utilities/` (new), `assets/utilities/` (new), `scripts/generate_utilities.py` + `migrate_classnames.py` + `validate_utilities.py` (moved), `plugins/acss-utilities/` (tombstone), CHANGELOG, `plugin.json` |
| 5 | `scripts/detect.py` (new), `scripts/manifest.py` (new), `scripts/_tokens.py` (new), old scripts deleted, `tests/validate_*.{mjs,py}` renamed, `tests/run.sh`, `tests/README.md` |

---

## Out of scope

- `style-agent` — keep as-is; adding a `/utility-extract` inverse skill is a future decision after demand is established.
- A `--dry-run` flag on `/theme create` and `/kit-add` — useful but not blocking.
- Auto-generating `marketplace.json` from `plugin.json` — would eliminate description-drift risk; worth doing after Phase 1 if drift returns.
- Whether to keep `plugins/acss-utilities/` in-tree as a tombstone vs. removing it from git — either works; the choice is purely cosmetic after Phase 4.