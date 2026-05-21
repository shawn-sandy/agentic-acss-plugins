# Project Hooks

Hooks defined in `.claude/settings.json` run before or after specific tool calls. They enforce repo conventions automatically — every contributor on every machine, no opt-in needed.

## Files

| File | Committed? | Purpose |
|---|---|---|
| `.claude/settings.json` | Yes | Hook definitions. Shared across the team. |
| `.claude/settings.local.json` | No (gitignored) | Personal permissions allowlist and local overrides like `plansDirectory`. |

If a hook misbehaves, the fix is in `settings.json` — not in `settings.local.json`.

## PostToolUse — advisory checks after `Write` or `Edit`

These run after Claude writes or edits a file. They warn or fail loudly so issues are caught before commit.

### 1. WCAG contrast check

| Field | Value |
|---|---|
| Matcher | `Write\|Edit` |
| Status message | `Checking WCAG contrast...` |
| Behaviour | If the touched file matches `plugins/acss-kit/assets/themes/*.css`, runs `python3 plugins/acss-kit/scripts/validate_theme.py <file>` (timeout 15s). Failures print to stdout. |
| Why | Theme CSS edits can push color-role pairs below WCAG 2.2 AA contrast thresholds. Running the validator inline catches regressions before commit without requiring a manual batch run. |

### 2. Utility CSS validator

| Field | Value |
|---|---|
| Matcher | `Write\|Edit` |
| Status message | `Validating utility CSS...` |
| Behaviour | If the touched file matches `plugins/acss-kit/assets/utilities/*.css`, runs `python3 plugins/acss-kit/scripts/validate_utilities.py <file>` (timeout 15s). Failures print to stdout. |
| Why | Utility CSS files have structural contracts (kebab-case selectors, `var()` fallbacks, responsive parity, no duplicates). The hook enforces these on every edit rather than only at batch-validation time. |

### 3. JSON validator

| Field | Value |
|---|---|
| Matcher | `Write\|Edit` |
| Status message | `Validating JSON...` |
| Behaviour | If the touched file ends in `.json`, parses it with `python3 json.load`. Parse errors print to stdout (the hook redirects stderr via `2>&1`) and the command exits non-zero, surfacing as a PostToolUse error. |
| Why | Catches truncated edits in `plugin.json`, `marketplace.json`, `theme.tokens.json` before they propagate. |

### 4. plugin.json schema check

| Field | Value |
|---|---|
| Matcher | `Write\|Edit` |
| Status message | `Checking plugin.json schema...` |
| Behaviour | If the touched file matches `plugins/*/.claude-plugin/plugin.json`, runs `jq` to confirm `name`, `version`, and `description` are non-empty strings. **Exits 2 on failure**, blocking the operation. |
| Why | Plugin manifests are silently authoritative for `/plugin update` — a broken manifest is a release-blocker. |

### 5. Command front-matter check

| Field | Value |
|---|---|
| Matcher | `Write\|Edit` |
| Status message | `Checking command front-matter...` |
| Behaviour | If the touched file matches `plugins/*/commands/*.md`, warns when `description:` or `allowed-tools:` is missing from the YAML front-matter. Warning only — no exit code. |
| Why | These two fields drive how Claude surfaces and gates the command — easy to forget when scaffolding by hand. |

### 6. SKILL.md front-matter check

| Field | Value |
|---|---|
| Matcher | `Write\|Edit` |
| Status message | `Checking SKILL.md front-matter...` |
| Behaviour | If the touched file ends in `/SKILL.md`, warns when `name:` or `description:` is missing. Warning only — no exit code. |
| Why | Same reason as the command check — front-matter is the contract Claude reads to decide when a skill applies. |

## PreToolUse — gates before `Bash`

These run before Claude executes a Bash command. They can block dangerous operations.

### 7. Main-branch guard

| Field | Value |
|---|---|
| Matcher | `Bash` |
| Status message | `Checking branch guard...` |
| Behaviour | If the command is `git commit` or `git push` (any form that targets `main`), and the current branch is `main`, **exits 2 to block** with `[main-guard] BLOCKED: direct commit/push to main is not allowed. Use a feature branch.` |
| Why | Project policy is feature-branch + PR; this stops accidental direct commits to `main`. Includes both `git push origin main`-style and naked `git push` while on `main`. |

## Adding a new hook

1. Open `.claude/settings.json` and add an entry under `hooks.PostToolUse` or `hooks.PreToolUse`.
2. `matcher` is a regex against the tool name (`Write|Edit`, `Bash`, etc.).
3. `command` is shell that reads the tool input from stdin via `jq`. Exit `0` to pass, `2` to block (PreToolUse) or surface as an error (PostToolUse).
4. Add a `statusMessage` so contributors see what's running.
5. Document the hook in this file.

For deeper guidance see the Claude Code docs on hooks.
