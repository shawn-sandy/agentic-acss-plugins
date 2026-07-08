# Styles — Usage Guide

The theming system for fpkit/acss projects. It generates OKLCH light/dark themes as plain CSS custom properties — a fixed set of semantic **role** tokens (`--color-primary`, `--color-surface`, `--color-text`, …) that every component reads. You seed a theme from a single hex color and the palette math derives the rest, validating each theme against WCAG 2.2 AA contrast before it lands.

You never author JSON. Themes are CSS files you own, edit, and commit.

## Add it to your project

1. **One-time setup** (run once per project): `/setup` — installs `sass`, writes `.acss-target.json`, copies the `ui.tsx` foundation, and (unless you pass `--no-theme`) seeds `src/styles/theme/light.css` + `dark.css` from a seed hex color. It also appends the `@import` lines to your CSS entry.
2. **Generate or refine themes** with the commands below. `/theme-create` is the usual starting point if you skipped the seed step, or when you want to regenerate from a new color.

Themes are committed artifacts — keep `src/styles/theme/` in version control, not `.gitignore`.

## Commands

| Command | Purpose |
|---------|---------|
| `/theme-create <hex> [--mode=light\|dark\|both]` | Generate `light.css` / `dark.css` from a seed color using OKLCH palette math. |
| `/theme-brand <name> [--from=<hex>]` | Scaffold `brand-<name>.css` with primary/accent overrides that layer over light/dark. |
| `/theme-update <file> <--color-role=#hex> [...]` | Edit specific role values in a theme file and re-validate (reverts changes that fail AA). |
| `/theme-extract <image\|figma-url>` | Extract brand colors from an image or Figma design, then generate theme CSS. |
| `/theme-from-design <DESIGN.md>` | Generate a full theme — colors plus spacing/rounded/typography — from a DESIGN.md file. |
| `/theme-from-figma <figma-url\|fileKey>` | Generate a theme from a Figma file's variables via the Figma MCP server. |
| `/color-scale <color> [--name=<name>] [--format=css\|json\|both]` | Generate a 10-step OKLCH scale (50–900) from a hex, CSS named color, or theme role. |
| `/design-export [--format=design-md\|dtcg\|tailwind]` | Export the project's theme back out as a DESIGN.md (or DTCG/Tailwind via the upstream CLI). |

Every write-bearing command runs the WCAG contrast validator automatically before finishing.

## How themes are consumed

Generated theme files live under `src/styles/theme/`:

- `light.css` — semantic role tokens under `:root`
- `dark.css` — the same roles under `[data-theme="dark"]`
- `brand-<name>.css` — optional primary/accent overrides layered on top

Import them into your app's CSS entry **after** `foundation.css` so theme values win the cascade:

```css
/* src/styles/index.css */
@import "./foundation.css";
@import "./theme/light.css";
@import "./theme/dark.css";
@import "./theme/brand-forest.css"; /* optional — after light + dark */
```

Toggle dark mode by setting `data-theme="dark"` on the `<html>` element.

Components never hardcode colors — they read the role tokens with a fallback, so they render correctly with or without a theme present:

```scss
.btn[data-color="primary"] {
  background: var(--btn-primary-bg, var(--color-primary, #0066cc));
  color: var(--btn-primary-color, var(--color-text-inverse, #fff));
}
```

Override a role in your theme file and every component that reads it restyles at once — that CSS-custom-property layer is the whole contract between styles and components.

## Theme roles

A theme defines 18 `--color-*` roles (15 required + 3 optional), grouped by purpose. Below are the categories with a couple of examples each; the full list with contrast pairings is in [`role-catalogue.md`](../skills/styles/references/role-catalogue.md).

| Category | Examples | Purpose |
|----------|----------|---------|
| Backgrounds | `--color-background`, `--color-surface`, `--color-surface-raised` | Page, cards/panels, elevated surfaces (modals, popovers). |
| Text | `--color-text`, `--color-text-muted`, `--color-text-inverse` | Body copy, secondary text, text on a primary background. |
| Borders | `--color-border`, `--color-border-strong` | Default and emphasized (form-focus) borders. |
| Brand & semantic | `--color-primary`, `--color-primary-hover`, `--color-success`, `--color-warning`, `--color-danger`, `--color-info` | Brand action color and state colors. |
| Focus | `--color-focus-ring` | Keyboard focus indicator; usually equals `--color-primary`. |
| Optional | `--color-surface-subtle`, `--color-text-subtle`, `--color-brand-accent` | Tertiary surfaces/text and secondary brand accent. |

Beyond colors, a theme can also carry **mode-independent** dimension tokens — `space-radius.css` (`--space-*`, `--radius-*`) and `typography.css` (`--font-<role>-*`) — emitted when the source (a DESIGN.md, for example) provides them.

## Related

- [Component index](components/README.md) — components that consume these roles.
- Styles skill (maintainer reference): [`skills/styles/SKILL.md`](../skills/styles/SKILL.md).
