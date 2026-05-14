---
name: create-utilities
description: Use when the developer wants to create utility classes from a plain-language visual description — turning intent like "centered flex row with padding" into a ready-to-use class string.
allowed-tools: Read, Glob, Grep, Bash, AskUserQuestion
---

# create-utilities

Generate a utility class string from a plain-language description of visual intent. Detects which utility library the project uses (acss-kit, Tailwind, Bootstrap, or Tailwind-compatible fallback) and maps the description to specific class names via LLM reasoning. Outputs a class string and a one-line HTML example ready to use — chains naturally into `/css-to-class` when the user wants to consolidate into a named class.

---

## Input forms

| Form | Example |
|---|---|
| Plain description | `"a card with white background, 1rem padding, subtle shadow, and rounded corners"` |
| Component phrase | `"primary button with hover state"` |
| HTML element with intent | `<div> <!-- make this a centered hero section -->` |

---

## Framework detection

Grep project files to identify which utility library is active:

- **acss-kit** — `utilities.css` present in the project containing selectors like `.bg-primary`, `.flex`, `.m-4`
- **Tailwind** — `tailwind.config.*` file exists, or `@tailwind base` appears in any `.css`/`.scss` file
- **Bootstrap** — `bootstrap.css` present, or `bs-` prefixed classes appear in source files
- **Generic fallback** — no framework detected; use Tailwind-compatible naming (`flex`, `p-4`, `rounded`, etc.) — the de-facto standard most developers recognise

When multiple frameworks are detected, use `AskUserQuestion` to confirm which vocabulary to use — never silently pick one.

---

## Workflow

1. **Parse description.** Extract the visual properties being described: layout, spacing, color, typography, borders, shadows, states. If the description is too vague to generate a confident class list (e.g., "make it look nice", "a styled button"), use `AskUserQuestion` with specific follow-up prompts before proceeding:
   - What layout type? (flex / grid / block)
   - What color role? (primary / neutral / danger / etc.)
   - What spacing scale? (small / medium / large, or a specific value)

2. **Detect framework.** Run the framework detection above:
   ```bash
   find . \( -name "utilities.css" -o -name "tailwind.config.*" -o -name "bootstrap.css" \) \
     -not -path "*/node_modules/*" -not -path "*/.git/*" -not -path "*/dist/*" -not -path "*/build/*"
   ```
   Also grep for `@tailwind base` in `.css`/`.scss` files. If multiple frameworks are found, or if the user confirms no framework, fall back to Tailwind-compatible naming.

3. **Map to classes.** For each extracted visual property, use LLM reasoning to select the best class name from the detected framework's vocabulary. Apply framework-specific naming conventions:
   - **acss-kit**: `.bg-primary`, `.p-4`, `.flex`, `.items-center`, `.rounded`, `.shadow`
   - **Tailwind**: `bg-primary`, `p-4`, `flex`, `items-center`, `rounded`, `shadow`
   - **Bootstrap**: `bg-primary`, `p-3`, `d-flex`, `align-items-center`, `rounded`, `shadow-sm`
   - **Fallback**: Tailwind-compatible names

   Order the final class list: **layout → spacing → color → typography → border/radius → shadow → state**.

   When a description maps to multiple plausible scale values (e.g., "large padding" → `p-6`, `p-8`, or `p-10`?), use `AskUserQuestion` to confirm the intended value before emitting.

4. **Apply accessibility defaults.** If the description implies an interactive element (button, link, input, select, or similar), automatically include the appropriate focus-visible or focus-ring class even if not explicitly mentioned. Append it to the state position in the class list and add a brief `# a11y` comment in the summary to explain the addition.

5. **Emit output.** Print two fenced code blocks:

   **Class string:**
   ```
   flex items-center p-4 bg-primary rounded shadow focus-visible:ring
   ```

   **HTML example** (one line, showing the class applied to the most appropriate element for the description):
   ```html
   <button class="flex items-center p-4 bg-primary rounded shadow focus-visible:ring">Label</button>
   ```

6. **Print summary.** One concise block listing:
   - Framework detected (or fallback used)
   - Number of classes generated
   - Any a11y classes added (with brief reason)
   - Any ambiguities resolved via `AskUserQuestion`
   - Any described properties that could not be mapped to a class (listed as unmapped)
   - If the description implies a foreground/background color pair likely to fail WCAG 4.5:1 contrast, flag it with a one-line contrast warning

   Close with: `Run /css-to-class [name] to consolidate into a named class.`
