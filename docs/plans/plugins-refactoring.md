---
status: proposal
type: refactor
created: 2026-06-14
repo-name: acss-plugins
---

# Proposal: Plugins refactoring

> Covers the four targets selected in review — the **style-agent ↔ acss-kit
> boundary**, **overlap/duplication**, **doc/structure drift**, and **prep for
> the DESIGN.md work**. Grounded in a full pass over both plugins. The headline:
> the two plugins are **complementary, not overlapping**, and the most valuable
> near-term work is a **doc-truth pass** plus **boundary clarification** — *not*
> a code reorg, which the plugin format actively resists.

## Load-bearing constraint (verified): plugins are self-contained

Each plugin resolves scripts and assets through its **own**
`${CLAUDE_PLUGIN_ROOT}`; a repo grep finds **no cross-plugin references** (every
`plugins/acss-kit/...` mention is acss-kit referring to itself), there is **no
`shared/` or `core/` plugin**, and the Claude Code marketplace format has **no
plugin-dependency mechanism** — installs are independent.

**Consequence:** a cross-plugin "shared core" (the natural instinct for the
generic OKLCH math, token serialization, and CSS-resolver helpers) is **not
viable** without either code duplication or a third plugin the marketplace can't
guarantee is installed. This single fact reframes targets 1 and 4: the boundary
is drawn by **responsibility**, not by extracting shared code.

## Target 1 — style-agent ↔ acss-kit boundary

**Finding: no functional overlap.** The plugins operate at different layers:

| Plugin | Owns | Coupling |
|---|---|---|
| `acss-kit` | fpkit component generation, OKLCH theming, prebuilt utility/bridge bundles, React/Sass setup detection | fpkit/React-bound |
| `style-agent` | generic CSS class authoring (`css-to-class`, `inline-style-to-class`, `create-utilities`), multi-framework detection | framework-agnostic |

**Coupling is asymmetric.** Three tiers, from the analysis:

- **Generic algorithm, acss vocabulary** — `_oklch.py`, `generate_palette.py`,
  `tokens_to_css.py`/`css_to_tokens.py`, `validate_theme.py`. The *math* is pure
  stdlib with zero fpkit references; the *role names* (the 18 `--color-*`
  properties) and contrast pairs are acss-specific.
- **Tightly fpkit-bound** — the 15 component skills + `kit-core` (`data-*`
  selectors, polymorphic `UI`, `aria-disabled`), `generate_bridge.py`
  (hard-coded fpkit alias map), setup detectors (`detect_stack.py`,
  `verify_integration.py` — React + Sass).
- **Already generic, already in style-agent** — the css-to-class resolver,
  variable discovery, framework detection.

**Recommendation: do not split the plugins, and do not build a shared core now.**
The generic-but-acss-vocabulary tooling stays in `acss-kit` (its only consumer).
Draw the boundary by responsibility:

> **`style-agent`** = author/transform CSS *in place* for *any* project.
> **`acss-kit`** = generate + theme *fpkit* projects.

If a genuine second consumer of the color math ever appears, revisit via a
dedicated `core` plugin — but that's premature today (YAGNI given one consumer).

## Target 2 — overlap / duplication

The only near-collision is **utility generation**:

| | `acss-kit /utility-add` + `utilities` skill | `style-agent /create-utilities` |
|---|---|---|
| What | Copies a **prebuilt** `utilities.css` (+ `token-bridge.css`) into a React project | **Generates** a class string from a plain-language description |
| Framework | fpkit/acss only | Detects acss-kit / Tailwind / Bootstrap / fallback |
| Output | Files on disk | A ready-to-paste string |

These are **not the same capability** and should not be merged — but a user
won't know which to reach for. This is a **positioning problem, not a code
problem.** Fix it with docs: a short "when to use which" note in both READMEs
and the marketplace blurbs, cross-linking the two. (Same for `css-to-class`,
which acss-kit users can also use — it's framework-agnostic.)

## Target 3 — doc / structure drift (the concrete, low-risk win)

A full audit found **16 findings**; the high-impact ones:

| # | File | Stale claim | Truth |
|---|---|---|---|
| 1 | `CLAUDE.md:14` | style-agent "First skill: `/css-to-class`" | 3 skills + 3 commands |
| 2 | `CLAUDE.md:46` | style-agent "One skill … and one command" | 3 and 3 |
| 3 | `CLAUDE.md:13` | acss-kit skill list omits `prompt-book` | 22 skills total |
| 4 | `CLAUDE.md:98` | acss-kit command table missing `/color-scale` | 17 commands |
| 5 | `CLAUDE.md:99` | style-agent table lists only `/css-to-class` | + `/inline-style-to-class`, `/create-utilities` |
| 6 | `README.md:16` | acss-kit version `1.1.0` | `1.2.1` |
| 7 | `README.md:17` | style-agent version `0.2.0` | `0.4.0` (→ `0.5.0` after the COMPONENT.md plan) |
| 8 | `README.md:130` | "16 component references" | 15 |
| 9 | `README.md:132–133` | references skills `component-form`, `component-creator` | **do not exist** |
| 10 | `README.md:146` | skills list shows monolithic `components`, omits `kit-core` | 15 `component-*` + 7 named |
| 11 | `AGENTS.md:34,38` | `skills/components/SKILL.md` path + same phantom skills | pre-split layout; no longer exists |
| 12 | `marketplace.json` | acss-kit lists 10/17 commands; style-agent omits `/create-utilities` | incomplete |
| 13 | `acss-kit/CHANGELOG.md` | historical refs to `acss-utilities` (renamed plugin) | leave (history), but note |

**Recommendation: one "doc-truth pass" PR.** Mechanical, low-risk, high-value —
it removes references to skills that never shipped and corrects every count and
version. This is the first thing to execute and can land immediately.

## Target 4 — prep for the DESIGN.md / COMPONENT.md work

Placement decisions, made consistent with the self-containment constraint:

| New artifact | Home | Why |
|---|---|---|
| `COMPONENT.md` spec (Workstream B) | **style-agent** | Decided in review; pure docs, framework-neutral |
| `design_md_to_tokens.py`, `validate_design_md.py`, `tokens_to_design_md.py` | **acss-kit** | They consume `css-tailwind` and emit **acss role CSS**; they live with the theme pipeline, OKLCH gap-synthesis, and `validate_theme.py` they depend on |
| Token homes (`typography.css`, `space-radius.css`, schema growth) | **acss-kit** | Extends `theme.schema.json` / `_tokens.py` / `tokens_to_css.py` |
| `/theme-from-design`, `/design-export` | **acss-kit** | Wrap the adapter + existing `styles` pipeline |

The apparent cross-plugin tension — `COMPONENT.md` lives in style-agent but the
DESIGN.md *adapter* lives in acss-kit — **is not a problem**: the two coordinate
through the **file format** (`{token.path}` references), not through shared code.
A spec is a document; the adapter is an implementation. This is exactly the loose
coupling the self-containment constraint forces, and it's the right shape anyway.

> **Note:** "DESIGN.md is framework-agnostic, so its tooling should be in
> style-agent" is a tempting but wrong inference — the *format* is neutral, but
> *our adapter into our theme* is acss-specific (role vocabulary, OKLCH
> synthesis, contrast gate). It belongs where its dependencies are.

## Recommendations summary

1. **Keep two plugins; no shared core** (format-blocked, single-consumer).
2. **Boundary by responsibility** — style-agent transforms any CSS in place;
   acss-kit generates/themes fpkit.
3. **Don't merge utility commands** — clarify positioning in docs instead.
4. **Run a doc-truth pass** — fix the 16 drift findings (execute first).
5. **Place DESIGN.md tooling in acss-kit, COMPONENT.md spec in style-agent** —
   coordinate via the file format, not code.

## Sequenced plan

| PR | Scope | Risk | Status |
|---|---|---|---|
| **R1** | Doc-truth pass — fix the 16 drift findings across CLAUDE.md, README.md, AGENTS.md, marketplace.json | Low (docs only) | ready to execute |
| **R2** | Boundary/positioning docs — "when to use which" matrix in both READMEs + marketplace cross-links | Low | after R1 |
| **B / A…** | COMPONENT.md spec + DESIGN.md token homes/adapter | — | per `design-md-spec-alignment.md` roadmap; placement settled above |

## Open questions

1. **Future `core` plugin?** Defer until a real second consumer of the color
   math exists. (Today: premature.)
2. **Multi-framework theming in style-agent?** Blocked by both the vocabulary
   coupling and the sharing constraint — out of scope unless prioritized.
3. **`acss-utilities` history in CHANGELOG** — leave as historical record, or
   add a one-line note that it was folded into `acss-kit`?
