---
name: validate-plugins
description: "Validate plugin structure and health. --scope=plugin (deep single-plugin check), --scope=all (fast repo-wide sweep), --scope=health (full health dashboard)."
disable-model-invocation: false
---

# /validate-plugins

Usage: `/validate-plugins [<plugin-name>] [--scope=plugin|all|health]`

Route by `--scope`:

- `--scope=plugin` — deep validation of one plugin before publishing (default when a name is given)
- `--scope=all` — fast structural sweep across every plugin in the repo (default when no name is given)
- `--scope=health` — full health dashboard for one plugin (structure + components + catalog + themes)

---

## --scope=plugin — Deep single-plugin validation

Usage: `/validate-plugins acss-kit` or `/validate-plugins acss-kit --scope=plugin`

Run each check in order. Report all failures at the end, not one at a time.

### 1. Manifest
- `plugins/<plugin>/.claude-plugin/plugin.json` exists and is valid JSON
- Required fields present: `name`, `description`, `version`, `author`, `license`
- `version` is a valid semver string
- `claudeCodeMinVersion` is present (warn if missing, don't fail)

### 2. Marketplace entry
- `.claude-plugin/marketplace.json` has an entry matching the plugin name
- The entry does **not** have a `"version"` field (this causes silent conflicts)
- `description` is non-empty

### 3. Required files
- `README.md` exists
- `commands/` directory exists and contains at least one `.md` file
- `skills/` directory exists and contains at least one `SKILL.md`

### 4. Command files
For each `commands/*.md`:
- Has valid YAML front-matter with `description` and `allowed-tools` fields
- Body references `SKILL.md` (not re-implements logic inline)
- Does not contain repo-relative paths to fpkit source (e.g., `../../acss/`)

### 5. SKILL.md references
- No repo-relative fpkit source links — all fpkit references must be full GitHub URLs (`https://github.com/shawn-sandy/acss/...`)
- Each command mentioned in the SKILL.md has a corresponding `commands/*.md` file

### 6. Python scripts (if present)
- Run `python3 -m py_compile <script>` on each `.py` file in `plugins/<plugin>/scripts/`
- Report any syntax errors

### 7. Assets
- If `assets/` exists, verify no `.tmpl` files contain un-substituted `{{PLACEHOLDER}}` tokens that don't follow the `{{ALL_CAPS}}` convention

### Output

```text
PASS  Manifest fields
PASS  Marketplace entry
FAIL  Command files — app-init.md missing allowed-tools front-matter
PASS  SKILL.md references
...
```

Exit with a count of failures. If zero failures: "Plugin <name> is ready to publish."

---

## --scope=all — Fast repo-wide structural sweep

Usage: `/validate-plugins --scope=all`

Scans every directory under `plugins/` and reports pass/fail for each. No plugin name needed.

Run these checks for each `plugins/*/` directory:

### 1. Manifest exists and has required fields

```bash
jq -e '(.name | type == "string" and length > 0) and (.version | type == "string" and length > 0) and (.description | type == "string" and length > 0)' plugins/<plugin>/.claude-plugin/plugin.json
```

- PASS if file exists and all three fields are non-null/non-empty strings.
- FAIL if file is missing or any field is absent or empty.

### 2. Marketplace entry has no `version` key

Read `.claude-plugin/marketplace.json`. Run two checks in sequence.

First verify the entry exists:
```bash
jq -e --arg p "<plugin>" '.plugins | map(.name) | index($p) != null' .claude-plugin/marketplace.json
```
- FAIL if absent: "marketplace.json has no entry for <plugin> — add one."

Then verify no `version` key:
```bash
jq -e '.plugins[] | select(.name == "<plugin>") | has("version") | not' .claude-plugin/marketplace.json
```
- FAIL: "marketplace.json entry for <plugin> carries a `version` key — remove it."

### 3. Required files present

- `plugins/<plugin>/README.md`
- `plugins/<plugin>/skills/` containing at least one `SKILL.md`
- `plugins/<plugin>/commands/` containing at least one `.md` file

### Output

```text
plugins/acss-kit
  PASS  Manifest fields (name, version, description)
  PASS  Marketplace entry has no version key
  PASS  README.md present
  PASS  skills/ contains SKILL.md files
  PASS  commands/ has .md files

Summary: 2 plugins checked, 0 failures total.
```

After the sweep, offer: "Run `/validate-plugins <name>` for a full pre-publish check on any plugin above."

---

## --scope=health — Full health dashboard

Usage: `/validate-plugins acss-kit --scope=health`

Produces a single dashboard summarizing structural and content health. Read-only — does NOT modify any files.

### Step 1 — Resolve target

If no argument is provided, default to `acss-kit`. Confirm `plugins/<plugin-name>/.claude-plugin/plugin.json` exists. If not, list available plugins and halt.

### Step 2 — Structural validation

Run the `--scope=plugin` checks above on `<plugin-name>`. Capture output as the "Structure" section.

### Step 3 — Component reference scan

For each file under `plugins/<plugin-name>/skills/components/references/components/*.md` (excluding `catalog.md`):

1. Check whether the file contains all nine canonical sections (verification banner, Overview, Generation Contract, Props Interface, TSX Template, CSS Variables, SCSS Template, Accessibility, Usage Examples).
2. Mark `OK` if all present, `FIX` if any are missing or out of order.

Roll up to: `N components OK / M components FIX`.

### Step 4 — Catalog parity

1. Read `plugins/<plugin-name>/skills/components/references/components/catalog.md`. Extract every component name from the "Verification Status" table.
2. Compare to `*.md` files in `references/components/` (excluding `catalog.md`).
3. Report orphans (file present, no catalog row) and stale rows (catalog row, no file).

### Step 5 — Theme reference parity

Invoke the `theme-reference-reviewer` agent. Capture its check verdicts. Each FAIL becomes a row in the "Themes" section.

### Step 6 — Bundled theme validation

`validate_theme.py` only validates files matching `^(light|dark|brand-[\w-]+)\.css$`.

1. Build the candidate file list from `assets/` and `assets/brand-presets/` (if present).
2. Run `python3 plugins/<plugin-name>/scripts/validate_theme.py <file>` for each candidate (timeout 30s).
3. Classify: exit 0 + `validate_theme: OK` → PASS; exit 1 → FAIL; `no palette files found` in stdout → INFO (not PASS).

### Step 7 — Render the dashboard

```text
== plugin-health: <plugin-name> @ v<version> ==

Structure              [OK | FIX] <one-line summary>
Components             [OK | FIX] N OK / M FIX
Catalog parity         [OK | FIX] <orphans/stale counts>
Theme references       [OK | FIX] <fail count>
Bundled themes         [OK | FIX] <preset pass/fail counts>

-- Detail --

Components needing attention:
  - <name>.md — missing: Accessibility

Catalog issues:
  - Orphan: <name>.md (file present, no catalog row)

Bundled theme failures:
  - <file> — <failing pair name>

-- Suggested fixes --

  Run /validate-plugins <name>           (for each Structure FIX)
  Run /acss-kit-component-update <name>  (for each Component FIX)
  Run /acss-kit-style-update <path>      (for each Theme FIX)
  Manual: edit catalog.md                (for each Catalog issue)
```

If everything is OK: "All systems green. Plugin is release-ready."

### Step 8 — Pre-release reminder

```text
Before opening a PR:
  1. Run /release-plugin <plugin-name> <new-version>
  2. Confirm plugins/<plugin-name>/CHANGELOG.md mentions user-visible changes
```
