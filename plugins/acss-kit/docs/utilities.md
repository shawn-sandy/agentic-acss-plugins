# Utilities — Usage Guide

Tailwind-style atomic CSS utility classes for fpkit/acss projects. A single prebuilt `utilities.css` bundle ships the full atomic suite — spacing, flexbox, grid, color, type, radius, shadow, display, position, and z-index families — plus a `token-bridge.css` alias layer that wires the utilities' color classes up to your acss-kit theme roles.

No build step, no JIT purge — the bundle is complete and you drop it in.

## Add it to your project

Run `/utility-add` to copy the bundle into your project:

```text
/utility-add
/utility-add --target=src/styles
/utility-add --families=spacing,flex,color-bg
/utility-add --no-bridge
```

It detects your utilities directory (default `src/styles/`), copies `utilities.css`, and — unless you pass `--no-bridge` — copies `token-bridge.css` too. If `acss-kit` is installed alongside, it also verifies your CSS entry imports the files it wrote.

If you have already run `/setup` for components and themes, `/utility-add` reuses the same project config (`.acss-target.json`). Utilities work standalone too — without an acss-kit theme, the bridge's hex fallbacks resolve to sensible fpkit-default colors.

## Commands

| Command | Purpose |
|---------|---------|
| `/utility-add [--target=<dir>] [--families=<list>] [--no-bridge]` | Copy `utilities.css` (and `token-bridge.css`) into your project. |
| `/utility-list [family]` | Read-only catalogue printer — list families, or every class in one family. |
| `/utility-tune <natural-language>` | Adjust the spacing baseline, breakpoints, or which families are enabled. |
| `/utility-bridge [--theme=<file>]` | Regenerate `token-bridge.css` aliases against your active theme. |

## Using the classes

Import the bridge **before** the utilities so the color aliases are defined when the utility classes resolve them:

```ts
import "./styles/token-bridge.css";   // first
import "./styles/utilities.css";       // then
```

Then compose classes directly in your markup:

```tsx
// Flex row: spaced children, centered vertically, padded
<div className="flex items-center justify-between p-4 gap-3">…</div>

// Surface card with muted border and rounded corners
<article className="bg-surface border-border rounded-lg shadow p-6">…</article>

// Primary-colored heading text
<h2 className="text-primary font-semibold text-2xl mb-2">Plan</h2>
```

Spacing uses a `0.25rem` baseline (`.m-4` = `1rem`, `.p-8` = `2rem`) and emits CSS logical properties, so `mt`/`mb`/`ml`/`mr` follow the document's writing mode.

**Responsive variants** use a plain hyphen prefix — no escaping needed. Prefixes are `sm` (30rem), `md` (48rem), `lg` (62rem), `xl` (80rem), plus `print`:

```tsx
<div className="hide sm-show">Mobile-only header</div>
<button className="bg-primary p-4 md-p-6 lg-p-8">Padded button</button>
```

Run `/utility-list` to see the enabled families and the spacing/breakpoint scales, or `/utility-list spacing` for every class in a family. The full catalogue is in [`utility-catalogue.md`](../skills/utilities/references/utility-catalogue.md); breakpoint details are in [`breakpoints.md`](../skills/utilities/references/breakpoints.md).

## The token bridge

`utilities.css` references fpkit-style token names (`--color-error`, `--color-error-bg`, `--color-secondary`, `--color-primary-light`) that don't all exist in acss-kit's role catalogue. `token-bridge.css` is the alias layer that maps them onto acss-kit's roles — `--color-error` aliases to `--color-danger`, `-bg` and `-light` variants are synthesized with `color-mix(in oklch, …)`, and every alias is defined for both `:root` and `[data-theme="dark"]`. Regenerate it with `/utility-bridge` whenever your theme changes (a new `/theme-create`, a `/theme-update` edit, or a custom palette) so the utility color classes track your current colors. See [`token-bridge.md`](../skills/utilities/references/token-bridge.md) for the full mapping.

## Related

- [Component index](components/README.md) — components you can style alongside these utilities.
- Utilities skill (maintainer reference): [`skills/utilities/SKILL.md`](../skills/utilities/SKILL.md).
