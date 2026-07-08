# style-agent developer guide

## What this plugin is

`style-agent` is a framework-agnostic CSS authoring plugin for Claude Code. It provides skills for writing, extracting, and organising CSS utilities and classes in any web project — plain CSS, SCSS, Tailwind, or any utility-first workflow.

## Install

```text
/plugin marketplace add shawn-sandy/agentic-acss-plugins
/plugin install style-agent@shawn-sandy-agentic-acss-plugins
```

## Commands

| Command | What it does |
|---|---|
| `/css-to-class [name]` | Extract utility classes from an HTML element or class string into a single named CSS class |
| `/inline-style-to-class [name]` | Convert an inline style attribute, JSX style object, or `<style>` block into a named CSS class and append it to the project stylesheet, replacing hard-coded values with CSS variables (reuse-or-create) |
| `/create-utilities [description]` | Generate a utility class string from a plain-language visual description |

For per-command usage guides (when to use, how to run, before/after examples), see [`docs/commands/`](commands/README.md).

## Skills

The plugin ships three skills. Command logic delegates to each skill file.

- `skills/css-to-class/SKILL.md`
- `skills/inline-style-to-class/SKILL.md`
- `skills/create-utilities/SKILL.md`

## Specifications

`style-agent` publishes the **COMPONENT.md** spec — a framework-neutral format
for describing a component's structure, props, behavior, and accessibility that
an agent projects into any framework (React, HTML, Astro, Angular, Vue, Svelte,
web-component), themed by a sibling [DESIGN.md](https://github.com/google-labs-code/design.md).
Together they form a two-file design system: DESIGN.md owns tokens, COMPONENT.md
owns components.

- [`docs/component-md/spec.md`](component-md/spec.md) — the specification.
- [`docs/component-md/examples/button.component.md`](component-md/examples/button.component.md) — a complete, conformant example.

## Adding new skills

Follow the same pattern — create `skills/<skill-name>/SKILL.md` with `name:` and `description:` front-matter, add a matching command in `commands/<name>.md` that delegates to it.
