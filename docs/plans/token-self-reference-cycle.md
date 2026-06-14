---
status: completed
type: fix
created: 2026-06-14
repo-name: acss-plugins
---

# Plan: fix self-referential token definitions (cyclic `var(--x, …)`)

> Surfaced by a **Codex review on PR #86** (the button token-sweep pilot). The
> token generators emit *definitions* that reference themselves, which is a CSS
> dependency cycle — so generated token files likely don't actually theme
> components. **Pre-existing and repo-wide** (the color system shares the
> pattern), so this is tracked as a **dedicated fix**, separate from PR 2 (which
> stays scoped to the button sweep and is unaffected — components are *consumers*
> and use the correct nested-fallback form).

## The finding

`_tokens.py` emits token **definitions** as self-references:

```css
:root {
  --color-primary: var(--color-primary, #4f46e5);   /* format_palette  (_tokens.py:125) — colors, pre-existing */
  --space-sm:      var(--space-sm, 0.5rem);          /* format_scales   (_tokens.py:212) — PR 1 */
  --radius-md:     var(--radius-md, 0.5rem);
  --font-label-md-weight: var(--font-label-md-weight, 600);  /* format_typography (_tokens.py:231) — PR 1 */
}
```

A custom property whose value references **itself** is a **CSS dependency
cycle** → it computes to the *guaranteed-invalid value*. A consumer like
`gap: var(--btn-gap, var(--space-sm, 0.5rem))` then finds `--space-sm` invalid
and falls through to the innermost literal. **Net: loading the generated token
files does not theme the component** — it always renders the hardcoded fallback.

The same applies to colors: `--color-primary: var(--color-primary, #hex)` is
cyclic, so `var(--color-primary, …)` in components/utilities falls to their own
fallback rather than the theme value. (Foundation intentionally omits `--color-*`
— P1 — so there is no non-cyclic definition elsewhere to break the cycle.)

The **consumer** side is correct and unaffected: token-bridge.css, the
`color-*` utilities, and component SCSS all use `var(--token, fallback)` to
*read* a token — that's the right pattern. Only the **definition** emit is wrong.

## Why our tests don't catch it

- `validate_theme.py` reads the **fallback hex** out of `var(--x, #hex)` (via
  `resolve_hex`), so contrast passes regardless of runtime cascade.
- The e2e jsdom/axe path doesn't resolve custom-property **cycles** like a real
  browser, so rendered-HTML tests stay green.

Neither exercises the actual cascade, so this stayed latent.

## Step 1 — Verify in a real browser (do this first)

Before any cross-cutting change, confirm the behavior empirically — the blast
radius (regenerating every theme file) warrants certainty:

```html
<style>
  :root { --x: var(--x, 10px); }   /* current (self-ref) pattern */
  :root { --y: 10px; }             /* proposed (raw) pattern */
  #a { width: var(--x, 99px); }    /* expect 99px if --x is cyclic/invalid */
  #b { width: var(--y, 99px); }    /* expect 10px */
</style>
<div id="a"></div><div id="b"></div>
```

- *Verify:* `#a` computes to **99px** (confirms the self-ref is cyclic → broken)
  and `#b` to **10px** (confirms the raw definition + consumer-fallback works).
  If `#a` is 10px, the pattern is fine and this plan is moot — close it.

> **Result (2026-06-14, real Chromium via Playwright).** Ran the equivalent test
> — a "theme" sets both a self-ref token (`--t: var(--t, 2rem)`) and a raw token
> (`--t: 2rem`), each consumed as button does (`var(--btn-x, var(--t, 0.5rem))`):
> the **self-ref consumer = `8px`** (0.5rem literal — theme's 2rem ignored), the
> **raw consumer = `32px`** (2rem — theme applies). Confirmed: self-referential
> definitions are cyclic and do not theme; raw definitions work. **Implemented**
> (Steps 2–3 below).

## Step 2 — Fix the emit format (definitions raw, consumers unchanged)

Change the three writers in `_tokens.py` to emit **raw values** for definitions:

```diff
- {role}: var({role}, {palette[role]});
+ {role}: {palette[role]};
- {prefix}{name}: var({prefix}{name}, {value});
+ {prefix}{name}: {value};
- {FONT_PREFIX}{role}-{key}: var({FONT_PREFIX}{role}-{key}, {sub[key]});
+ {FONT_PREFIX}{role}-{key}: {sub[key]};
```

- *Why:* a theme file's job is to **set** the token; consumers already provide
  the `var(--token, fallback)` read. *Verify:* generated `light.css` reads
  `--color-primary: #4f46e5;`; a browser test with the generated file + a
  consumer shows the themed value applies.

## Step 3 — Ripple (all within the generator/assets boundary)

- **Round-trip still works** — `resolve_hex` extracts `#hex` from a raw value
  (its `_HEX_RE` already matches), and `resolve_fallback` returns a raw
  dimension unchanged. `css_to_tokens.py` needs no logic change; **verify** the
  round-trip self-tests still pass (their *assertions* on `var(--x, val)` output
  must be updated to the raw form).
- **Update self-tests** — `tokens_to_css.py` / `css_to_tokens.py` self-tests
  assert the `var(--x, val)` output shape; change to raw.
- **Regenerate bundled assets** — `assets/tokens/space-radius.css` and
  `typography.css` (and any shipped starter theme) to raw form.
- **Update the convention docs** — `tokens_to_css.py` docstring and CLAUDE.md
  ("Every var() reference includes a hardcoded fallback") to clarify the
  fallback rule applies to **consumers**, not token **definitions**.
- **PR 2 golden is unaffected** — `button.scss` is a consumer (nested `var()`);
  its golden doesn't change. Theme files aren't golden-tested.

## Scope, risk, compatibility

- **Blast radius: the color system.** Changing `format_palette` re-shapes every
  generated `light.css`/`dark.css`/`brand-*.css`. This is the bulk of the risk —
  hence Step 1's empirical gate.
- **Migration:** existing user theme files (self-ref) stay broken until
  regenerated; the fix makes *new* output correct. Note in the release/CHANGELOG;
  consider a one-line `/theme-update`-style note or a codemod.
- **Backward compatibility of the round-trip:** raw definitions parse fine
  (verified above), so `/theme-extract` and `/style-tune` keep working.

## Out of scope

- PR 2 (button sweep) — already merged/scoped; components are consumers and need
  no change.
- Token-bridge / utility consumer files — already correct.

## Next step

Run Step 1 in a browser to confirm, then implement Steps 2–3 as a dedicated PR
(`acss-kit` minor bump — it materially changes generated theme output). If Step 1
shows the pattern works, close this plan.
