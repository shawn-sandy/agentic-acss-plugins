---
name: css-to-class
description: Extract a list of CSS utility classes from an HTML element or class string into a single named CSS class. Resolves each token to its actual declarations by reading the plugin's own assets — no external processor required. Use when a developer wants to replace multi-class utility soup with a single semantic selector.
allowed-tools: Read, Glob, Grep, AskUserQuestion
---

# css-to-class

Convert a multi-class HTML element or plain class string into a single, semantically named CSS class. Resolves each utility token to its actual property/value declarations by reading `${CLAUDE_PLUGIN_ROOT}/assets/utilities.css` and the per-family partials — no `@apply`, no external build tool.

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
- If `name` is supplied: convert spaces/underscores to `-`, lowercase, truncate to 20 chars. Warn the user if anything was changed.
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

3. **Resolve utility declarations.** For each class token:
   a. Read `${CLAUDE_PLUGIN_ROOT}/assets/utilities.css`. Grep for a selector block matching `.<token>` exactly (e.g. `.py-8 {`). Extract the property/value declarations from that block.
   b. If not found in the bundle, also check the per-family partials under `${CLAUDE_PLUGIN_ROOT}/assets/utilities/`.
   c. Tokens not found in either location are **unresolved** — they are custom or semantic classes defined elsewhere in the user's project.

4. **Emit the CSS class block.** Output a single class with:
   - Resolved declarations inlined in source order (one property per line).
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

5. **Emit the refactored HTML.** Replace the full `class="…"` value with the new single class name. Preserve all other attributes unchanged (including `data-*`, `id`, `aria-*`).

6. **Print a summary:**
   - Original class count → 1, name chosen, whether it was provided or auto-generated
   - Resolved: N declarations inlined from plugin assets
   - Unresolved: list any tokens that need manual declarations
   - Any name truncation or kebab-case coercion warnings

---

## References to load

- `references/utility-catalogue.md` — consult when a token lookup in the CSS files is ambiguous.
