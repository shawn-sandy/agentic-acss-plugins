# Plan: Execute Phase 1 of simplify-acss-plugins-marketplace

## Context

The branch `refactor/phase-1-simplify-plugins` is parked at the front of Phase 1 of [simplify-acss-plugins-marketplace.md](./simplify-acss-plugins-marketplace.md). The user picked that file as canonical (tag-in-place for maintainer skills, not move-into-plugin). Phase 1 has seven sub-steps; the README fix is already in the working tree but uncommitted. This plan executes the remaining six.

## Objective

Land Phase 1 end-to-end as a sequence of focused commits on the existing branch — no plugin version bumps, `tests/run.sh` green throughout. Each commit covers one Phase-1 sub-step so the PR is easy to review.

## Steps

<ol>

<li>

**Commit 1.1 — README version table fix (already staged in working tree).** Verify the README rows match `plugin.json` (`acss-kit 0.11.2`, `acss-utilities 0.5.0`, `style-agent 0.2.0`), confirm style-agent row is present, then commit only `README.md` plus the related `CLAUDE.md` touch.

*Why:* this work is already done; commit it cleanly before touching anything else so subsequent commits stay focused.

*Verify:* `grep -E '0\.11\.2|0\.5\.0|0\.2\.0' README.md` returns three lines; `git log -1 --stat` shows only `README.md` (and `CLAUDE.md` if related) in the commit.

</li>

<li>

**Commit 1.2 — Tag six maintainer skills as `acss-kit-*` with `[Maintainer]` prefix.** Rename the six skill dirs under `.claude/skills/`: `changelog-entry → acss-kit-changelog-entry`, `component-author → acss-kit-component-author`, `component-update → acss-kit-component-update`, `style-author → acss-kit-style-author`, `style-update → acss-kit-style-update`, `test-component → acss-kit-test-component`. In each SKILL.md, update `name:` to match the new dir and prepend `[Maintainer]` to `description:` (if not already present). Update the maintainer-tooling table in `CLAUDE.md`. Land the pending description-trim edits in the same commit so the working tree is clean.

*Why:* tagging suppresses auto-triggering in user sessions and makes the maintainer/cross-plugin split obvious in `ls .claude/skills/`.

*Verify:* `ls .claude/skills/acss-kit-*` lists six dirs; `grep -l '^description:.*\[Maintainer\]' .claude/skills/acss-kit-*/SKILL.md | wc -l` returns 6; `tests/run.sh` green.

</li>

<li>

**Commit 1.3 — Merge `validate-plugin` + `verify-plugins` + `plugin-health` into one `validate-plugins` skill** with `--scope=plugin|all|health` routing. Read all three SKILL.md files first, design the merged body, write `.claude/skills/validate-plugins/SKILL.md`, delete the three originals. Update any cross-references in `CLAUDE.md`, the plan files, or commands.

*Why:* three skills doing layered structural validation is the most concentrated maintainer-tooling bloat. `plugin-health` already calls `validate-plugin` as a sub-step.

*Verify:* invoking the new skill with `--scope=all` reproduces verify-plugins output for a sample plugin; `--scope=health` reproduces plugin-health checklist; `tests/run.sh` green.

</li>

<li>

**Commit 1.4 — Merge `release-plugin` + `release-check` into one skill with a `--check` mode.** Same pattern as 1.3: read both, write one, delete the other, update references.

*Why:* the two pair in workflow but ship separately.

*Verify:* `release-plugin --check acss-kit` produces the old release-check report; without `--check` it produces the version-bump workflow.

</li>

<li>

**Commit 1.5 — Document the WCAG + utility-CSS hooks in `.claude/hooks.md`.** Read `.claude/settings.json` for the full hook list, read current `.claude/hooks.md`, add entries for any PostToolUse hooks not yet documented. Keep all existing hooks.

*Why:* documentation parity — these hooks provide real-time feedback that `validate-plugin` only catches in batch.

*Verify:* `.claude/hooks.md` enumerates all PostToolUse + PreToolUse hooks from `.claude/settings.json`.

</li>

<li>

**Commit 1.6 — Strip the script inventory out of `.claude/rules/python-scripts.md`.** Keep the stdlib-only contract and the detector-vs-generator distinction. Delete the per-script listing.

*Why:* the rule injects ~7 KB into context on every script edit and the inventory rots every time a script is added.

*Verify:* `wc -c .claude/rules/python-scripts.md` < 2000; file contains contract sections but no per-script bullets.

</li>

<li>

**Commit 1.7 — Resolve `docs/commands.md` vs `docs/prompt-book.md` per plugin.** For each of `plugins/acss-kit/docs/` and `plugins/acss-utilities/docs/`: if both exist, delete `commands.md` and keep `prompt-book.md`. Update each plugin's `docs/README.md` to link only to the prompt book.

*Why:* one source of truth for the command catalogue.

*Verify:* `find plugins -name commands.md` returns only `plugins/acss-utilities/docs/commands.md` (kept — no prompt-book.md exists there); `plugins/acss-kit/docs/README.md` links to `prompt-book.md` only.

</li>

</ol>

## Verification

End-to-end Phase-1 exit:
- `tests/run.sh` green
- `git diff main...HEAD --stat` shows seven focused commits matching the steps above
- No plugin `version:` field touched in any `plugin.json` (Phase 1 is non-user-facing)
- `ls .claude/skills/` shows: `acss-kit-{changelog-entry,component-author,component-update,style-author,style-update,test-component}`, `add-command`, `release-plugin` (with `--check` mode), `validate-plugins` — and nothing else
- `plugins/acss-kit/.claude-plugin/plugin.json` and the others remain at their current versions

## Next steps (out of scope)

- Phase 2: absorb pilot skills (`component-creator`, `component-form`, `style-tune`) into parent skills. Requires the skill-listing budget raise from `docs/plans/raise-skilllistingbudgetfraction-current-jiggly-pie.md` as a prerequisite.
- Delete `synthetic-hugging-newt-ultraplan.md` as a discarded alternative once Phase 1 lands, so future readers don't re-litigate the maintainer-skill location decision.
