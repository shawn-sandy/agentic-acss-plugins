---
status: todo
type: feature
created: 2026-05-14
---

# Plan: Add create-utilities skill to style-agent

## Context

`style-agent` already has two class-authoring skills: `css-to-class` (collapse a utility list into a named class) and `inline-style-to-class` (promote an inline style to a class). The missing direction is the entry point: a developer has a visual intent described in plain language ("a flex container with centered items and 1rem padding") but no class list yet. Today they must mentally map that intent to utility names by hand. A `create-utilities` skill fills that gap — natural language description → ready-to-use utility class string — and chains naturally into the existing `css-to-class` workflow when the user wants to consolidate.

## Objective

Add a `create-utilities` skill and matching `/create-utilities [description]` command to `plugins/style-agent/`. The skill accepts a plain-text visual description, detects which utility library the project uses (acss-kit, Tailwind, Bootstrap utilities, or Tailwind-compatible generic fallback), maps the description to specific class names via LLM reasoning, and outputs a class string plus a one-line HTML example. It stays single-purpose — named-class consolidation is delegated to `/css-to-class`.

## Steps

1. **Create `plugins/style-agent/skills/create-utilities/SKILL.md`** — *Why:* the skill file is the authoritative source of behavior; the command delegates to it entirely. Write with four sections: front-matter (`name`, `description`, `allowed-tools`), Input Forms table, Framework Detection workflow, and the core 6-step Workflow (see SKILL.md design below). *Verify:* `grep -c '^##' plugins/style-agent/skills/create-utilities/SKILL.md` returns 4+ section headings; front-matter `name:` and `description:` fields are present.

2. **Create `plugins/style-agent/commands/create-utilities.md`** — *Why:* every skill needs a matching command that delegates to it (plugin convention). Use `argument-hint: [description]` (not `[name]` — the skill takes a plain-language description, not a CSS identifier). Follow the existing command pattern: YAML front-matter with `description`, `argument-hint`, `allowed-tools`, then a one-paragraph body referencing `${CLAUDE_PLUGIN_ROOT}/skills/create-utilities/SKILL.md`. *Verify:* file contains `${CLAUDE_PLUGIN_ROOT}/skills/create-utilities/SKILL.md`, `argument-hint: [description]` is present, and the file has no logic beyond the delegation paragraph.

3. **Update `plugins/style-agent/docs/README.md`** — *Why:* maintainer guide must stay current. Add `/create-utilities [description]` row to the Commands table and `skills/create-utilities/SKILL.md` line to the Skills list. *Verify:* `grep create-utilities plugins/style-agent/docs/README.md` returns 2 matches.

4. **Update `plugins/style-agent/README.md`** — *Why:* user-facing docs must document the new command. Add a `### /create-utilities [description]` section after `inline-style-to-class`, with a one-line description, an input example, an output example (class string + HTML snippet), and a note that `/css-to-class` can consolidate the output into a named class. *Verify:* the new section heading is present and the output example shows both a class string and an HTML element.

5. **Update `plugins/style-agent/CHANGELOG.md`** — *Why:* Keep a Changelog convention. Add a `### Added` entry under `## [0.3.0]` (not `[Unreleased]` — we are bumping the version in the same changeset, so the two should be in sync): "`/create-utilities` — natural-language description to utility class string (new skill + command)". *Verify:* entry appears under `## [0.3.0]` heading and follows the existing entry style.

6. **Bump version in `plugins/style-agent/.claude-plugin/plugin.json`** from `0.2.0` to `0.3.0` — *Why:* adding a new command is a minor semver increment. *Verify:* `grep version plugins/style-agent/.claude-plugin/plugin.json` shows `"version": "0.3.0"`.

7. **Update `marketplace.json` description for `style-agent`** — *Why:* CLAUDE.md pre-submit checklist requires updating the marketplace entry description when a change is user-facing; adding a new command qualifies. Find the `style-agent` entry in `.claude-plugin/marketplace.json` and append the new capability to the description string. *Verify:* `grep create-utilities .claude-plugin/marketplace.json` (or the repo-root marketplace file) returns a match.

## SKILL.md design (detail for step 1)

### Front-matter
```yaml
---
name: create-utilities
description: Use when the developer wants to translate a plain-language visual description into utility classes — turning intent like "centered flex row with padding" into a ready-to-use class string.
allowed-tools: Read, Glob, Grep, Bash, AskUserQuestion
---
```

### Input forms table
| Form | Example |
|---|---|
| Plain description | `"a card with white background, 1rem padding, subtle shadow, and rounded corners"` |
| Component phrase | `"primary button with hover state"` |
| HTML element with intent | `<div> <!-- make this a centered hero section -->` |

### Framework detection (step 2 of workflow)
Grep project files to identify which utility library is active:
- **acss-kit** — presence of `utilities.css` containing `.bg-primary`, `.flex`, `.m-4` selectors
- **Tailwind** — `tailwind.config.*` file or `@tailwind base` in any `.css`/`.scss`
- **Bootstrap** — `bootstrap.css` or `bs-` prefixed classes present in source files
- **Generic fallback** — no framework detected; emit Tailwind-compatible class names (`flex`, `p-4`, `rounded`, etc.) — the de-facto standard most developers recognise

When multiple frameworks are detected, use `AskUserQuestion` to ask the user which vocabulary to use. Do not silently pick one.

### Core workflow (6 steps)

1. **Parse description.** Extract visual properties: layout, spacing, color, typography, borders, shadows, states. If the description is too vague to generate a confident class list (e.g., "make it look nice", "a styled button"), use `AskUserQuestion` with specific follow-up prompts — layout type? color role? spacing scale? — before proceeding.

2. **Detect framework.** Run framework detection above. If multiple frameworks are detected or none is found, use `AskUserQuestion` to confirm which vocabulary to use. If none is confirmed, fall back to Tailwind-compatible naming.

3. **Map tokens.** For each extracted visual property, use LLM reasoning to select the best class name from the detected framework's vocabulary. Order the final list: layout → spacing → color → typography → border/radius → shadow → state. If a description maps to multiple plausible scale values (e.g., "large padding" → `p-6`, `p-8`, or `p-10`?), use `AskUserQuestion` to confirm the intended value before emitting.

4. **Apply accessibility defaults.** If the description implies an interactive element (button, link, input, or similar), automatically include the appropriate focus-visible or focus-ring class even if not explicitly requested. Note any a11y additions with a brief inline comment so the user understands why they were included.

5. **Emit output.** Print two code blocks:
   - The class string: e.g. `` `flex items-center p-4 bg-primary rounded focus-visible:ring` ``
   - A one-line HTML example showing the class string applied: e.g. `<button class="flex items-center p-4 bg-primary rounded focus-visible:ring">Label</button>`

6. **Print summary.** List: description parsed → N classes generated, framework detected, any a11y classes added, any ambiguities resolved, any properties not mapped. If the description implied a foreground/background color pair that is likely to fail WCAG 4.5:1 contrast, flag it with a brief contrast warning. Close with: `Run /css-to-class [name] to consolidate into a named class.`

## Verification

After implementation:
1. Run `tests/run.sh` from repo root — must be green (structural validation).
2. Install locally: `claude --plugin-dir ./plugins/style-agent` and run `/create-utilities "a centered flex row with 1rem gap and primary background"` — should output a class string and HTML example in under one round-trip.
3. Test vague input: run `/create-utilities "make it look nice"` — should trigger `AskUserQuestion` asking for specifics before generating any output.
4. Test framework detection: run in a project with Tailwind vs. one with acss-kit utilities — confirm emitted class names match the correct vocabulary.
5. Test a11y defaults: run `/create-utilities "a primary submit button"` — output should include a focus-visible or focus-ring class.
6. Test multi-framework: run in a project with both Tailwind and acss-kit detected — should ask which vocabulary to use.
7. Confirm plugin version shows `0.3.0` via `/plugin list` and CHANGELOG shows `[0.3.0]`.

## Next Steps *(optional)*

- Wire `/create-utilities` output into `/css-to-class` in a single chained command:
  ```text
  Add a chained `/describe-and-name` command to style-agent that runs the create-utilities skill
  followed by the css-to-class skill in sequence — user provides a description and a name,
  gets back a named CSS class directly. The command lives at
  plugins/style-agent/commands/describe-and-name.md and should delegate to both SKILL.md
  files in order, passing the class string from create-utilities as input to css-to-class.
  ```

- Extend framework detection to read `vocab.json` when acss-kit utilities are installed, for an exact class inventory:
  ```text
  In plugins/style-agent/skills/create-utilities/SKILL.md, extend step 2 (Framework Detection)
  so that when acss-kit utilities are detected, the workflow also reads
  plugins/acss-kit/assets/utilities/vocab.json (or the project-installed copy at
  src/styles/utilities/vocab.json) to get the exact available class names before mapping.
  This prevents suggesting classes that aren't in the bundle. Update the skill's allowed-tools
  to include Read, and add a note in the workflow about the vocab.json lookup path.
  ```

## Interview Summary

Conducted 2026-05-14. File renamed from `i-m-going-to-create-cached-pond.md` to `add-create-utilities-skill-style-agent.md`.

### Key Decisions Confirmed

- **Mapping approach**: Pure LLM reasoning — no lookup tables or grep-based vocab validation; Claude infers class names from the detected framework's conventions.
- **Multi-framework conflict**: Use `AskUserQuestion` when multiple frameworks are detected (Tailwind + acss-kit) rather than silently picking one.
- **Step 6 removed**: `create-utilities` stays single-purpose (description → class list). The summary message tells the user to run `/css-to-class` to consolidate into a named class. The auto-name algorithm lives in `css-to-class` only — no duplication.
- **Generic fallback**: Tailwind-compatible naming when no framework is detected.
- **Vague input**: Use `AskUserQuestion` with specific follow-up prompts (layout type? color role? spacing scale?) rather than generating loose output.
- **Output format**: Both class string + one-line HTML example showing it applied.
- **A11y defaults**: For interactive elements (button, link, input), automatically include focus-visible/focus-ring classes with a note.
- **Contrast warnings**: Flag obvious low-contrast color pairs in the summary.

### Open Risks & Concerns

1. **`argument-hint` corrected** — was `[name]`, now `[description]`; fixed in this plan revision.
2. **CHANGELOG/version timing** — plan now writes `[0.3.0]` heading (not `[Unreleased]`) to stay in sync with the plugin.json bump in the same changeset.
3. **`marketplace.json` added** — new Step 7 covers the entry description update.
4. **No reproducible test fixture** — verification relies on live session invocation; structure tests pass but skill reasoning is untestable without a smoke-test fixture.

### Simplification Opportunities Applied

- Removed "suggest a name based on description" from the summary step — the auto-name algorithm already lives in `css-to-class/SKILL.md`; duplicating it here would create two places to maintain the same logic.
