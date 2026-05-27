---
name: inline-style-to-class
description: Use when the developer wants to convert an inline style attribute, JSX style object, or <style> block into a named CSS class appended to the project stylesheet. Replaces hard-coded colors, units, and values with CSS variables — reusing an existing variable when one matches and creating a new one when none does.
allowed-tools: Read, Glob, Grep, Bash, Write, Edit, AskUserQuestion
---

# inline-style-to-class

Convert an inline `style` attribute, JSX `style` object, or `<style>` block into a single, semantically named CSS class. Appends the result to a stylesheet detected from the project's own file conventions — works with plain CSS, SCSS, or Sass-indented syntax. The inverse operation of `/css-to-class`.

Every concrete value in the migrated declarations is replaced with a CSS variable: if a custom property in the project already holds that value, the class references it; otherwise a new variable is created and declared. The original literal is always kept as the `var()` fallback, so the class renders even when the variable is absent.

---

## Input forms

| Form | Example |
|---|---|
| HTML inline attribute | `<div style="background: var(--surface-1); padding: 1rem">` |
| JSX style object | `<Button style={{ backgroundColor: theme.primary, padding: 8 }}>` |
| `<style>` block | `<style>.hero { color: red; padding: 2rem; }</style>` |

---

## Name rules

- Max **20 characters**, **kebab-case** only (`[a-z][a-z0-9-]*`).
- If `name` is supplied, apply this sanitisation pipeline in order:
  1. Lowercase.
  2. Replace spaces and underscores with `-`.
  3. Strip any character not in `[a-z0-9-]`.
  4. Strip leading hyphens and leading digits until the name starts with `[a-z]`.
  5. Strip trailing hyphens. Collapse consecutive hyphens to one.
  6. Truncate to 20 chars.
  If the result is empty after step 6, ask via `AskUserQuestion` for a valid name instead of emitting an invalid identifier. Warn the user whenever any coercion occurred.
- If `name` is omitted: auto-generate via the algorithm below. When the result is ambiguous or ≤ 3 chars, ask via `AskUserQuestion` with the generated name pre-filled as the suggestion.

### Auto-name algorithm

1. If an element tag is present, derive an abbreviation: `button` → `btn`, `section` → `section`, `header` → `header`, `nav` → `nav`, `ul`/`li` → `list`, `input` → `input`, `img` → `img`, `a` → `link`. All other tags use the tag name verbatim (e.g. `div` → `div`).
2. From the first declaration in the style source, extract a role hint from the property name:
   - `background` / `background-color` / `color` → `bg`
   - `padding` / `padding-*` → `pad`
   - `margin` / `margin-*` → `gap`
   - `font-size` / `font-weight` / `font-*` → `type`
   - `display` / `flex` / `grid` → `layout`
   - `border` / `border-*` → `border`
   - `width` / `height` / `min-*` / `max-*` → `size`
   - `position` / `top` / `left` / `z-index` → `pos`
   - Any other property — skip the role hint.
3. Join with `-`: `<tag-abbrev>-<role>`, e.g. `div-bg`, `btn-pad`. If no tag is available, use the role hint alone.
4. Truncate to 20 chars. Collapse double `-`. Strip leading/trailing `-`.
5. If the result is empty, use `custom-class` and warn. If the result is 1–3 chars, ask via `AskUserQuestion` with the suggestion pre-filled.

---

## Stylesheet discovery

1. Glob for stylesheets in priority order, excluding `**/node_modules/**`, `**/.git/**`, `**/dist/**`, `**/build/**`:
   - `src/**/*.{css,scss,sass}`
   - `styles/**/*.{css,scss,sass}`
   - `app/**/*.{css,scss,sass}`
   - `*.{css,scss,sass}` (repo root)
2. From the matching files, detect:
   - **Syntax flavor** — by extension (`.css`, `.scss`, `.sass`).
   - **Indentation** — read the first non-empty rule body; count leading whitespace characters.
   - **Trailing newline** — note whether the file ends with `\n`.
3. Selection: if exactly one candidate exists, use it. If multiple candidates exist and one is a clear entry file (named `globals`, `main`, `index`, `styles`, `app`, or `base`), use that one. Otherwise prompt with `AskUserQuestion` to pick.
4. If no stylesheet is found, emit the CSS block to chat only and note that no target file was detected; invite the user to paste it manually.

---

## Variable discovery

Run this alongside Stylesheet discovery so the class can be tokenized.

1. **Collect existing variables.** Across the same glob set (same excludes), grep every custom-property declaration with `^\s*(--[a-z0-9-]+)\s*:\s*([^;]+);`. Build a **reverse map** of *normalised value → variable name* (see normalisation under Value tokenizing rules). This map drives reuse — when a migrated value matches, reference the existing variable instead of creating one.
2. **Detect the naming convention per value category.** Inspect the discovered names to infer the project's prefix for each category — e.g. colors as `--color-*` vs `--clr-*` vs `--c-*`; spacing as `--space-*` vs `--spacing-*` vs `--size-*`. Use the detected prefix when creating new variables of that category. If a category has no precedent, fall back to the default semantic prefix listed below.
3. **Locate the declaration target** for new variables, in priority order:
   - A dedicated tokens/variables file already in the project: `tokens.{css,scss,sass}`, `variables.{css,scss,sass}`, or `_variables.{scss,sass}`.
   - An existing `:root { }` block (in any discovered stylesheet, preferring an entry file named `globals`, `main`, `index`, `styles`, `app`, or `base`).
   - Otherwise: the target stylesheet chosen in Stylesheet discovery — a new `:root { }` block will be created at the top of it.
   Remember this target for the "Declare new variables" workflow step.

---

## Value tokenizing rules

Every concrete value is replaced with a variable. Reuse always wins over creation.

1. **Classify the value:**
   - **color** — `#hex` (3 or 6 digit, matched by `#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})`), `rgb()`/`rgba()`, `hsl()`/`hsla()`, or a named color (`red`, `white`, …).
   - **length / dimension** — a number with a unit (`px`, `rem`, `em`, `%`, `vh`, `vw`, `ch`, …).
   - **radius / font-size / shadow / z-index** — recognised from the property name (`border-radius`, `font-size`, `box-shadow`, `z-index`).
   - **keyword** — a bare identifier such as `flex`, `block`, `none`, `auto`, `center`.
   - **other** — anything else concrete (e.g. multi-value shorthands); tokenize the whole value as one unit.
2. **Normalise for matching:** lowercase the value; expand 3-digit hex to 6-digit; collapse internal whitespace to single spaces. Matching is **exact on the normalised form only** — values are never converted across color formats (no hex↔rgb↔hsl) and units are never converted (`16px` ≠ `1rem`). Note this limitation in the summary when relevant.
3. **Skip (do not tokenize):**
   - Values that are already a `var(...)` reference (matched by `var\(\s*(--[a-z0-9-]+)\s*(?:,\s*([^)]+))?\)`) — pass through unchanged.
   - Unresolved JSX expressions — keep the existing `/* unresolved */` placeholder behavior.
4. **Dedupe within a run:** the same normalised value resolves to one variable. A variable created earlier in the same run is reused for later occurrences rather than created twice.

### Naming new variables

When no existing variable matches, create one:

1. Use the project's detected prefix for the value's category (from Variable discovery step 2).
2. If there is no precedent, use the default semantic template for the category:
   - color → `--color-1`, `--color-2`, … (or a descriptive `--color-<role>` when the property implies one)
   - length / spacing → `--space-*`
   - size (`width`/`height`/`min-*`/`max-*`) → `--size-*`
   - radius → `--radius-*`
   - font-size → `--font-size-*` (or `--text-*` if that prefix is already used)
   - shadow → `--shadow-*`
   - z-index → `--z-*`
   - keyword → `--<property>-<value>` (e.g. `display: flex` → `--display-flex`)
3. **Sanitise** the candidate to a valid custom-property identifier: lowercase, replace `.` and spaces with `-`, strip any character not in `[a-z0-9-]`, collapse consecutive hyphens (e.g. `1.5rem` → `space-1-5rem`).
4. **Collision handling:** if the name already exists with a *different* value, append `-2`, `-3`, … until unique.

---

## Workflow

1. **Parse input.** Detect the form of the input:
   - **HTML inline attribute** — match `style="..."` or `style='...'`; split on `;`; trim; parse `property: value` pairs. Extract the surrounding element tag if present.
   - **JSX style object** — match `style={{...}}`; extract the object literal body; split key/value pairs. Convert each camelCase key to kebab-case (insert `-` before each uppercase letter, then lowercase the whole key). For numeric literal values, emit a coercion warning: "numeric value — verify unit". For any value that is a JS expression (not a string or number literal), emit a `/* unresolved: <expr> */` placeholder.
   - **`<style>` block** — extract content between `<style>` and `</style>`; parse rules. If one rule, use its declarations. If multiple rules, ask via `AskUserQuestion`: merge all declarations or pick a specific rule.

2. **Determine the class name.** Apply the Name rules above. Use the `[name]` argument if provided. Otherwise apply the auto-name algorithm. If the generated name is ambiguous or ≤ 3 chars, ask via `AskUserQuestion` with the suggestion pre-filled.

3. **Discover the target stylesheet and existing variables.** Follow the Stylesheet discovery and Variable discovery sections. Confirm the chosen file with the user only when the choice is ambiguous.

4. **Build the CSS class block.** Emit using the detected syntax flavor and indentation:
   - Comment header: `/* from: <source summary — e.g. "style attr on <div>", "JSX style object", or "<style> block" */`.
   - One property per line.
   - **Tokenize every value** via the Value tokenizing rules: reuse a matching existing variable or create a new one, then emit `property: var(--name, <original-literal>);` with the original literal kept as the fallback. Skip values that are already `var(...)` references and unresolved expressions.
   - Unresolved JSX expressions: `/* <property>: unresolved — was JS expression */`.
   - Numeric values (no unit): still tokenize, but append a `/* verify unit */` inline comment after the declaration.
   - For Sass-indented (`.sass`) syntax, omit braces and use the detected indentation.

5. **Declare new variables.** For each variable created in step 4, write its `--name: value;` declaration to the target located in Variable discovery step 3 (a tokens/variables file, an existing `:root` block, or — if none exists — a new `:root { }` block inserted at the top of the target stylesheet). Match the file's detected syntax flavor, indentation, and trailing-newline convention; for `.sass`, omit braces. Reused (already-existing) variables are not re-declared.

6. **Append to the target stylesheet.** Use `Edit` to append the class block, preceded by one blank line. Preserve any trailing newline the file already had.

7. **Emit refactored source.** Produce a clean version of the original input with the inline style removed:
   - **HTML** — remove the `style="..."` attribute entirely if all declarations migrated; if some were unresolved, keep only unmigrated declarations in the attribute. Add the new class to any existing `class` attribute (append to the list); if none exists, add `class="<name>"`. Preserve all other attributes unchanged (`data-*`, `id`, `aria-*`).
   - **JSX** — same logic using `className`. For partially-migrated objects, preserve remaining key/value pairs in the style prop.
   - **`<style>` block** — emit a comment noting the rule was extracted: `/* rule moved to .<name> in <stylesheet path> */`; do not rewrite the `<style>` block automatically.

8. **Print a summary:**
   - Class name chosen, whether it was provided or auto-generated, and any coercion warnings.
   - Target stylesheet path and confirmation that the class was appended (or a note if no file was found).
   - Number of declarations migrated.
   - Variables reused: each `value → --name` that matched an existing variable.
   - Variables created: each `--name: value` and the file it was declared in.
   - Number of unresolved JS expressions (if any).
   - Numeric-value unit warnings (if any).
