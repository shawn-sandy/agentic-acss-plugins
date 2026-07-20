---
name: css
description: Use when the developer wants to author CSS from a plain-language description — emits a raw CSS/SCSS rule or an inline style attribute, reusing the project's own custom properties. For a utility-class string instead, use create-utilities.
allowed-tools: Read, Glob, Grep, Bash, Edit, Write, AskUserQuestion
---

# css

Turn a plain-language description of visual intent into a raw CSS/SCSS rule or an inline `style` attribute. Values are mapped onto the project's existing CSS custom properties when they match, and modern-CSS features with known footguns (`@container`, `@layer`, fluid `clamp()`, state selectors) are emitted from the bundled references rather than from memory.

This skill **authors** CSS. The sibling skills transform it: `/css-to-class` collapses utility soup into a named class, `/inline-style-to-class` promotes an existing inline style into one, and `/create-utilities` emits a utility-class string for projects that use a utility framework.

---

## Input forms

| Form | Example |
|---|---|
| Plain description | `"a flex row aligned centered with a small gap"` |
| Description with mode | `/css inline "a red 1rem-padded box"` |
| Description with target | `"a card with a soft shadow — put it in src/styles/main.css"` |
| Element with intent | `<button> <!-- primary button with a hover state -->` |

---

## Workflow

Stages run in this order. Nothing is emitted until the clarification gate resolves.

1. **Clarify** — run the clarification gate below. Batch every triggered question into one `AskUserQuestion` call. When no trigger fires, skip this stage entirely.
2. **Parse description** — extract the concrete properties being described: layout, spacing, colour, typography, borders, shadows, states, adaptive behaviour, and the element the rule is for.
3. **Detect output mode** — apply the output-mode branch below (class mode by default, inline mode on request).
4. **Resolve tokens** — apply the three-tier token resolution below against the project's own custom properties.
5. **Focus-visible** — apply the focus-visible step below for interactive elements.
6. **Consult references** — load any bundled reference whose topic the parsed intent touches (see References).
7. **Emit** — print the rule (or the inline attribute), and append to a stylesheet only under the conditions in the output-mode branch.
8. **Summarise** — print the summary spec below.
9. **Offer refinements** — close with two or three concrete next moves, per Refinement offer below.

---

## Clarification gate

Runs **before anything is emitted**. Every triggered question goes into a **single batched `AskUserQuestion` call** — never a second interrogation round. A concrete, fully-specified description **skips the gate entirely** and is emitted with no questions asked.

Four triggers:

- **(a) Unmappable description.** The description cannot be mapped to concrete properties with confidence — e.g. `"make it look nice"`, `"a styled button"`. Ask what layout, what colour role, what spacing scale.
- **(b) Scale tie.** A relative size word maps equally well to two adjacent steps of the project's scale — `"small"` could be `--space-2` or `--space-3`. Ask which step; never coin-flip a design system.
- **(c) Interactive element with unspecified states.** The description implies an interactive element but does not say which states it wants. Ask **which of `hover`, `focus`, `active`, and `disabled`** to emit. **When the description already names its states** (`"a button with a hover state"`), **emit exactly those and ask nothing.**
- **(d) Adaptive sizing with no stated basis.** The description implies adaptive sizing without saying what it adapts to. Ask whether it should respond to **its container or the viewport**, since that routes to `@container` versus `@media`. **When the description already says** (`"adapts to its container"`, `"stacks below 768px"`), **take it at its word** and do not ask.

When no trigger fires, emit directly — a well-specified request must not be interrogated. Nothing is emitted until the answers resolve.

---

## Output-mode branch

### Class mode (default)

- **Print by default.** The rule is printed to chat. It is appended to a stylesheet **only when the user names a target file.**
- **Confirm before any append.** Before writing, explicitly confirm **the resolved target path and the class name** with the user — appending mutates a file in their project.
- **Class name is proposed, not asked.** Derive it from the description (kebab-case, max 20 chars, matching the sibling skills' name rules) and **name the proposal in the summary**, so a bad guess costs one follow-up rather than a question up front.
- **Collision rule** (reused from `inline-style-to-class`): on a **same-name-different-value** clash, append a numeric suffix `-2`, `-3`, … until unique, and **report the suffixing in the summary**.
- **SCSS vs plain CSS is inferred** from the project's stylesheet extensions — glob for `**/*.{css,scss}` (excluding `node_modules`, `.git`, `dist`, `build`) and match the dominant flavour. **No stylesheet at all means plain CSS.**
- **`.sass` (indented syntax) is never an append target.** This skill emits brace-and-semicolon blocks, which are invalid in indented Sass. Exclude `.sass` from the inference glob; if the user names a `.sass` file as the target, refuse the append with a one-line reason and print the rule instead.

### Inline mode

Fires when the user says `inline` or points at an element.

**Refuse inline mode**, with a **one-line reason**, and **fall back to class mode**, when the description implies any of:

1. `:hover`
2. `:focus-visible`
3. `@media`
4. `@container`
5. `@layer`
6. `@supports`
7. a pseudo-element (`::before`, `::after`, …)

An inline `style` attribute cannot carry any of these, and a dropped state is lost without an error.

---

## Focus-visible

Sits between token resolution and emit.

- When the parsed description implies an **interactive element — button, link, input, select, or a custom widget** — emit a `:focus-visible` rule alongside the requested styling.
- When the output mode **cannot carry a state** (inline mode), **warn about its absence in the summary**.

Parity with `create-utilities` Step 4: without it, a generated button rule ships with no focus indicator and fails WCAG 2.4.7.

---

## Token resolution

Grep the project for custom-property declarations (`^\s*(--[A-Za-z0-9_-]+)\s*:\s*([^;\n]+);?`) across the same glob set, and **read the whole scale before mapping a relative word like "small"** — `"small"` is a position in a scale, not a value.

Three tiers:

1. **Exact-value match** — a custom property already holds the resolved value: use the variable.
2. **Semantic-name match** — no exact value, but a property's name matches the described role (e.g. `--space-2` for a small gap): use it and **name the choice in the summary**.
3. **No match** — emit the literal value.

**Never create a new custom property unless the user explicitly asks for one.** This **deliberately inverts `inline-style-to-class`**, which creates variables freely because there the value is already committed to the user's markup; here the request is authoring from scratch and inventing tokens would write into someone's design system on a throwaway request.

---

## References

Loaded by **model judgment when the parsed intent touches their topic** — **not** via a keyword trigger table, since no keyword table anticipates every phrasing. The summary must name which of these were consulted.

| Reference | Covers |
|---|---|
| `${CLAUDE_PLUGIN_ROOT}/skills/css/references/container-queries.md` | `container-type` on the parent, a container cannot query itself, `cqi`/`cqb` units, `container-name`. |
| `${CLAUDE_PLUGIN_ROOT}/skills/css/references/cascade-layers.md` | Unlayered styles outrank layered ones, `@layer` order declared first, third-party CSS, `!important` inversion. |
| `${CLAUDE_PLUGIN_ROOT}/skills/css/references/responsive-text.md` | `clamp()` with a rem addend, pure-vw failing WCAG 1.4.4 at 200% zoom, slope formula, `text-wrap`. |
| `${CLAUDE_PLUGIN_ROOT}/skills/css/references/progressive-enhancement.md` | `@supports` detecting upward rather than not-detection cascading down, `prefers-reduced-motion`, `prefers-contrast`. |
| `${CLAUDE_PLUGIN_ROOT}/skills/css/references/logical-properties.md` | `inline-size`, `block-size`, `margin-inline`, `padding-block`, `inset`, writing-mode rationale. |
| `${CLAUDE_PLUGIN_ROOT}/skills/css/references/modern-selectors.md` | `:has()` restrictions, `:is()`/`:where()`/`:not()` specificity, `:nth-child(An+B of S)`, native nesting vs SCSS `&`. |
| `${CLAUDE_PLUGIN_ROOT}/skills/css/references/state-selectors.md` | `:user-invalid` over `:invalid`, `[aria-disabled="true"]` over `:disabled`, `:focus-visible` rationale, `:empty`, `:placeholder-shown`. |
| `${CLAUDE_PLUGIN_ROOT}/skills/css/references/viewport-units.md` | `dvh`/`svh`/`lvh` versus `vh` under mobile browser chrome, `100vw` overflow with a scrollbar. |

---

## Summary spec

Print one concise block containing:

- **Output mode** — class (printed, or appended to `<path>`) or inline, plus the one-line reason if inline mode was refused.
- **Class name proposed** — the name derived from the description, and any `-2`/`-3` collision suffix that was applied.
- **Tokens resolved** — each `value → var(--name)` reuse, naming any tier-2 semantic-name choice explicitly, and any literal emitted because nothing matched. State that no new custom property was created.
- **Accessibility** — the `:focus-visible` rule emitted, or a warning that the mode cannot carry one.
- **References consulted** — **name every reference file that was loaded, or state that none were.** This is required on every result: it is the visible failure signal when a footgun doc was silently skipped.
- **Clarifications resolved** — any answers taken from the batched gate.

---

## Refinement offer

Every result closes with **two or three concrete next moves drawn from what was actually emitted** — the answer is already delivered, so the offer costs the user nothing. Draw from what the rule contains, for example:

- `Tighten the gap to var(--space-1)?`
- `Add a hover state?`
- `Switch to an inline style attribute?`
- `Promote it to a named class in your stylesheet — run /inline-style-to-class.`

Never offer a move the emitted rule does not support (e.g. do not offer to switch to inline when inline mode was refused).
