# Add `/inline-style-to-class` skill to `style-agent` plugin

## Context

The `style-agent` plugin currently ships a single skill, `/css-to-class`, which extracts a list of utility class tokens from a `class` attribute into a single semantically-named CSS class. Authors working in the opposite direction — a codebase peppered with inline `style=""` attributes, JSX `style={{ ... }}` objects, or ad-hoc `<style>` blocks — have no symmetric tool to migrate those declarations into a reusable class. This plan adds `inline-style-to-class` as a sibling skill that converts inline style declarations into a named CSS class, **emits the result to chat, and appends it to a project stylesheet** detected from existing project conventions.

The skill mirrors `css-to-class`'s shape (single-file SKILL.md, no scripts, no references, delegating command) so maintenance stays uniform across the plugin.

## Objective

Ship a new sibling skill + command in `plugins/style-agent/`, named `inline-style-to-class`, that:

1. Accepts three input forms: inline HTML/JSX `style="..."` attributes, JSX `style={{ ... }}` objects, and `<style>...</style>` tag block contents.
2. Normalises declarations to kebab-case CSS, with no project-CSS discovery (declarations come from the input verbatim).
3. Emits the new CSS class block + refactored source to chat **and** appends the class block to a project stylesheet whose location and syntax (`.css` / `.scss` / Sass-indented) are auto-detected; asks if ambiguous.
4. Reuses the sibling's name rules (max 20 chars, kebab-case, sanitisation pipeline, `AskUserQuestion` fallback).

## Files to create

| Path | Purpose |
|---|---|
| `plugins/style-agent/skills/inline-style-to-class/SKILL.md` | All skill logic — front-matter + 7-step workflow. |
| `plugins/style-agent/commands/inline-style-to-class.md` | Thin delegating command body (3–6 lines). |

## Files to edit

| Path | Change |
|---|---|
| `plugins/style-agent/.claude-plugin/plugin.json` | Bump `version` (minor: feature addition). |
| `plugins/style-agent/CHANGELOG.md` | Add entry under `[Unreleased] → Added`. |
| `plugins/style-agent/README.md` | Add `### /inline-style-to-class [name]` block under `## Commands` with Input/Output examples and Name rules line. |
| `plugins/style-agent/docs/README.md` | Add row to the Commands table. |
| `.claude-plugin/marketplace.json` | Append `Run /inline-style-to-class to ...` to the `style-agent` entry's `description`; consider adding `inline-styles` to `tags`. |

No changes to `.claude/settings.json` hooks (existing PostToolUse validators cover the new files automatically).

## Steps

1. **Author `skills/inline-style-to-class/SKILL.md`** with front-matter mirroring the sibling, but with `allowed-tools: Read, Glob, Grep, Bash, Write, Edit, AskUserQuestion` (adds `Write, Edit` because this skill saves to a stylesheet — the sibling does not). Body uses 7 numbered workflow steps with bold-lead sentences, identical structure to `css-to-class/SKILL.md`. *Why:* Surface-symmetry across sibling skills makes the plugin easier to maintain and review.

2. **Define input parsing (Workflow step 1).** Three forms:
   - **HTML/JSX inline attribute** — match `style="..."` or `style='...'`; split on `;`, trim, parse `prop: value` pairs.
   - **JSX style object** — match `style={{ ... }}`; parse JS object literal; convert camelCase → kebab-case (e.g. `backgroundColor` → `background-color`); preserve string and numeric literals; flag any JS expression value as `/* unresolved: <expr> */`.
   - **`<style>` block contents** — parse rules; if one rule, take its declarations; if multiple rules, prompt with `AskUserQuestion` (merge all into one class, or pick one rule).

   *Why:* These three forms cover the realistic migration surface; raw CSS-property blocks were intentionally excluded by the user.

3. **Define name rules and auto-name algorithm (Workflow step 2).** Reuse the sibling's 20-char kebab-case constraint and 6-step sanitisation pipeline verbatim. Auto-name source differs (no class tokens to draw from) — derive from element tag plus a salient property:
   - `<div style="background: ...">` → `div-bg`
   - `<button style="padding: ...">` → `btn-pad` (well-known tag abbreviations)
   - JSX object on bare component → first declared property
   - Fallback: `AskUserQuestion` for the name; default `custom-class`.

   *Why:* Inline styles lack the semantic class-token signal `css-to-class` uses, so the auto-namer must lean on the element + first property; user can always override via the `[name]` argument.

4. **Define stylesheet discovery (Workflow step 3).** Glob common locations in priority order: `src/**/*.{css,scss,sass}`, `styles/**/*.{css,scss,sass}`, `app/**/*.{css,scss,sass}`, then repo-root `*.{css,scss,sass}`. Detect:
   - **Syntax flavor** from the file extension.
   - **Indentation** from the first non-empty rule body (count leading whitespace).
   - **Trailing newline** on the file.

   If a single candidate clearly dominates (e.g. one `globals.css`), use it. If multiple candidates of similar standing exist, prompt with `AskUserQuestion` to pick. *Why:* The user explicitly asked for "based on project patterns" — auto-detect first, ask only when ambiguous.

5. **Define CSS class block emission (Workflow step 4).** Mirror the sibling's output shape:
   - Comment header: `/* extracted-from: <element snippet or "style block"> */`
   - Properties one per line, kebab-case, preserve units and `var(...)` references verbatim.
   - Unresolved JSX expressions become `/* <camelCase>: add value manually — was JSX expression */` placeholders.
   - For Sass-indented syntax, emit without braces and with the detected indent.

6. **Define stylesheet append (Workflow step 5).** Use `Edit` to append the new class block to the chosen stylesheet — preserve any trailing newline, use the detected indentation, separate from prior content with one blank line. *Why:* `Edit`-based append preserves byte-exact existing content; `Write` would risk overwriting.

7. **Define refactored source emission (Workflow step 6).** Strip the migrated declarations from the source:
   - Inline `style="..."` → remove the attribute entirely if all declarations migrated; otherwise keep only the unmigrated subset.
   - JSX `style={{ ... }}` → same logic, JS-side.
   - `<style>` block → emit a note that the rule was moved; do not auto-rewrite the block (out of scope).
   - Add the new class to the existing `class` / `className` attribute (don't overwrite). Preserve all other attributes (`data-*`, `id`, `aria-*`, etc.) — same preservation rule as the sibling.

8. **Define summary output (Workflow step 7).** Print: chosen name, target stylesheet path, declarations migrated count, unresolved-expression count, any coercion warnings (camelCase→kebab; numeric values preserved with `/* verify unit */` comment rather than auto-appending a unit). Match the sibling's summary format.

9. **Author `commands/inline-style-to-class.md`** — 4-line delegating body identical in shape to `commands/css-to-class.md`:
   ```yaml
   description: Convert an inline style attribute, JSX style object, or <style> block into a named CSS class and append it to the project stylesheet
   argument-hint: [name]
   allowed-tools: Read, Glob, Grep, Bash, Write, Edit, AskUserQuestion
   ```
   Body: one-sentence purpose, then `Follow ${CLAUDE_PLUGIN_ROOT}/skills/inline-style-to-class/SKILL.md.`, then the standard delegation line.

10. **Bump `plugin.json` version** — minor bump (feature addition; no breaking change). Confirm `marketplace.json` entry has no `version` field per repo convention.

11. **Update CHANGELOG, README, docs/README, marketplace description** in a single pass per the sibling's existing patterns (entries already documented in the briefing). Append `Run /inline-style-to-class to migrate inline styles into named classes.` to the marketplace description.

## Critical files to read before implementing

- `plugins/style-agent/skills/css-to-class/SKILL.md` — copy 7-step structure, name rules, sanitisation pipeline.
- `plugins/style-agent/commands/css-to-class.md` — copy delegating command body shape.
- `plugins/style-agent/README.md` — copy command-section formatting.
- `plugins/style-agent/docs/README.md` — copy Commands-table row formatting.
- `.claude-plugin/marketplace.json` — `style-agent` entry to amend.
- `.claude/rules/command-authoring.md` — confirm front-matter requirements.

## Verification

1. **Structural validation** — run `tests/run.sh` from repo root; PostToolUse hooks will additionally validate front-matter on every Write/Edit during authoring.
2. **Manifest sanity** — `cat plugins/style-agent/.claude-plugin/plugin.json | python3 -m json.tool` and `cat .claude-plugin/marketplace.json | python3 -m json.tool` to confirm valid JSON.
3. **Local install smoke test** — `claude --plugin-dir ./plugins/style-agent` from repo root; confirm `/inline-style-to-class` appears in the slash-command list and its help text matches the command's `description`.
4. **End-to-end fixture** — in a scratch directory:
   - Run `/inline-style-to-class hero-bg` against `<div style="background: var(--surface-1); padding: 1rem">Hi</div>` with a `styles/globals.css` present; confirm:
     - Class `.hero-bg { background: var(--surface-1); padding: 1rem; }` appended to `styles/globals.css`.
     - Refactored output: `<div class="hero-bg">Hi</div>`.
     - Summary lists 2 declarations migrated, 0 unresolved.
   - Repeat with a JSX object: `<Button style={{ backgroundColor: theme.primary, padding: 8 }}>` — confirm `backgroundColor` → `background-color`, `8` preserved with `/* verify unit */` comment, `theme.primary` → unresolved placeholder.
   - Repeat with a `<style>` block containing two rules — confirm `AskUserQuestion` prompts for merge-vs-pick.
5. **Multi-stylesheet ambiguity** — fixture with both `src/styles/main.scss` and `styles/globals.css`; confirm `AskUserQuestion` prompts to pick.
6. **Sibling regression** — run `/css-to-class card-base` against a known fixture; confirm unchanged behavior.

## Out of scope (Next Steps)

- Auto-rewriting `<style>` block contents in place (step 7 only emits a note).
- Coupling to `acss-kit` design tokens (would break framework-agnostic premise — explicitly rejected upstream).
- A reverse `/class-to-style` (re-inlining a class) — unlikely to be useful but listed for completeness.
- Python helper script for parsing — not needed; current SKILL.md tooling (Read/Grep/Bash) is sufficient and the sibling has no script either.

## Unresolved Questions

None — user answered all four design questions; no open items.
