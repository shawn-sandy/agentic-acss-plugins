# Table — Usage Guide

A semantic HTML table wrapper with compound sub-components: `Table`, `Table.Caption`, `Table.Head`, `Table.Body`, `Table.Row`, `Table.HeaderCell`, and `Table.Cell`. It renders native `<table>`/`<caption>`/`<thead>`/`<tbody>`/`<tr>`/`<th>`/`<td>` elements and carries no opinion on sorting, filtering, or pagination — those are application concerns you layer on top.

## Add it to your project

1. **One-time setup** (run once per project): `/setup` — installs `sass`, writes `.acss-target.json`, and creates the `ui.tsx` foundation every component imports.
2. **Add this component:** `/kit-add Table` — copies `table.tsx` + `table.scss` into your components directory (default `src/components/fpkit/`).
   - Or run `/kit-sync` once to install **all** components, the foundation, and a starter theme together.

The generated component is self-contained — no `@fpkit/acss` install required.

## Import

`Table` is a compound component — the root and all six sub-parts ship in one file.

```tsx
import Table from './fpkit/table/table'
import './fpkit/table/table.scss'
```

Adjust the path to match the `componentsDir` in your `.acss-target.json`.

## Props

**`Table`**

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `aria-label` | `string` | — | Accessible name — alternative to `<Table.Caption>`. |
| `aria-labelledby` | `string` | — | Accessible name reference — alternative to `<Table.Caption>`. |
| `classes` | `string` | — | CSS class(es). |
| `styles` | `React.CSSProperties` | — | Inline styles. |
| `children` | `React.ReactNode` | — | Caption, head, and body sub-components. |

Plus any native `<table>` attribute.

**`Table.HeaderCell`**

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `scope` | `'col' \| 'row' \| 'colgroup' \| 'rowgroup'` | `col` | Header scope; set `row` for row headers, spans for complex tables. |

Plus any native `<th>` attribute.

**`Table.Caption` / `.Head` / `.Body` / `.Row` / `.Cell`** each accept the native props of their element (`<caption>`, `<thead>`, `<tbody>`, `<tr>`, `<td>` respectively).

## Examples

```tsx
// Basic data table with caption
<Table>
  <Table.Caption>Quarterly revenue, 2024</Table.Caption>
  <Table.Head>
    <Table.Row>
      <Table.HeaderCell>Quarter</Table.HeaderCell>
      <Table.HeaderCell>Revenue</Table.HeaderCell>
      <Table.HeaderCell>YoY change</Table.HeaderCell>
    </Table.Row>
  </Table.Head>
  <Table.Body>
    <Table.Row>
      <Table.HeaderCell scope="row">Q1</Table.HeaderCell>
      <Table.Cell>$1.2M</Table.Cell>
      <Table.Cell>+5%</Table.Cell>
    </Table.Row>
    <Table.Row>
      <Table.HeaderCell scope="row">Q2</Table.HeaderCell>
      <Table.Cell>$1.4M</Table.Cell>
      <Table.Cell>+18%</Table.Cell>
    </Table.Row>
  </Table.Body>
</Table>

// Accessible name via aria-labelledby (when caption duplicates a nearby heading)
<>
  <h2 id="users-heading">Active users</h2>
  <Table aria-labelledby="users-heading">
    <Table.Head>
      <Table.Row>
        <Table.HeaderCell>Name</Table.HeaderCell>
        <Table.HeaderCell>Email</Table.HeaderCell>
      </Table.Row>
    </Table.Head>
    <Table.Body>
      <Table.Row>
        <Table.Cell>Alice</Table.Cell>
        <Table.Cell>alice@example.com</Table.Cell>
      </Table.Row>
    </Table.Body>
  </Table>
</>

// Wide table, scrollable wrapper
<div style={{ overflowX: 'auto' }}>
  <Table>
    {/* ...many columns... */}
  </Table>
</div>
```

## Theming

Override these CSS custom properties in your theme to restyle every table. Each has a fallback, so overriding is optional.

| Variable | Purpose |
|----------|---------|
| `--table-width` | Table width (default `100%`). |
| `--table-caption-fw` | Caption font weight. |
| `--table-th-bg` | Header-cell background. |
| `--table-th-padding` / `--table-td-padding` | Header / body cell padding. |
| `--table-th-border-bottom` | Header separator border. |
| `--table-td-border-bottom` | Row separator border. |
| `--table-row-hover-bg` | Row hover background. |

```css
:root {
  --table-th-bg: #f0f0f5;
  --table-row-hover-bg: #f5f3ff;
}
```

Generate a full matching theme with `/theme-create` (see [styles.md](../styles.md)).

## Accessibility

- Always give a data table an accessible name — a `<Table.Caption>` first child (richest, visible to all), `aria-label`, or `aria-labelledby` pointing at a nearby heading.
- `<Table.HeaderCell>` defaults `scope="col"`; pass `scope="row"` for row headers, and `colgroup`/`rowgroup` (or `headers="…"` on cells) for spanning headers in complex tables.
- Keep native table semantics — don't add `role="grid"` unless building a fully interactive grid, and never `role="presentation"` for layout (use CSS Grid/Flexbox instead).
- For wide tables on narrow viewports, prefer a horizontal-scroll wrapper (`overflow-x: auto`) over collapsing rows — scrolling preserves the row-column relationship AT users rely on.
- Header text on `--table-th-bg`, body text, and `--table-row-hover-bg` must all keep text contrast at 4.5:1; row-separator borders used as the sole divider must meet 3:1 (WCAG 1.4.11).

## Related

- [Component index](README.md)
- [List](list.md) — for non-tabular, single-dimension data
- Full maintainer reference: [`skills/component-table/reference.md`](../../skills/component-table/reference.md)
