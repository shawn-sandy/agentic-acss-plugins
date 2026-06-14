---
paths:
  - "**/DESIGN.md"
---

# DESIGN.md Conventions

Advisory reminders when reading or writing a [DESIGN.md](https://github.com/google-labs-code/design.md)
(Google Labs design-token format) in any project. The acss-kit bridge consumes
and produces these — keep them on-spec so the round-trip holds.

- **Front-matter is YAML** with token groups: `colors`, `spacing`, `rounded`,
  `typography` (composite: `fontFamily`/`fontSize`/`fontWeight`/`lineHeight`/
  `letterSpacing`), and a freeform `components` block. Quote hex values
  (`primary: '#855300'`) — a bare `#` opens a YAML comment.
- **A primary color MUST be defined.** acss-kit hard-fails without it — it seeds
  the OKLCH palette. (`validate_design_md.py` treats `missing-primary` as an
  error, stricter than the upstream CLI's warning, by decision.)
- **Section order / headings.** Canonical `##` sections (Overview, Colors,
  Typography, …); duplicate headings are a spec error. `{token.path}` references
  (e.g. `{colors.primary}`) must resolve to a defined token.
- **Role-name translation (Appendix A).** acss-kit maps Material-3 / Figma color
  names to our 18 `--color-*` roles: `on-surface`→`--color-text`,
  `outline-variant`→`--color-border`, `outline`→`--color-border-strong`,
  `error`→`--color-danger`, etc. Roles M3 omits (`success`, `warning`,
  `focus-ring`) are OKLCH-synthesized on import and kept under our names on export.
- **Validation:** `python3 plugins/acss-kit/scripts/validate_design_md.py <file>`
  (shells `npx @google/design.md lint`; needs Node/`npx`). The generators
  (`design_md_to_tokens.py`, `tokens_to_design_md.py`, `figma_to_tokens.py`)
  isolate every name assumption in adapter tables — the reconciliation point
  against the real spec. See `docs/plans/design-md-spec-alignment.md`.
