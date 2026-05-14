---
name: release-plugin
description: "Bump a plugin's version and check release paperwork. Use --check to audit CHANGELOG/README before opening a PR; omit --check to do the version bump."
disable-model-invocation: false
---

# /release-plugin

Two modes:

- **Version bump** — `/release-plugin <plugin-name> <new-version>` — bumps `plugin.json`, cleans up `marketplace.json`.
- **Release check** — `/release-plugin <plugin-name> --check` — audits whether the paperwork is complete on the current branch before opening a PR.

---

## Version bump mode

Usage: `/release-plugin acss-kit 0.3.1`

1. **Confirm the plugin exists** — verify `plugins/<plugin-name>/.claude-plugin/plugin.json` exists. If not, list available plugins from `.claude-plugin/marketplace.json` and stop.

2. **Read current version** from `plugins/<plugin>/.claude-plugin/plugin.json`.

3. **Validate the new version** — must be a valid semver string (`MAJOR.MINOR.PATCH`). Refuse if not.

4. **Bump `plugin.json`** — update the `"version"` field in `plugins/<plugin>/.claude-plugin/plugin.json`.

5. **Check marketplace.json** — read `.claude-plugin/marketplace.json`. If the matching plugin entry contains a `"version"` key, **remove it** and warn the user ("marketplace.json should not have a version field — the plugin.json always wins").

6. **Ask the user** if the marketplace.json `description` for this plugin needs updating to reflect the change. If yes, update it.

7. **Print a pre-commit summary**:
   - Plugin bumped: `<plugin>` `<old>` → `<new>`
   - Files modified: list them
   - Reminder: "Run the pre-submit checklist in CLAUDE.md before committing."

Do not commit. Do not push. Leave that to the user.

---

## --check mode — Release paperwork audit

Usage: `/release-plugin acss-kit --check`

Audits whether the release paperwork is complete on the current branch. Does **not** perform a version bump. Run this after the version bump and before opening a PR.

### 1. Confirm plugin exists

Verify the argument matches a directory under `plugins/`. If not, list available plugins and stop.

### 2. Diff main...HEAD for the plugin

```bash
git diff main...HEAD --name-only -- plugins/<plugin>/
```

Collect the list of changed files scoped to `plugins/<plugin>/`.

### 3. Check version bump

- Attempt to read `plugins/<plugin>/.claude-plugin/plugin.json` from `main` via `git show main:plugins/<plugin>/.claude-plugin/plugin.json`.
- If that exits non-zero (new plugin): PASS with note "New plugin — initial version establishes the baseline."
- Otherwise compare `version` fields between `main` and `HEAD`.
- PASS if the field differs. FAIL if unchanged: "plugin.json version not bumped — run `/release-plugin <name> <new-version>` first."

### 4. Check CHANGELOG touched

- PASS if `plugins/<plugin>/CHANGELOG.md` appears in the diff.
- FAIL if absent: "CHANGELOG.md not updated — add an entry for this release."

### 5. Check README updated when commands or SKILL changed

If any of `plugins/<plugin>/commands/*.md` or `plugins/<plugin>/skills/**/SKILL.md` are in the diff, then `plugins/<plugin>/README.md` must also be in the diff.

- PASS if README is touched or no trigger paths changed.
- FAIL: "commands/ or SKILL.md changed — update README.md to reflect new behavior."

### 6. Check marketplace.json description (informational)

The root marketplace.json is not scoped to the plugin dir. Run a separate unscoped diff:

```bash
git diff main...HEAD --name-only
```

If `.claude-plugin/marketplace.json` appears, note it as touched. If not, remind: "Consider updating `.claude-plugin/marketplace.json` description if this change is user-facing."

### Output

```
Release checklist for acss-kit (main...HEAD)

  [PASS] plugin.json version bumped (0.2.1 → 0.3.0)
  [FAIL] CHANGELOG.md not updated
  [PASS] README.md updated alongside command changes
  [INFO] marketplace.json not touched — update description if change is user-facing

1 item needs attention before opening a PR.
```

If all required checks pass: "Release paperwork complete. Ready to open a PR."

Do not commit, push, or open the PR — leave that to the user or `/ship`.
