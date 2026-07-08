# Card — Usage Guide

A flexible container for grouping related content, built as a compound component: `Card`, `Card.Title`, `Card.Content`, and `Card.Footer`. Supports an interactive (whole-card clickable) variant with keyboard support.

## Add it to your project

1. **One-time setup** (run once per project): `/setup` — installs `sass`, writes `.acss-target.json`, and creates the `ui.tsx` foundation every component imports.
2. **Add this component:** `/kit-add Card` — copies `card.tsx` + `card.scss` into your components directory (default `src/components/fpkit/`).
   - Or run `/kit-sync` once to install **all** components, the foundation, and a starter theme together.

The generated component is self-contained — no `@fpkit/acss` install required. All four sub-components ship in a single `card.tsx`.

## Import

```tsx
import Card from './fpkit/card/card'
import './fpkit/card/card.scss'
```

`Card.Title`, `Card.Content`, and `Card.Footer` are attached to the default export — no extra imports. Adjust the path to match the `componentsDir` in your `.acss-target.json`.

## Props

`Card` (root):

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `as` | `React.ElementType` | `div` | Element to render as (e.g. `article`, `section`). |
| `children` | `React.ReactNode` | — | Card content, typically the sub-components. |
| `interactive` | `boolean` | `false` | Makes the whole card clickable + keyboard-navigable. |
| `onClick` | `() => void` | — | Click handler (required when `interactive`). |
| `classes` | `string` | — | CSS class names. |
| `styles` | `React.CSSProperties` | — | Inline styles. |

Sub-components — `Card.Title` (`as` default `h3`, plus `id`, `className`), `Card.Content` (`as` default `article`), `Card.Footer` (`as` default `div`). Each also accepts `children` and native attributes for its element.

## Examples

```tsx
// Basic card
<Card>
  <Card.Title>Product Name</Card.Title>
  <Card.Content>
    <p>Product description here...</p>
  </Card.Content>
  <Card.Footer>
    <button>Buy Now — $29.99</button>
  </Card.Footer>
</Card>

// Accessible card with linked title
<Card as="article" aria-labelledby="product-1">
  <Card.Title id="product-1">Featured Widget</Card.Title>
  <Card.Content>
    <p>Best widget on the market.</p>
  </Card.Content>
</Card>

// Interactive card (entire card is clickable)
<Card
  interactive
  aria-label="View article: 5 Tips for Better Code"
  onClick={() => navigate('/articles/1')}
>
  <Card.Title>5 Tips for Better Code</Card.Title>
  <Card.Content>
    <p>Learn how to write cleaner code...</p>
  </Card.Content>
</Card>

// Custom heading level for document outline
<Card as="section">
  <Card.Title as="h2">Section Title</Card.Title>
  <Card.Content>Content here...</Card.Content>
</Card>
```

## Theming

Override these CSS custom properties in your theme to restyle every card. Each has a fallback, so overriding is optional.

| Variable | Purpose |
|----------|---------|
| `--card-bg` / `--card-color` | Card background/text. |
| `--card-radius` | Corner radius. |
| `--card-border` / `--card-shadow` | Border and drop shadow. |
| `--card-title-fs` / `--card-title-padding` | Title size and padding. |
| `--card-content-padding` | Content region padding. |
| `--card-footer-bg` / `--card-footer-padding` | Footer background and padding. |
| `--card-interactive-hover-shadow` / `--card-interactive-hover-transform` | Hover feedback on interactive cards. |
| `--card-focus-outline` | Focus ring on interactive cards. |

```css
:root {
  --card-radius: 0.75rem;
  --card-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}
```

Generate a full matching theme with `/theme-create` (see [styles.md](../styles.md)).

## Accessibility

- Non-interactive cards carry no interactive semantics. For a semantic association with the title, use `as="article"` and link it with `aria-labelledby` pointing at `Card.Title`'s `id`.
- Interactive cards get `role="button"`, `tabIndex={0}`, and Enter/Space activation. Always pass an `aria-label` describing what activating the card does — the text content is not always a complete accessible name.
- Avoid nesting other interactive elements (links, buttons) inside an interactive card; prefer a non-interactive card with an explicit action instead.
- `Card.Title` defaults to `<h3>`. Set `as="h2"` etc. to keep the document outline correct — never skip heading levels.
- Interactive cards show a `:focus-visible` outline and easily exceed the 44 px target-size minimum.

## Related

- [Component index](README.md)
- Full maintainer reference: [`skills/component-card/reference.md`](../../skills/component-card/reference.md)
