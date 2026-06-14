# Theme JSON Schema

> **⚠️ Internal-only contract — not a user-facing authoring format.**
>
> The user-facing authoring format is the **CSS Token Convention** documented in [`SKILL.md`](../SKILL.md). Users edit CSS theme files (`light.css`, `dark.css`, `brand-*.css`) directly — no JSON authoring is required or recommended.
>
> The JSON schema is retained as an **internal contract** for [`scripts/tokens_to_css.py`](../../../scripts/tokens_to_css.py) and [`scripts/css_to_tokens.py`](../../../scripts/css_to_tokens.py), which use it to translate between the OKLCH palette generator's output and CSS theme files. End users do not need to read or write JSON conforming to this schema.
>
> This document is preserved as a reference for contributors maintaining the round-trip scripts. The schema file itself (`assets/theme.schema.json`) carries `"deprecated": true` to discourage user authoring.

`assets/theme.schema.json` is a JSON Schema (Draft-07) describing the structure of a `theme.tokens.json` file. The file is **internal-only** — the round-trip scripts read/write JSON conforming to it, but no user-facing flow asks the developer to author one.

## Top-level structure

```json
{
  "modes": {
    "light": { ...palette },
    "dark":  { ...palette }
  },
  "brands": {
    "forest": { ...brand-overrides },
    "coral":  { ...brand-overrides }
  }
}
```

- `modes.light` and `modes.dark` are each a full palette object (all required roles).
- `brands` is optional; each key maps to a `brand-overrides` object with only the roles being overridden (primary + optional accent).

## Palette object

All role names are constrained to the enum in `role-catalogue.md`. Values are hex colors only: `#rrggbb` or `#rgb`.

```json
{
  "--color-background":    "#ffffff",
  "--color-surface":       "#f9fafb",
  "--color-surface-raised":"#ffffff",
  "--color-text":          "#111827",
  "--color-text-muted":    "#4b5563",
  "--color-text-inverse":  "#ffffff",
  "--color-border":        "#e5e7eb",
  "--color-border-strong": "#d1d5db",
  "--color-primary":       "#4f46e5",
  "--color-primary-hover": "#4338ca",
  "--color-success":       "#0a7d3b",
  "--color-warning":       "#ae7100",
  "--color-danger":        "#b42318",
  "--color-info":          "#4f46e5",
  "--color-focus-ring":    "#4f46e5"
}
```

Required roles: all 15 listed above. Optional: `--color-surface-subtle`, `--color-text-subtle`, `--color-brand-accent`.

## Brand overrides object

Only primary/accent roles. Background, text, and border roles must NOT appear in brand overrides — those are mode-level concerns.

```json
{
  "--color-primary":       "#0f766e",
  "--color-primary-hover": "#0d6b63",
  "--color-focus-ring":    "#0f766e"
}
```

Optional: `--color-brand-accent`.

## Non-color token sections (DESIGN.md parity)

Three optional, **mode-independent** top-level sections carry the typography,
spacing, and rounded tokens that bring our token layer to DESIGN.md parity. They
are additive — colors-only input still produces only `light.css` / `dark.css`.

```json
{
  "spacing":   { "xs": "0.25rem", "sm": "0.5rem", "md": "1rem", "lg": "1.5rem", "xl": "2rem", "2xl": "3rem" },
  "rounded":   { "none": "0", "sm": "0.25rem", "md": "0.5rem", "lg": "1rem", "xl": "1.5rem", "full": "9999px" },
  "typography": {
    "body-md": { "family": "system-ui, sans-serif", "size": "1rem", "weight": "400", "line": "1.5", "tracking": "0.01em" }
  }
}
```

- `spacing` / `rounded` are `map<name, dimension>` (a dimension is `0` or a
  number with a `px`/`em`/`rem` unit). Emitted to **`space-radius.css`** as
  `--space-<name>` and `--radius-<name>`.
- `typography` is `map<role, composite>`; each composite has optional
  `family` / `size` / `weight` / `line` / `tracking`. Emitted to
  **`typography.css`** as `--font-<role>-<sub>`.
- The CSS prefixes are **not** drop-in Tailwind v4 `@theme` names: acss-kit uses
  `--space-*` and composite `--font-<role>-*` tokens, whereas Tailwind uses
  `--spacing-*` and the split `--text-*` / `--font-weight-*` / `--leading-*` /
  `--tracking-*` namespaces (only `--radius-*` matches), so a DESIGN.md
  `css-tailwind` export needs a name adapter rather than a mechanical prefix remap.
- Default scales ship at [`assets/tokens/space-radius.css`](../../../assets/tokens/space-radius.css)
  and [`assets/tokens/typography.css`](../../../assets/tokens/typography.css) for
  projects with no DESIGN.md.
- Structural validation (dimension units, scale completeness, typography
  sub-props) is handled by [`scripts/validate_tokens.py`](../../../scripts/validate_tokens.py)
  — the dimension/typography counterpart to `validate_theme.py`'s contrast gate.

## Round-tripping

CSS → JSON:

```bash
python3 scripts/css_to_tokens.py src/styles/theme/light.css src/styles/theme/dark.css \
  > theme.tokens.json
```

JSON → CSS:

```bash
python3 scripts/tokens_to_css.py theme.tokens.json --out-dir src/styles/theme/
```

The round-trip is semantically lossless: only whitespace and comment ordering may differ in the CSS output.

## Schema validation (manual)

No external runtime is required. Claude Code validates the JSON structure during `/theme-extract` when it calls `css_to_tokens.py` and checks the output against the schema inline. For local validation with a JSON Schema tool:

```bash
# with jsonschema (pip install jsonschema)
python3 -m jsonschema -i theme.tokens.json \
  plugins/acss-kit/assets/theme.schema.json
```
