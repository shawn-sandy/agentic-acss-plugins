# Maintainer Skills

Project-local skills for working on the `acss-kit` plugin. These are distinct from the plugin's own end-user skills (which live under `plugins/acss-kit/skills/`) — these run **on this repo while you maintain it**.

Each skill has a slash command of the same name. Skills prefixed `acss-kit-` are maintainer-only and tagged `[Maintainer]` in their descriptions to suppress auto-triggering in user sessions.

## Authoring — scaffold new artifacts

| Skill | What it does |
|---|---|
| [`/add-command`](add-command/SKILL.md) | Scaffold a new slash command for a plugin — creates `commands/<name>.md` with front-matter and adds a stub section to the relevant `SKILL.md`. |
| [`/acss-kit-component-author`](acss-kit-component-author/SKILL.md) | Scaffold a new per-component skill at `plugins/acss-kit/skills/component-<name>/` with `SKILL.md` and `reference.md` in the canonical embedded-markdown shape. |
| [`/acss-kit-style-author`](acss-kit-style-author/SKILL.md) | Scaffold a bundled brand preset, palette role, or theme-schema field for `acss-kit`. Three sub-flows; ends with a WCAG 2.2 AA contrast re-validation. |

## Updating — refresh existing artifacts

| Skill | What it does |
|---|---|
| [`/acss-kit-component-update`](acss-kit-component-update/SKILL.md) | Re-verify an existing component reference doc against its captured fpkit ref, surface drift in TSX/SCSS templates, and run the canonical-shape reviewer agent. |
| [`/acss-kit-style-update`](acss-kit-style-update/SKILL.md) | Re-validate and roll forward theme assets after edits to `role-catalogue.md`, `palette-algorithm.md`, `theme.schema.json`, or a bundled brand preset. |

## Validation — read-only audits

| Skill | What it does |
|---|---|
| [`/validate-plugins`](validate-plugins/SKILL.md) | Structural validation at three scopes: `--scope=plugin` (deep single-plugin check), `--scope=all` (fast repo-wide sweep), `--scope=health` (full health dashboard). |

## Release — pre-PR paperwork

| Skill | What it does |
|---|---|
| [`/release-plugin`](release-plugin/SKILL.md) | Bump a plugin's version in `plugin.json` and update `marketplace.json` description if needed. Use `--check` mode to audit whether release paperwork is complete before opening a PR. |

## Changelog

| Skill | What it does |
|---|---|
| [`/acss-kit-changelog-entry`](acss-kit-changelog-entry/SKILL.md) | Generate a Keep-a-Changelog entry for `acss-kit` from git log since last tag. Groups commits by conventional type and appends to `CHANGELOG.md`. |
| [`/acss-kit-test-component`](acss-kit-test-component/SKILL.md) | Run the component test suite against a specific component reference doc. |

## Adding a new skill

1. Create `.claude/skills/<skill-name>/SKILL.md` with at minimum a `name:` and `description:` in YAML front-matter.
2. Body is instructions to Claude — explain when to use it and the steps to follow.
3. If the skill should be invokable as a slash command, the folder name is the command name.
4. Add a row to the matching table above.
