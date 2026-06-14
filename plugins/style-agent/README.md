# style-agent

Write, extract, and organise CSS utilities and classes for any web project. Framework-agnostic — works with plain CSS, compiled SCSS output, Tailwind, or any utility-first workflow. Declaration lookup reads `.css` files in your project, so SCSS source files are supported via their compiled output.

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

```text
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

### `/inline-style-to-class [name]`

Convert an inline `style` attribute, JSX `style={{ ... }}` object, or `<style>` block into a single, semantically named CSS class and append it to the project stylesheet. Hard-coded colors, units, and values are replaced with CSS variables — reusing an existing variable when one already holds that value, and creating a new one (declared in your tokens file or a `:root` block) when none does. Values already written as `var(...)` pass through untouched, and the original literal is kept as the `var()` fallback.

**Input** — paste an HTML element, JSX markup, or a `<style>` block:

```html
<div style="background: #2563eb; padding: 1rem">
```

```jsx
<Button style={{ backgroundColor: theme.primary, padding: 8 }}>
```

**Output** — a ready-to-use CSS class appended to your project stylesheet, plus refactored source. Hard-coded values are tokenized (here `#2563eb` matched an existing `--color-primary`; `1rem` had no match, so `--space-1rem` was created):

```css
/* from: style attr on <div> */
.div-bg {
  background: var(--color-primary, #2563eb);
  padding: var(--space-1rem, 1rem);
}
```

```html
<div class="div-bg">
```

**Name rules** — max 20 characters, kebab-case. Omit `name` to auto-generate from the element tag and first declared property.

### `/create-utilities [description]`

Generate a utility class string from a plain-language description of visual intent. Detects the project's utility framework (acss-kit, Tailwind, Bootstrap, or Tailwind-compatible fallback) and maps the description to specific class names.

**Input** — describe what you want in plain language:

```text
a centered flex row with 1rem gap and a primary background
```

```text
primary submit button with hover state
```

**Output** — a class string and a one-line HTML example:

```text
flex items-center gap-4 bg-primary focus-visible:ring
```

```html
<button class="flex items-center gap-4 bg-primary focus-visible:ring">Label</button>
```

For interactive elements (button, link, input), focus styling is handled automatically — `focus-visible:ring` for Tailwind/fallback projects, `focus-ring` for Bootstrap. For acss-kit, the skill warns in the summary that no focus utility exists in the bundle and suggests adding `:focus-visible` CSS to your project or using an acss-kit component class. Run `/css-to-class [name]` on the output to consolidate into a single named CSS class.

## Specifications

### COMPONENT.md

A framework-neutral format for describing a component's structure, props,
behavior, and accessibility that an agent projects into **any** framework
(React, HTML, Astro, Angular, Vue, Svelte, web-component), themed by a sibling
[DESIGN.md](https://github.com/google-labs-code/design.md). Together they form a
two-file design system — DESIGN.md owns tokens, COMPONENT.md owns components,
coupled through `{token.path}` references.

- Spec: [`docs/component-md/spec.md`](docs/component-md/spec.md)
- Example: [`docs/component-md/examples/button.component.md`](docs/component-md/examples/button.component.md)

## Developer guide

See [`docs/README.md`](docs/README.md).
