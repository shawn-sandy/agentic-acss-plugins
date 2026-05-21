---
paths:
  - "plugins/*/skills/**/SKILL.md"
---

# SKILL.md Front-Matter Conventions

Two tiers of plugin skills, with different front-matter expectations:

## Component-tier skills (`plugins/*/skills/component-*/SKILL.md`)

- Must set `disable-model-invocation: true` — keeps the catalog out of the
  model's initial context. Dispatch is by exact path/name from the
  orchestrator (kit-core's lookup table, `/kit-add <name>`,
  `/kit-list` globbing `component-*/`), not by description matching, so
  hiding the description does not break routing.
- Must declare a `hint:` field describing how the user (or Claude) should
  invoke the skill once it is hidden from auto-context. Convention:
  ```yaml
  hint: >-
    Invoke explicitly via `/kit-add <name>`, `/kit-create` (then ask for
    a <component>), or call the `component-<name>` skill by name.
    Describe <component-specific details: variant, size, state, slots>.
  ```
- `hint:` is a project-controlled convention. The Claude Code harness
  silently ignores unknown front-matter keys, but tooling in this repo
  (`/kit-list`, docs generation) can surface it.

## Orchestrator-tier and cross-cutting skills (entry points)

`kit-core`, `styles`, `utilities`, `setup`, `style-tune`, `kit-sync`,
`prompt-book`, and any future entry-point skill:

- Leave `disable-model-invocation` unset (defaults to `false`) — these
  are the discoverable entry points that should appear in initial context.
- No `hint:` required.

## Validation

The PostToolUse front-matter hook in `.claude/settings.json` only checks
for presence of `name:` and `description:`. The `disable-model-invocation`
and `hint:` fields are convention-enforced via this rule, not by the hook.
