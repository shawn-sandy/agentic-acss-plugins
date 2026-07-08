# Component Usage Guides

Consumer-facing guides for using each `acss-kit` component in your own React project. Each guide covers: how to add the component, how to import it, its props, copy-paste examples, theming variables, and accessibility notes.

> These are **consumer** guides. The canonical, verified-against-fpkit source for each component lives in `skills/component-<name>/reference.md`.

## First time here?

1. Run `/setup` once — installs `sass`, creates the `ui.tsx` foundation, writes `.acss-target.json`, and seeds a starter theme.
2. Add a component with `/kit-add <Name>`, or install everything at once with `/kit-sync`.
3. Import the generated `.tsx` + `.scss` pair and use it.

See the [tutorial](../tutorial.md) for a full walkthrough and [concepts](../concepts.md) for the mental model.

## Components

| Component | What it is |
|-----------|-----------|
| [Alert](alert.md) | Status/feedback message banner. |
| [Button](button.md) | Primary interactive element with size/style/color variants. |
| [Card](card.md) | Content container with header/body/footer regions. |
| [Checkbox](checkbox.md) | Accessible checkbox input. |
| [Dialog](dialog.md) | Modal dialog / `<dialog>` wrapper. |
| [Field](field.md) | Label + control + help/error wrapper for forms. |
| [Icon](icon.md) | Inline SVG icon. |
| [Icon Button](icon-button.md) | Icon-only button. |
| [Img](img.md) | Responsive image with aspect-ratio control. |
| [Input](input.md) | Text input control. |
| [Link](link.md) | Styled anchor / router-agnostic link. |
| [List](list.md) | Ordered/unordered list wrapper. |
| [Nav](nav.md) | Navigation landmark with links. |
| [Popover](popover.md) | Anchored popover / tooltip. |
| [Table](table.md) | Data table with accessible structure. |

## Styles and utilities

| Guide | What it covers |
|-------|---------------|
| [Styles (theming)](../styles.md) | OKLCH light/dark themes, brand presets, theme-role edits, token extraction. |
| [Utilities (atomic CSS)](../utilities.md) | Tailwind-style utility classes, breakpoints, the token bridge. |
