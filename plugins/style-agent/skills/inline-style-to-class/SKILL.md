---
name: inline-style-to-class
description: Convert an inline style attribute, JSX style object, or <style> block into a single named CSS class and append it to the project stylesheet. Detects the target stylesheet from project file conventions — no external processor, no framework assumption. Use when migrating inline styles to reusable, maintainable CSS classes.
allowed-tools: Read, Glob, Grep, Bash, Write, Edit, AskUserQuestion
---

# inline-style-to-class

Convert an inline `style` attribute, JSX `style` object, or `<style>` block into a single, semantically named CSS class. Appends the result to a stylesheet detected from the project's own file conventions — works with plain CSS, SCSS, or Sass-indented syntax. The inverse operation of `/css-to-class`.

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
- If `name` is omitted: auto-generate via the algorithm below. When the result is ambiguous or a single token under 4 chars, ask via `AskUserQuestion` with the generated name pre-filled as the suggestion.

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
5. If the result is empty or ≤ 1 char, use `custom-class` and warn.

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

## Workflow

1. **Parse input.** Detect the form of the input:
   - **HTML inline attribute** — match `style="..."` or `style='...'`; split on `;`; trim; parse `property: value` pairs. Extract the surrounding element tag if present.
   - **JSX style object** — match `style={{...}}`; extract the object literal body; split key/value pairs. Convert each camelCase key to kebab-case (insert `-` before each uppercase letter, then lowercase the whole key). For numeric literal values, emit a coercion warning: "numeric value — verify unit". For any value that is a JS expression (not a string or number literal), emit a `/* unresolved: <expr> */` placeholder.
   - **`<style>` block** — extract content between `<style>` and `</style>`; parse rules. If one rule, use its declarations. If multiple rules, ask via `AskUserQuestion`: merge all declarations or pick a specific rule.

2. **Determine the class name.** Apply the Name rules above. Use the `[name]` argument if provided. Otherwise apply the auto-name algorithm. If the generated name is ambiguous or ≤ 3 chars, ask via `AskUserQuestion` with the suggestion pre-filled.

3. **Discover the target stylesheet.** Follow the Stylesheet discovery section. Confirm the chosen file with the user only when the choice is ambiguous.

4. **Build the CSS class block.** Emit using the detected syntax flavor and indentation:
   - Comment header: `/* from: <source summary — e.g. "style attr on <div>", "JSX style object", or "<style> block" */ `.
   - One property per line.
   - Unresolved JSX expressions: `/* <property>: unresolved — was JS expression */`.
   - Numeric values (no unit): preserve value and append `/* verify unit */` inline comment.
   - For Sass-indented (`.sass`) syntax, omit braces and use the detected indentation.

5. **Append to the target stylesheet.** Use `Edit` to append the class block, preceded by one blank line. Preserve any trailing newline the file already had.

6. **Emit refactored source.** Produce a clean version of the original input with the inline style removed:
   - **HTML** — remove the `style="..."` attribute entirely if all declarations migrated; if some were unresolved, keep only unmigrated declarations in the attribute. Add the new class to any existing `class` attribute (append to the list); if none exists, add `class="<name>"`. Preserve all other attributes unchanged (`data-*`, `id`, `aria-*`).
   - **JSX** — same logic using `className`. For partially-migrated objects, preserve remaining key/value pairs in the style prop.
   - **`<style>` block** — emit a comment noting the rule was extracted: `/* rule moved to .<name> in <stylesheet path> */`; do not rewrite the `<style>` block automatically.

7. **Print a summary:**
   - Class name chosen, whether it was provided or auto-generated, and any coercion warnings.
   - Target stylesheet path and confirmation that the class was appended (or a note if no file was found).
   - Number of declarations migrated.
   - Number of unresolved JS expressions (if any).
   - Numeric-value unit warnings (if any).
