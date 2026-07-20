---
status: todo
type: feature
created: 2026-07-19
issue: https://github.com/shawn-sandy/agentic-acss-plugins/issues/107
glance: style-agent can transform styles but cannot author them from plain language, and the modern-CSS features developers most want (@container, @layer, fluid type) carry footguns models get wrong from memory. Done means /css turns a description into a correct rule that reuses the project's own CSS variables, and a build-time validator proves every reference snippet parses.
---

# Plan: Add a /css authoring skill to style-agent

## Objective

Add a single `css` skill to `plugins/style-agent` that turns a plain-language description into a CSS/SCSS rule or inline `style` attribute, reusing the project's existing custom properties when they match, backed by bundled references for modern-CSS features with known footguns.

## Context

`style-agent` ships three skills that all transform existing styles: `css-to-class` (utility soup to named class), `inline-style-to-class` (inline to named class), and `create-utilities` (description to utility class string). Nothing authors raw CSS from a description — `create-utilities` only helps projects that already use a utility framework.

The modern CSS features developers most want help with — `@container`, `@layer`, `clamp()` fluid type, `@supports`, logical properties — carry specific footguns reproduced wrongly from memory: unlayered styles beating layered ones, a missing `container-type` on the parent, viewport-only `clamp()` breaking 200% zoom (WCAG 1.4.4). That gotcha knowledge is the deliverable, not the words-to-properties transform.

A prior exploration considered per-pattern skills (`/flex`, `/grid`, `/text`, `/color`). Rejected: each would carry the same three-sentence body while adding a `description:` competing for skill routing. Patterns become documentation examples; modern-CSS features become on-demand references; there is one skill. Three decisions were resolved during planning: class mode prints by default and appends only when the user names a target file; CSS-vs-SCSS is inferred from the project's stylesheet extensions (no stylesheet at all means plain CSS); and the reference pack was extended with modern selectors and viewport units during the alignment review. A later pass added `:not()` to the logical-selector family and a ninth reference for state selectors — `:invalid` versus `:user-invalid` and `[aria-disabled]` versus `:disabled` fail real users the same way viewport-only `clamp()` does, and the `[aria-disabled]` rule is one this repo already enforces on every stylesheet edit.

## Files

- plugins/style-agent/skills/css/SKILL.md (new) — the whole skill: parse, mode branch, token tiers, emit
- plugins/style-agent/skills/css/references/container-queries.md (new) — container-type on parent, cqi units, naming
- plugins/style-agent/skills/css/references/cascade-layers.md (new) — unlayered-wins rule, layer order, third-party CSS
- plugins/style-agent/skills/css/references/responsive-text.md (new) — clamp() with rem addend, WCAG 1.4.4, text-wrap
- plugins/style-agent/skills/css/references/progressive-enhancement.md (new) — @supports upward, prefers-reduced-motion
- plugins/style-agent/skills/css/references/logical-properties.md (new) — inline-size, margin-inline, writing modes
- plugins/style-agent/skills/css/references/modern-selectors.md (new) — :has(), :is()/:where()/:not() specificity, :nth-child of, native nesting vs SCSS
- plugins/style-agent/skills/css/references/state-selectors.md (new) — :user-invalid vs :invalid, [aria-disabled] per repo rule, :focus-visible rationale, :empty
- plugins/style-agent/skills/css/references/viewport-units.md (new) — dvh/svh/lvh mobile chrome, 100vw scrollbar overflow
- plugins/style-agent/commands/css.md (new) — thin command delegating to the skill
- plugins/style-agent/skills/create-utilities/SKILL.md (modified) — description disambiguation clause vs /css
- plugins/style-agent/.claude-plugin/plugin.json (modified) — minor version bump
- plugins/style-agent/README.md (modified) — new ### /css subsection (this file has no table)
- plugins/style-agent/CHANGELOG.md (modified) — Added entry
- plugins/style-agent/docs/README.md (modified) — Commands table row and "ships three skills" count at line 26
- plugins/style-agent/docs/commands/css.md (new) — user-facing command doc
- plugins/style-agent/docs/commands/README.md (modified) — index row and "three CSS commands" intro line
- tests/fixtures/known-bad/known-bad-css-reference.md (new) — malformed css fence plus an scss fence
- .claude-plugin/marketplace.json (modified) — style-agent description mentions authoring
- CLAUDE.md (modified) — style-agent skill and command counts, command table
- tests/validate_reference_css.py (new) — parses every fenced CSS block in the references
- tests/run.sh (modified) — invoke the new validator

## Steps

1. Write plugins/style-agent/skills/css/SKILL.md with front-matter (name, description, allowed-tools: Read, Glob, Grep, Bash, Edit, Write, AskUserQuestion matching the three sibling skills; disable-model-invocation unset per .claude/rules/skill-front-matter.md) and a workflow of clarify (step 3's gate), parse description, detect output mode, resolve tokens, consult references, emit, summarise, then offer refinements — closing every result with two or three concrete next moves drawn from what was actually emitted (tighten the gap, add a hover state, switch to inline, promote to a named class via /inline-style-to-class), since the answer is already delivered and the offer costs the user nothing; the references are listed with one-line summaries and loaded by model judgment when the parsed intent touches their topic rather than via a keyword trigger table, and the emitted summary must name which references were consulted (or state none) Why: SKILL.md is the only always-loaded artefact so all routing and workflow logic must live there; judgment-based loading handles phrasings no keyword table would anticipate, and naming the consulted references in the summary gives that judgment a visible failure signal instead of silently skipping a footgun doc Verify: head -6 shows valid front-matter including Bash, the PostToolUse SKILL.md hook passes on write, the reference list carries a one-line summary per file, the workflow names clarify as its first stage and refinement-offer as its last, and the summary spec requires a consulted-references line.
2. Write the css skill's description front-matter to state explicitly that it emits a raw CSS/SCSS rule or inline style, and add a matching one-line clause to plugins/style-agent/skills/create-utilities/SKILL.md's description stating it emits a utility-class string, each naming the other as the alternative Why: the two skills answer the same phrasing — this plan's own driving example is nearly verbatim create-utilities' documented example — so without an explicit output-form contrast in both descriptions an ambiguous request routes by inference Verify: grep both description lines and confirm each names its output form and cross-references the other skill.
3. Add a clarification gate to SKILL.md that runs before anything is emitted, batching every triggered question into a single AskUserQuestion call (never a second interrogation round, and never fired at all when the description is already concrete). Four triggers: (a) the description cannot be mapped to concrete properties with confidence, for example "make it look nice"; (b) a relative size word maps equally well to two adjacent scale steps, so "small" could be --space-2 or --space-3; (c) the description implies an interactive element but does not say which states it wants, in which case ask which of hover, focus, active, and disabled to emit — when the description already names its states ("a button with a hover state"), emit exactly those and ask nothing; (d) the description implies adaptive sizing without saying what it adapts to, in which case ask whether it should respond to its container or to the viewport, since that routes to @container versus @media — when the description already says ("adapts to its container", "stacks below 768px"), take it at its word. When no trigger fires, emit directly — a well-specified request must not be interrogated Why: guessing on any of these silently changes the output in a way the user cannot see — a tie is a coin flip on someone's design system, and the prototype showed that "a primary button with a hover state" currently returns a rule with no :hover block at all; batching keeps the cost at one turn no matter how many triggers fire Verify: the section names all four triggers, states for triggers (c) and (d) that an explicitly-specified description is taken at its word rather than questioned, states that questions are batched into one call, states that a concrete description skips the gate entirely, and states that nothing is emitted until the answers resolve.
4. Specify the output-mode branch in SKILL.md: class mode prints the rule by default and appends to a stylesheet only when the user names a target file — and before any append, confirm the resolved target path and class name with the user, since appending mutates a file in their project; the class name itself is proposed from the description rather than asked for, and the proposal is named in the summary so a bad guess costs one follow-up. Appending reuses inline-style-to-class's proven collision rule (on a same-name-different-value clash append a numeric suffix -2, -3, and report it); SCSS vs plain CSS is inferred from the project's stylesheet extensions with plain CSS as the no-stylesheet default; inline mode fires when the user says inline or points at an element, and is refused with a one-line reason (falling back to class mode) when the description implies :hover, :focus-visible, @media, @container, @layer, @supports, or a pseudo-element Why: this is the skill's only real branch and its only silent-wrong-answer risk since a dropped :hover in an inline style is lost without error, and appending without the sibling's collision rule would write a conflicting selector into a real user stylesheet Verify: the section names all seven refusal triggers, states the fallback is class mode, states the print-by-default and extension-inference rules, specifies the numeric-suffix collision behaviour, and requires an explicit confirmation of target path and class name before any append.
5. Add a focus-visible step to SKILL.md between token resolution and emit: when the parsed description implies an interactive element (button, link, input, select, or a custom widget) emit a :focus-visible rule alongside the requested styling, or when the output mode cannot carry one state its absence in the summary Why: create-utilities Step 4 already guarantees this and without the parity a generated button rule ships with no focus indicator, failing WCAG 2.4.7 Verify: the section names the interactive-element trigger list and states both the emit path and the summary-warning path.
6. Specify token resolution in SKILL.md as three tiers: exact-value match uses the variable, semantic-name match uses it and names the choice in the summary, no match emits the literal; the skill greps the project for custom-property declarations and reads the whole scale before mapping relative words like small, and never creates a new custom property unless asked Why: "small" is a position in a scale not a value, and inventing tokens would write into someone's design system on a throwaway request — deliberately inverting inline-style-to-class, where the value is already committed Verify: the section states all three tiers, the whole-scale read, and the no-invention rule with a cross-reference to inline-style-to-class.
7. Write references/container-queries.md covering container-type: inline-size on the parent, that a container cannot query itself, cqi/cqb versus viewport units, container-name for nesting, and one correct minimal template, cross-linking cascade-layers.md Why: the missing container-type omission is the most common container-query failure and produces CSS that silently never matches Verify: the file contains a fenced CSS block declaring container-type on a parent selector before any @container rule.
8. Write references/cascade-layers.md covering the unlayered-styles-win rule, the @layer order declaration coming first, where third-party CSS belongs, and !important inverting layer order, cross-linking container-queries.md Why: unlayered-beats-layered is counter-intuitive and is why most first @layer attempts appear to do nothing Verify: the file states the unlayered-wins rule in prose, not only in a code comment.
9. Write references/responsive-text.md covering clamp() with a rem-plus-vw preferred term, that a pure-vw term fails WCAG 1.4.4 at 200% zoom, a worked slope formula, and text-wrap balance and pretty Why: fluid type is the most-requested modern-CSS item and its accessibility failure is invisible without explicitly testing zoom Verify: the file names WCAG 1.4.4 and shows a clamp() whose middle term includes a rem addend.
10. Write the four short references — progressive-enhancement.md (@supports detecting the new feature and enhancing upward rather than not-detection cascading down, prefers-reduced-motion, prefers-contrast), logical-properties.md (inline-size, block-size, margin-inline, padding-block, inset, writing-mode rationale), modern-selectors.md (:has() with its no-pseudo-element restriction, :is() taking the highest specificity of its list versus :where() contributing zero, :not() sharing the same highest-of-list rule in its multi-argument form and matching far wider than authors expect, :nth-child(An+B of S), and native CSS nesting and how its & differs from SCSS), and viewport-units.md (dvh/svh/lvh versus vh under mobile browser chrome, and 100vw causing horizontal overflow when a scrollbar is present) Why: all four are short gotcha files that complete the modern-CSS pack, :not() belongs beside :is()/:where() because it shares their specificity rule and is misremembered the same way, and none warrants its own step Verify: each file has at least one fenced CSS block, progressive-enhancement.md does not use @supports not as the primary pattern, and modern-selectors.md states both the :where() zero-specificity rule and the :not() multi-argument specificity rule in prose.
11. Write references/state-selectors.md covering :invalid matching an empty required field before the user has typed (so :user-invalid and :user-valid are the correct defaults for form styling), [aria-disabled="true"] rather than the native :disabled selector per .claude/rules/scss-conventions.md, why :focus-visible is emitted instead of :focus (a mouse click should not paint a focus ring, which is why authors delete rings entirely and break keyboard use), :empty treating whitespace as content, and :placeholder-shown Why: state selectors are a second selector family the pack does not cover at all, and their naive choices fail real users the same way viewport-only clamp() does — a form that lights up red on load, or a disabled control that drops out of the tab order; the aria-disabled entry also stops the skill from generating CSS that violates a convention this repo already enforces on every stylesheet edit Verify: the file states the :user-invalid-over-:invalid default in prose, cites .claude/rules/scss-conventions.md for the aria-disabled rule, and carries at least one fenced CSS block.
12. Write plugins/style-agent/commands/css.md per .claude/rules/command-authoring.md: YAML front-matter with argument-hint: [description] matching create-utilities.md, plus a body that only delegates to the skill Why: repo convention keeps commands as thin entry points with logic in SKILL.md, and naming the argument-hint concretely keeps this step as specific as the rest of the plan Verify: the PostToolUse command front-matter hook passes, the front-matter carries argument-hint: [description], and the body contains no workflow steps.
13. Write tests/validate_reference_css.py extracting every fenced css block from the css skill's references, syntax-checking each with tinycss2 under the repo's generator/validator contract (errors to stderr, exit 0/1/2), and failing on any scss fence since the references are plain-CSS-only by decision; commit tests/fixtures/known-bad/known-bad-css-reference.md carrying one malformed css fence and one scss fence, and wire both the real run and a known-bad self-test into tests/run.sh alongside the existing known-bad section Why: this is a tokenizer-level syntax gate, not a correctness gate — tinycss2 will happily accept an invalid container-type keyword or a :has() containing a pseudo-element, so the per-file prose greps in steps 7 to 11 remain the real check on the gotcha claims; the committed known-bad fixture follows the pattern every other validator in this harness already uses so a future regex regression cannot pass silently Verify: python3 tests/validate_reference_css.py exits 0 on the real references and non-zero on the committed known-bad fixture, and tests/run.sh runs both assertions.
14. Update paperwork in one pass: bump plugin.json minor version, add the CHANGELOG Added entry, add a ### /css subsection to the style-agent README matching the existing per-command When-to-use / How-to-run / Example shape (that file has no table), update docs/README.md's Commands table and its "ships three skills" count, write docs/commands/css.md plus its index row and correct that file's "three CSS commands" intro line, update the marketplace.json description, and correct the style-agent counts in root CLAUDE.md Why: the repo pre-submit checklist requires all of these, three separate docs files carry a hard-coded "three" that goes stale the moment /css ships, and batching avoids a second commit Verify: tests/run.sh is green, no grep for "three skills" or "three CSS commands" matches under plugins/style-agent/, and grepping CLAUDE.md for style-agent shows four skills, four commands, and the /css entry.

## Tests

Tier 1 — This plan adds an executable validator to tests/
- Objective: every fenced CSS block in the css skill's reference files tokenizes without error, making broken guidance fail the build. File: tests/validate_reference_css.py; Type: smoke; Asserts: the guidance the skill hands users is syntactically valid CSS and carries no scss fence; Run: python3 tests/validate_reference_css.py
- Unit: the validator's own extraction and rejection logic. File: tests/fixtures/known-bad/known-bad-css-reference.md; Targets: validate_reference_css.py fence extraction; Key cases: a malformed css fence exits non-zero, an scss fence exits non-zero, multiple fences in one file are all checked
- Integration: repo-wide structural checks still pass with the new skill and command present. File: tests/run.sh; Targets: validate_manifest.py plus the new validate_reference_css.py; Key cases: style-agent still satisfies the manifest contract (commands/*.md present, SKILL.md under skills/), reference CSS parses, and the known-bad fixture is rejected

Scope note: tinycss2 is a tokenizer, so this validator is a syntax gate only — it cannot catch an invalid container-type keyword, a :has() containing a pseudo-element, or a malformed clamp() argument shape. The per-file prose assertions in steps 7 to 11 are the real correctness gate for the gotcha claims, and the skill-behaviour acceptance criteria below are verified by the manual walkthrough in Verification, not by CI.

## Acceptance Criteria

- [ ] /css "a flex row aligned centered with a small gap" emits a valid CSS rule
- [ ] With --space-2: 0.5rem present in the project the emitted gap uses var(--space-2); with no matching variable it emits the 0.5rem literal
- [ ] No new CSS custom property is ever written unless the user explicitly asks for one
- [ ] Class mode prints by default and appends to a stylesheet only when the user names a target file, suffixing -2/-3 on a same-name-different-value collision
- [ ] A description implying an interactive element yields a :focus-visible rule, or a summary warning when the mode cannot carry one
- [ ] A too-vague description triggers follow-up questions instead of a guessed rule
- [ ] A size word that maps equally to two adjacent scale steps is asked about, never coin-flipped
- [ ] An interactive-element request with unspecified states asks which of hover, focus, active, disabled to emit, and emits exactly those
- [ ] An interactive-element request that already names its states emits them without asking
- [ ] An adaptive-sizing request asks container-versus-viewport only when the description does not already say which
- [ ] A concrete, fully-specified description is emitted with no questions asked
- [ ] Every triggered question arrives in a single batched round, never a second interrogation
- [ ] Appending to a stylesheet confirms the target path and class name before writing
- [ ] Every result closes with two or three concrete refinement offers drawn from what was emitted
- [ ] The emitted summary names which references were consulted, or states none
- [ ] The css and create-utilities descriptions each name their output form and cross-reference the other
- [ ] /css inline emits a style attribute for a static description and refuses with a stated reason (falling back to class mode) when the description implies :hover, :focus-visible, @media, @container, @layer, @supports, or a pseudo-element
- [ ] A container-query request produces CSS with container-type set on the parent, not only an @container block
- [ ] A @layer request notes that unlayered styles outrank layered ones
- [ ] A fluid-type request produces a clamp() whose preferred term includes a rem addend, never viewport units alone
- [ ] A form-validation request styles :user-invalid rather than :invalid, so empty untouched fields are not marked as errors on load
- [ ] A disabled-state request emits [aria-disabled="true"] rather than :disabled, per .claude/rules/scss-conventions.md
- [ ] modern-selectors.md states both the :where() zero-specificity rule and the :not() multi-argument highest-of-list rule
- [ ] Reference files contain only fenced css blocks — the validator rejects scss fences
- [ ] The committed known-bad fixture makes the validator exit non-zero, asserted by tests/run.sh
- [ ] No "three skills" or "three CSS commands" string remains under plugins/style-agent/
- [ ] tests/run.sh is green including the new validator stage
- [ ] plugin.json version bumped and marketplace.json carries no version key
- [ ] Root CLAUDE.md reflects four style-agent skills and four commands

## Verification

Run tests/run.sh from the repo root and confirm it is green, including the new validate_reference_css.py stage. Install locally with claude --plugin-dir ./plugins/style-agent, then run the driving prompt /css "I want a flex row aligned centered with a small gap" in a fixture project with a --space-* scale and again in one without: the first must emit var(--space-2) (or the matching token, named in the summary) and the second the 0.5rem literal.

Run /css inline "flex row with a hover state" and confirm it refuses inline mode with a reason and emits a class instead. Run /css "a card that adapts to the width of its slot" and confirm container-type: inline-size lands on the parent. Run /css "heading that scales with the viewport" and confirm the clamp() middle term contains a rem addend and the summary mentions 200% zoom. Finally, git diff in the fixture projects must show no created custom properties and no stylesheet writes beyond an explicitly requested append.

## Review Record

Markdown-only section. Seven-reviewer Agent Team run on 2026-07-19 (architecture, completeness, testability, risk, conventions, UX, accessibility). No reviewer recommended rejection. Recorded here rather than appended to the rendered HTML because the HTML is regenerated from this spec and any direct HTML edit would be lost on the next render.

Agreements across independent reviewers: routing collision with create-utilities (risk + conventions); reference loading having no failure signal (architecture + risk); known-bad fixture over manual introduce-then-revert (testability + completeness); the /css to inline-style-to-class cross-link sitting in Next Steps (UX + architecture). No conflicts between reviewers.

Applied without triage — six factual errors verified against the repo: docs/README.md omitted from Files while asserting "ships three skills" at line 26; the README.md edit described as a table row when that file uses ### subsections; the docs/commands/README.md "three CSS commands" intro; the missing committed known-bad fixture where tests/fixtures/known-bad/ already holds known-bad.scss and known-bad.tsx; allowed-tools dropping Bash that all three siblings carry; an unspecified argument-hint.

Applied after triage: description disambiguation in both css and create-utilities (step 2); vague-description branch (step 3); focus-visible step (step 5); append collision suffixing (step 4); summary naming consulted references (step 1); corrected validator framing from correctness gate to tokenizer-level syntax gate (step 13 and the Tests scope note).

Reviewed and declined: a visually-hidden/sr-only reference file; forced-colors coverage in progressive-enhancement.md; an explicit out-of-scope declaration for contrast checking; enumerating the full summary contents; resolving whether "points at an element" means IDE selection or chat text; renaming the skill to a verb phrase; broadening python-scripts.md's glob to cover tests/.

Later reversal: the UX reviewer's token tie-break finding, declined during triage above, was reinstated when the skill's direction shifted toward clarifying with the user rather than defaulting silently. It now sits inside step 3's clarification gate alongside two further triggers — which states to emit for an interactive element, and container-versus-viewport for adaptive sizing. The gate batches every triggered question into one round and does not fire at all on a concrete description, so `plan-mode.md`'s "no friction on well-specified requests" still holds. Class name remains a proposal rather than a question, named in the summary so a bad guess costs one follow-up.

## Next Steps

- Add pattern examples to the command doc instead of as skills
  ```text
  In the agentic-acss-plugins repo, edit plugins/style-agent/docs/commands/css.md:
  add a "Common patterns" section with worked /css invocations and exact output
  for flex row, flex column, grid with named areas, centered container with
  max-inline-size, fluid-type text block, and a colour pair. Documentation
  examples only — do not create /flex, /grid, or /text commands or skills.
  Verify by rendering the markdown and confirming each example's CSS parses.
  ```
- Cross-link /css with the conversion skills
  ```text
  In the agentic-acss-plugins repo, add one line each to
  plugins/style-agent/skills/css/SKILL.md and
  plugins/style-agent/skills/inline-style-to-class/SKILL.md so /css inline
  points at /inline-style-to-class for later promotion to a named class and
  inline-style-to-class mentions /css as its authoring counterpart. Do not
  restructure either workflow. Verify with grep that each file mentions the
  other skill exactly once.
  ```
- Evaluate a colour/contrast reference
  ```text
  In the agentic-acss-plugins repo, decide whether
  plugins/style-agent/skills/css/references/ needs a color.md covering OKLCH,
  relative colour syntax, color-mix(), and WCAG contrast. First check whether
  plugins/acss-kit/skills/styles/references/ already covers this well enough
  to cross-link instead of duplicating. Deliver a link-vs-duplicate
  recommendation with reasoning; make no file changes until approved.
  ```
