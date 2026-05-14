---
name: style-tune
description: Use when the user wants to adjust the visual feel of a component or theme role — 'warmer button', 'softer card', 'bolder primary', 'calmer alert'.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion
metadata:
  version: "0.5.0"
---

# /style-tune

Route a natural-language aesthetic intent ("warmer button", "softer card", "deeper accent") to either a theme-role OKLCH edit or a component SCSS token edit. The full workflow for each layer lives in the parent skill; this router handles intent parsing and dispatch.

## Step 0 — Exit plan mode

Call `ExitPlanMode` before parsing intent. Both downstream paths write to disk — `/theme-update` edits theme CSS, component-layer edits SCSS in place, and OKLCH scripts run via Bash. Plan mode blocks all of these.

Stay in plan mode only when the user explicitly asked for a preview ("show me the deltas", "don't apply yet"). In that case, narrate the resolved `(modifier, token-family, layer)` tuples from Step A without invoking Write/Edit/Bash, and wait for approval.

---

## Step A — Resolve intent

### A0. Load the intent vocabulary

Read `${CLAUDE_PLUGIN_ROOT}/skills/style-tune/references/intent-vocabulary.md`. Each row maps a modifier (and synonyms) to a token family + canonical delta + "var-only fallback" route.

### A1. Tokenize the prompt

Parse the prompt for vocabulary matches. Each match yields a `(token-family, delta, layer-hint)` tuple. Record all matches before dispatching.

### A2. Resolve the subject and dispatch

| Subject in prompt | Layer | Follow |
|---|---|---|
| `primary`, `accent`, `danger`, `warning`, `info`, `success`, `brand`, `theme`, `app` | theme | `styles/SKILL.md` — Style-Tune Mode |
| `button` / `btn`, `card`, `alert`, `dialog`, `input`, `nav`, `form` | component | `components/SKILL.md` — Style-Tune Mode |
| bare `this` / `it` / `the component` / `everything` | ambiguous | AskUserQuestion |

"This button" / "the button" / "buttons" always map to a **global** SCSS edit — never inline `style={...}` props.

### A3. Confirm low-confidence intents

Use `AskUserQuestion` (≤ 4 options) when:
- The prompt is a single bare adjective with no subject ("warmer").
- A modifier has multiple plausible token families ("louder" → border vs shadow vs both).
- Modifiers contradict each other ("calmer but bolder").
- Subject is "alert" and modifier is a colour modifier — ask whether to tune base tokens only or include all four severity variants.

For unambiguous prompts, skip A3 and dispatch immediately.

---

## Step F — Summary

After the layer workflow completes, print:

```text
Layer:       <theme | component | both>
Files:       <list>

Modifier         Token / Role               Old           New           Status
warmer           --color-primary            #2563eb       #3265ec       accepted
warmer           --color-primary-hover      #1e4dc7       #294fc8       accepted
softer           --btn-radius               0.375rem      0.5625rem     accepted
calmer           --color-danger             #dc2626       #d8413b       reverted (contrast)

Notes:
  - <any var-only fallback routing notes or drift warnings from the layer workflow>

Next:
  - Try "now go a touch sharper" to dial back radius.
  - Or use /theme-update for explicit hex values.
```

Always include the "Next" hint so users know iteration is cheap and bounded.
