---
name: 'acss-kit'
colors:
  background: '#ffffff'
  surface: '#f3f5fc'
  surface-container-high: '#ffffff'
  on-surface: '#030307'
  on-surface-variant: '#75767d'
  on-primary: '#ffffff'
  outline-variant: '#dee1ec'
  outline: '#ced0db'
  primary: '#6266ee'
  primary-container: '#4e4dd3'
  tertiary: '#6266ee'
  error: '#861118'
  success: '#095717'
  warning: '#604008'
  focus-ring: '#6266ee'
spacing:
  xs: '0.25rem'
  sm: '0.5rem'
  md: '1rem'
  lg: '1.5rem'
  xl: '2rem'
  2xl: '3rem'
rounded:
  none: '0'
  sm: '0.25rem'
  md: '0.5rem'
  lg: '1rem'
  xl: '1.5rem'
  full: '9999px'
typography:
  headline-lg:
    fontFamily: 'system-ui, sans-serif'
    fontSize: '2rem'
    fontWeight: 700
    lineHeight: 1.2
  headline-md:
    fontFamily: 'system-ui, sans-serif'
    fontSize: '1.5rem'
    fontWeight: 700
    lineHeight: 1.25
  body-lg:
    fontFamily: 'system-ui, sans-serif'
    fontSize: '1.125rem'
    fontWeight: 400
    lineHeight: 1.6
  body-md:
    fontFamily: 'system-ui, sans-serif'
    fontSize: '1rem'
    fontWeight: 400
    lineHeight: 1.5
  body-sm:
    fontFamily: 'system-ui, sans-serif'
    fontSize: '0.875rem'
    fontWeight: 400
    lineHeight: 1.5
  label-md:
    fontFamily: 'system-ui, sans-serif'
    fontSize: '0.875rem'
    fontWeight: 600
    lineHeight: 1.4
    letterSpacing: '0.01em'
  label-sm:
    fontFamily: 'system-ui, sans-serif'
    fontSize: '0.75rem'
    fontWeight: 500
    lineHeight: 1.3
    letterSpacing: '0.02em'
---

# acss-kit

> **Dogfood fixture.** This is acss-kit's own default theme, published as a
> [DESIGN.md](https://github.com/google-labs-code/design.md) by the real
> `/design-export` pipeline (`generate_palette.py` → `tokens_to_css.py` →
> `tokens_to_design_md.py`, seed `#4f46e5`). It is the *tokens* half of the
> two-file design system; the 15 `plugins/acss-kit/skills/component-*/*.component.md`
> files are the *components* half, and every `{token.path}` they reference
> resolves against the front-matter above. `tests/run.sh` step 7g asserts that
> coupling holds. Regenerate with the command in `tests/fixtures/design-md/README.md`.
>
> **Semantic round-trip** (value-preserving, not byte-identical): the 18
> `--color-*` roles are emitted under DESIGN.md token names. M3 ladder tokens our
> theme does not model (`surface-tint`, the `*-container` pairs, `*-fixed*`) are
> not reproduced; roles with no M3 slot (`success`, `warning`, `focus-ring`,
> `text-subtle`) keep our names and round-trip.

## Overview

The neutral baseline acss-kit ships when a project provides no brand of its own:
an indigo primary (`#4f46e5` seed, contrast-tuned to `#6266ee`) on a near-white
surface, system-ui type, and a six-step spacing/radius scale. Swap the `primary`
color and regenerate to rebrand — every component re-themes through the
`{token.path}` references below.

## Colors

| DESIGN.md token | acss-kit role | Value |
|---|---|---|
| `background` | `--color-background` | `#ffffff` |
| `surface` | `--color-surface` | `#f3f5fc` |
| `surface-container-high` | `--color-surface-raised` | `#ffffff` |
| `on-surface` | `--color-text` | `#030307` |
| `on-surface-variant` | `--color-text-muted` | `#75767d` |
| `on-primary` | `--color-text-inverse` | `#ffffff` |
| `outline-variant` | `--color-border` | `#dee1ec` |
| `outline` | `--color-border-strong` | `#ced0db` |
| `primary` | `--color-primary` | `#6266ee` |
| `primary-container` | `--color-primary-hover` | `#4e4dd3` |
| `tertiary` | `--color-info` | `#6266ee` |
| `error` | `--color-danger` | `#861118` |
| `success` | `--color-success` | `#095717` |
| `warning` | `--color-warning` | `#604008` |
| `focus-ring` | `--color-focus-ring` | `#6266ee` |

## Typography

| Style | Family | Size | Weight | Line |
|---|---|---|---|---|
| `headline-lg` | system-ui, sans-serif | 2rem | 700 | 1.2 |
| `headline-md` | system-ui, sans-serif | 1.5rem | 700 | 1.25 |
| `body-lg` | system-ui, sans-serif | 1.125rem | 400 | 1.6 |
| `body-md` | system-ui, sans-serif | 1rem | 400 | 1.5 |
| `body-sm` | system-ui, sans-serif | 0.875rem | 400 | 1.5 |
| `label-md` | system-ui, sans-serif | 0.875rem | 600 | 1.4 |
| `label-sm` | system-ui, sans-serif | 0.75rem | 500 | 1.3 |

## Spacing & Radius

**spacing** — `xs` 0.25rem, `sm` 0.5rem, `md` 1rem, `lg` 1.5rem, `xl` 2rem, `2xl` 3rem

**rounded** — `none` 0, `sm` 0.25rem, `md` 0.5rem, `lg` 1rem, `xl` 1.5rem, `full` 9999px

## Components

Each shipped component's `tokens:` map references the primitives above by
`{token.path}` — never `components.*`. This is the coupling the dogfood test
exercises (component → token → DESIGN.md).

| Component | DESIGN.md tokens consumed |
|---|---|
| `alert` | `colors.surface` `colors.tertiary` `colors.success` `colors.warning` `colors.error` `rounded.md` `spacing.md` `typography.body-sm` `typography.label-md` |
| `button` | `colors.primary` `colors.on-primary` `rounded.md` `spacing.sm` `spacing.md` `typography.label-md` |
| `card` | `colors.surface` `colors.on-surface` `colors.outline-variant` `rounded.md` `spacing.lg` `spacing.md` |
| `checkbox` | `colors.surface` `colors.primary` `colors.outline-variant` `colors.on-surface` `colors.error` `rounded.sm` `spacing.sm` `typography.body-md` |
| `dialog` | `colors.surface` `colors.on-surface` `rounded.md` `spacing.lg` `spacing.md` `typography.headline-md` |
| `field` | `colors.on-surface` `spacing.sm` `spacing.md` `spacing.xs` `typography.label-sm` |
| `icon` | `colors.on-surface` |
| `icon-button` | `colors` (inherited) `rounded.full` `spacing.xl` `spacing.sm` `typography.label-md` |
| `img` | `rounded.none` |
| `input` | `colors.surface` `colors.on-surface` `colors.outline-variant` `colors.primary` `colors.error` `colors.success` `rounded.md` `spacing.md` `spacing.sm` |
| `link` | `colors.primary` |
| `list` | `colors.primary` `spacing.lg` `spacing.sm` `spacing.xs` `spacing.md` |
| `nav` | `colors.on-surface` `colors.primary` `rounded.sm` `spacing.md` `spacing.sm` |
| `popover` | `colors.surface` `colors.on-surface` `colors.outline-variant` `rounded.md` `spacing.sm` `spacing.md` |
| `table` | `colors.surface` `colors.on-surface` `colors.surface-container-high` `colors.outline-variant` `typography.label-md` |
