# style-agent

Write, extract, and organise CSS utilities and classes for any web project. Framework-agnostic — works with plain CSS, SCSS, Tailwind, or any utility-first workflow.

## Install

```text
/plugin marketplace add shawn-sandy/agentic-acss-plugins
/plugin install style-agent@shawn-sandy-agentic-acss-plugins
```

## Commands

### `/css-to-class [name]`

Extract a list of CSS utility classes from an HTML element or class string into a single, semantically named CSS class.

**Input** — paste an HTML element or a plain class list:

```html
<div class="testimonial flex-grid py-8 items-center" data-flex-grid>
```

```
testimonial flex-grid py-8 items-center
```

**Output** — a ready-to-use CSS class with declarations resolved from your project's own CSS files, plus the refactored HTML:

```css
/* extracted: testimonial flex-grid py-8 items-center */
.testimonial-grid {
  /* testimonial: add declarations manually */
  /* flex-grid: add declarations manually */
  padding-block: 2rem;
  align-items: center;
}
```

```html
<div class="testimonial-grid" data-flex-grid>
```

**Name rules** — max 20 characters, kebab-case. Omit `name` to auto-generate from the most semantic tokens in the class list.

## Developer guide

See [`docs/README.md`](docs/README.md).
