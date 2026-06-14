---
status: proposal
type: feature
created: 2026-06-14
repo-name: acss-plugins
---

# Proposal: a `flesh-out` skill — turn a half-formed idea into a decision-complete proposal

> This proposal codifies the workflow this very session used — taking "look at
> design.md and align our components" from a vague prompt to a 750-line,
> decision-complete proposal plus execution plans — into a reusable skill. The
> session is the worked example; every principle below maps to a concrete moment
> in it.

## The problem

A lot of valuable work starts as a half-formed idea: *"compare X to how we do
it,"* *"should we adopt Y,"* *"how would we…"*. The failure modes are
predictable:

- **Speculation over grounding** — answering from memory instead of fetching the
  real spec, reading the real code, or measuring the real numbers.
- **Surveying instead of deciding** — listing options forever without separating
  what's a *fact to look up* from what's a *decision for the human*.
- **Decisions that evaporate** — choices get made in chat, then never recorded or
  propagated into the artifact, so the next round re-litigates them.
- **One-shot reports** — a wall of text that can't be deepened, corrected, or
  turned into action.

The `flesh-out` skill is a **thinking partner** that avoids these: it researches
to ground, distinguishes facts from decisions, drives the human-in-the-loop
decision cadence, and produces a single living proposal artifact that deepens
each round and converges on something buildable.

## What the skill does (the workflow it codifies)

A loop, not a pipeline — the human steers it with "keep gathering," answers to
questions, and "let's build it":

0. **Frame.** Restate the idea in one line; name the domain(s) it touches.
   If it's underspecified, ask 2–3 clarifying questions *before* researching;
   otherwise proceed.
1. **Fan out research, in parallel.** Identify the external sources (web/docs,
   the actual spec/repo) and internal sources (this codebase) the idea touches,
   and gather them **concurrently** — `WebFetch`/`WebSearch` for the outside,
   `Explore`/`general-purpose` agents for breadth across the codebase (to
   preserve main-thread context). Ground, never speculate.
2. **Synthesize the core finding.** Don't dump what you read — state the *central
   insight*: how the idea relates to what already exists, in a side-by-side
   comparison. Surface the load-bearing realization, not a survey.
3. **Separate facts from decisions.** Maintain two lists: what's now *known* vs.
   what is genuinely the *human's call*. If unknowns are still facts, loop to
   step 1 ("keep gathering"). Only when the remaining unknowns are **decisions,
   not missing facts**, move on.
4. **Resolve decisions with the human.** Use `AskUserQuestion`,
   **recommendation-first** (best option labelled, with rationale) — never a bare
   menu. Then **record every answer in the artifact and propagate its
   consequences** to every section it touches.
5. **Author the proposal artifact.** Write/append to `docs/plans/<slug>.md` in
   the canonical shape (below); **commit and push each meaningful round** — the
   doc is the deliverable, chat is scaffolding.
6. **Deepen on request.** Each "continue / keep going" adds a *distinct layer*
   (tooling surface, worked examples, appendices, roadmap, a diagram) — grounded
   in new sources, never padding.
7. **Converge to execution.** When the proposal is decision-complete, offer to
   split it into execution plans using the repo's `Why`/`Verify` step format.

## Right-sizing triage (the scale-down gate)

Step 0 first picks a **tier**, so a small idea never gets a 10-section doc. The
skill scales the loop and the artifact to match:

| Tier | Signal | Response |
|---|---|---|
| **0 — Answer** | Single fact, known answer, or a well-specified task | Answer directly; **do not invoke the loop**. (e.g. "what version is style-agent?") |
| **1 — Lightweight** | A small, well-scoped idea touching one surface | One research pass; a short proposal (Context · finding · recommendation · open questions); skip appendices/roadmap. Often a single round. |
| **2 — Full** | Broad/ambiguous idea, external + internal surface, real decisions to make | The full 8-step loop and canonical artifact shape, deepened over multiple rounds. (This session was Tier 2.) |

The tier is a starting estimate, not a cage — escalate Tier 1 → 2 if research
reveals more surface, and stop early if a Tier 2 idea collapses to a clear answer.
Naming the tier out loud also sets the human's expectations for depth and pace.

## The proposal-artifact shape

The structure this session converged on, worth making canonical:

- **Front-matter** — `status` (proposal → plan), `type`, `created`.
- **Context** — the idea and why it's on the table.
- **Core finding** — the one central insight, called out as a block quote.
- **Side-by-side / comparison** — the idea vs. the existing approach, in a table.
- **Locked & resolved decisions** — what's settled, with dates.
- **Workstreams / options** — the distinct strands of work.
- **Risks & tensions** — honestly stated, including what's hard.
- **Open questions** — *only decisions remain here*; facts have been resolved.
- **Roadmap** — phased, dependency-ordered, sized (S/M/L).
- **Appendices** — the grounded artifacts (mapping tables, worked examples, I/O
  contracts) that make claims testable.

## Operating principles (the part that makes it work)

Each maps to a real moment in this session:

| Principle | This session |
|---|---|
| **Ground every claim in a real source.** | Fetched the real `paws-and-paths/DESIGN.md`, read the real `export.ts`, loaded the real Figma tool schemas — not memory. |
| **Quantify; don't hand-wave.** | Measured the component sweep: ~97 spacing + ~19 radius + ~47 typography = ~163 sites. |
| **Separate facts from decisions.** | "Keep gathering" → more grounding; once converged → surfaced four decisions via `AskUserQuestion`. |
| **Recommendation-first questions.** | Every option had a "(Recommended)" with rationale, not a bare list. |
| **Record decisions and propagate.** | After the four answers, updated Locked decisions *and* C.2, Appendix C, Workstream B, Next step. |
| **Iterative deepening, distinct layers.** | Rounds added: tooling surface → M3 grounding → appendices → export shapes/roadmap → diagram/inventory. |
| **Parallel fan-out; spawn agents for breadth.** | First move launched a `WebFetch` and an `Explore` agent together; later inventories ran as agents. |
| **Surface incidental findings.** | Research caught real bugs: `--color-primary-dark` not in the schema; alert hardcodes state colors; 16 doc-drift items. |
| **Commit the artifact each round.** | Eight commits pushed to the branch; the doc, not the chat, is the record. |
| **Signal convergence explicitly.** | Stated when "remaining unknowns are decisions, not missing facts." |

## Relationship to existing capabilities (why this isn't redundant)

`flesh-out` is the **upstream, human-in-the-loop, idea→proposal** layer. It sits
between "raw idea" and "implementation plan," and it *composes with* existing
tools rather than replacing them:

| Capability | What it does | How `flesh-out` differs / composes |
|---|---|---|
| **`deep-research` skill** | One-shot, web-centric, adversarially-verified **cited report** on a topic | `flesh-out` adds **codebase grounding**, a **human decision cadence**, and a **living proposal artifact** that converges on something buildable. It can **delegate its web-research phase to `deep-research`**, then layer on the rest. deep-research answers "what's true about X"; flesh-out answers "should we, and what exactly." |
| **`Plan` agent / execution-plan format** | Produces an **implementation plan** (steps, critical files, trade-offs) assuming the *what* is decided | `flesh-out` is **upstream** — it decides the *what/whether* and produces the proposal, then **hands the decided proposal to** the Plan agent or the repo's `Why`/`Verify` plan format for the *how*. Clear seam: flesh-out = "should we + what"; Plan = "how." |
| **Plan mode (`EnterPlanMode`)** | A harness gate for proposing a code change before acting | Different axis — that gates *edits*; `flesh-out` develops *ideas*. They can co-exist (flesh-out may run, then later work enters plan mode). |
| **`AskUserQuestion`** | Asks the user a structured question | A **tool `flesh-out` orchestrates** at step 4, not a competitor. |

The unique value is the **combination**: codebase + web grounding, an explicit
facts-vs-decisions discipline with the human in the loop, and a committed
artifact that deepens and converges — none of the above do all three.

## Proposed skill definition (draft)

Aligned with this repo's existing project-skill convention (`add-command`,
`release-plugin`): a slash-invocable, discoverable skill with `name` /
`description` / `disable-model-invocation: false` front-matter and a step-oriented
body. The repo's project skills omit `allowed-tools`, so this one does too (the
tools it leans on — `WebFetch`/`WebSearch`, `Agent`, `Read`/`Grep`/`Glob`,
`Write`/`Edit`, `Bash`, `AskUserQuestion` — are named in the body instead).

```yaml
---
name: flesh-out
description: >-
  Use when the user has a half-formed idea, a "should we / how would we"
  question, or wants to compare an external approach to ours and propose
  alignment. Researches across web + codebase in parallel, grounds every claim
  in real sources, separates facts from decisions, drives the decision cadence,
  and produces a decision-complete proposal doc under docs/plans/.
disable-model-invocation: false
---
```

Invocation: `/flesh-out <idea>` (or auto-triggers on a matching idea-shaped
prompt). The body is the right-sizing triage, the 8-step workflow, the
artifact-shape template, and the principles table — written as operating
instructions.

**When to use:** a vague-but-promising idea; a "compare and align" request;
anything needing research → comparison → a decision-complete proposal *before*
building.

**When not to use:** a concrete bug fix, a well-specified implementation task, or
a single factual lookup — those are Tier 0 below (answer directly, no loop).

## Where it lives

Three options:

1. **Project skill (`.claude/skills/flesh-out/`)** — alongside `add-command`,
   `release-plugin`, etc. Pro: versioned with this repo, discoverable here.
   Con: domain-general value trapped in one repo.
2. **Personal/global skill (`~/.claude/skills/`)** — Pro: available in every
   session/repo, which matches how general this workflow is. Con: not shared.
3. **A new framework-agnostic plugin** — overkill for one skill today.

**Recommendation:** start as a **project skill** here. The precedent is exact —
`.claude/skills/` already holds nine slash-invocable, discoverable workflow
skills (`add-command`, `release-plugin`, `validate-plugins`, …) with the same
`disable-model-invocation: false` shape, so `flesh-out` drops in with zero new
machinery. Add an explicit note that it is domain-general and a candidate to
promote to a global skill (`~/.claude/skills/`) once proven.

## Risks & tensions

- **Over-process for small ideas.** Step 0's "is this specific enough / big
  enough" gate must be real — trivial ideas should skip the loop, not get a
  10-section doc. The skill should *scale down* gracefully.
- **Research that never converges.** The facts-vs-decisions test (step 3) is the
  stop condition; without it, "keep gathering" runs forever. The skill must name
  convergence out loud.
- **Decision drift.** The propagate-on-answer rule (step 4) is load-bearing; if
  decisions aren't written back into the artifact, the doc rots. Worth a
  checklist line: "after every answer, update Locked decisions + each affected
  section."
- **Artifact sprawl.** Deepening must add distinct layers, not volume. The
  reviewer test: could each new section be a future execution-plan input?

## Open questions

1. **Name.** `flesh-out` vs. `develop-idea` / `scope` / `think-through` /
   `proposal`. (`flesh-out` matches the user's framing.)
2. **Placement.** Project skill now vs. global skill (see above).
3. **Artifact location.** Always `docs/plans/`, or a dedicated `docs/proposals/`
   to distinguish exploratory proposals from execution plans?
4. **Convergence handoff.** Should the skill itself author the execution
   plan(s), or stop at "decision-complete proposal" and hand to a separate
   planning skill?

## Dogfooding / self-test

This proposal was itself produced by the workflow it describes — which gives the
implementation a built-in test corpus. The five docs this session generated are
the regression set:

- `design-md-spec-alignment.md` — the Tier 2 exemplar (multi-round deepening,
  four resolved decisions, seven appendices).
- `component-md-spec.md` — the convergence handoff (proposal → execution plan).
- `plugins-refactoring.md` — research surfacing incidental findings (16 drift
  items, a verified architectural constraint).
- this file — the recursive case (the skill proposing itself).

Authoring `flesh-out/SKILL.md` should reproduce shapes like these; if it can't,
the skill body is underspecified.

## Next step

On approval, convert this into an execution plan and author
`.claude/skills/flesh-out/SKILL.md` with the right-sizing triage, the 8-step
workflow, the artifact-shape template, and the principles table — using this very
document (and the four siblings above) as the skill's canonical worked examples.
