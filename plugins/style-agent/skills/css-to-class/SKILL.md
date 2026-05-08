---
name: css-to-class
description: Extract a list of CSS utility classes from an HTML element or class string into a single named CSS class. Resolves each token to its actual declarations by grepping the project's own CSS files — no external processor, no framework assumption. Use when a developer wants to replace multi-class utility soup with a single semantic selector.
allowed-tools: Read, Glob, Grep, Bash, AskUserQuestion
---

# css-to-class

Convert a multi-class HTML element or plain class string into a single, semantically named CSS class. Resolves each utility token to its actual property/value declarations by grepping all `.css` files in the user's project — works with plain CSS, SCSS output, Tailwind, or any other utility-first workflow.

---

## Input forms

| Form | Example |
|---|---|
| HTML element | `<div class="testimonial flex-grid py-8 items-center" data-flex-grid>` |
| Plain class list | `testimonial flex-grid py-8 items-center` |
| Quoted string | `"flex py-4 items-center justify-between"` |

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
- If `name` is omitted: auto-generate via the algorithm below. When the result is ambiguous (all-utility list, or generated name is a single token under 4 chars), ask via `AskUserQuestion` with the generated name pre-filled as the suggestion rather than silently picking.

### Auto-name algorithm

1. Tokenise the class string on whitespace. Deduplicate (preserve order).
2. Partition tokens into **semantic** and **utility**:
   - **Utility prefixes** (classify as utility): `py-`, `px-`, `pt-`, `pb-`, `pl-`, `pr-`, `mt-`, `mb-`, `ml-`, `mr-`, `mx-`, `my-`, `m-`, `p-`, `gap-`, `text-`, `bg-`, `border-`, `rounded-`, `w-`, `h-`, `min-`, `max-`, `flex-`, `grid-`, `col-`, `row-`, `items-`, `justify-`, `self-`, `place-`, `order-`, `z-`, `opacity-`, `shadow-`, `ring-`, `sr-`, `not-sr-`.
   - Single well-known keywords with no hyphen (e.g. `flex`, `hidden`, `block`, `inline`) also count as **utility**.
   - Everything else is **semantic**.
3. Build the candidate name:
   - **Primary**: first semantic token. If none, first utility token stripped of any trailing `-N` numeric suffix.
   - **Secondary**: first remaining token (semantic preferred over utility) that adds distinct meaning. Skip if combining with primary exceeds 20 chars.
   - Join with `-`, lowercase. Collapse any double `-`. Strip leading/trailing `-`.
4. Truncate to 20 chars (hard limit). If result is empty or ≤ 1 char, use `custom-class` and warn.

---

## Workflow

1. **Parse input.** Accept a pasted HTML snippet or a bare class string (with or without surrounding quotes). Use a regex to extract the `class="…"` value when HTML is present. Tokenise and deduplicate.

2. **Determine the class name.** Apply the Name rules above. When auto-generating and the class list is all-utility or the generated name is ambiguous, use `AskUserQuestion` with the suggestion pre-filled.

3. **Discover CSS files.** Run:
   ```bash
   find . -name "*.css" -not -path "*/node_modules/*" -not -path "*/.git/*" -not -path "*/dist/*" -not -path "*/build/*"
   ```
   Collect the resulting file list. If no `.css` files are found, note this and all tokens will be unresolved.

4. **Resolve declarations.** For each class token, apply CSS identifier escaping rules to build its selector form before grepping:
   - Escape any character that is not a valid unquoted CSS identifier character: `:` → `\:`, `&` → `\&`, `.` → `\.`, `%` → `\%`, etc.
   - If the token starts with a digit, apply CSS hex escaping for that leading digit (the hex sequence requires a trailing space as its terminator). For example, `2xl:flex` becomes `\32 xl\:flex` in its selector form, where `\32` is the hex escape for `2` and the space terminates the escape sequence.
   This correctly handles Tailwind variant tokens (`hover:bg-red-500` → `.hover\:bg-red-500`) and breakpoint-prefixed tokens (`2xl:*` → `.\32 xl\:*`). Then grep the discovered files for a selector containing `.<escaped-token>` followed by any of: whitespace, `{`, `,`, or `:`. Extract the property/value declarations from the matching block.
   - A token is **resolved** if at least one CSS file contains a matching selector with declarations.
   - A token is **unresolved** if no match is found — it is a custom or semantic class defined elsewhere (or not yet written).

5. **Emit the CSS class block.** Output a single class with:
   - Resolved declarations inlined in source order (one property per line).
   - Resolved declarations that appear inside an at-rule (`@media`, `@supports`, `@layer`) in the source file must be emitted with their at-rule wrapper preserved as a nested block — do not strip the context, or the declarations will stop working at the intended breakpoint or feature query. Group multiple tokens that share the same at-rule condition into one nested block.
   - Each unresolved token as a `/* <token>: add declarations manually */` placeholder comment, preserving its relative position.

   Example for `<div class="testimonial flex-grid py-8 items-center">`:
   ```css
   /* extracted: testimonial flex-grid py-8 items-center */
   .testimonial-grid {
     /* testimonial: add declarations manually */
     /* flex-grid: add declarations manually */
     padding-block: 2rem;
     align-items: center;
   }
   ```

6. **Emit the refactored HTML.** Replace the full `class="…"` value with the new single class name. Preserve all other attributes unchanged (including `data-*`, `id`, `aria-*`).

7. **Print a summary:**
   - Original class count → 1, name chosen, whether it was provided or auto-generated
   - Resolved: N declarations inlined from project CSS files
   - Unresolved: list any tokens that need manual declarations
   - Any name truncation or kebab-case coercion warnings
