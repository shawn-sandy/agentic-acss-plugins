# style-agent developer guide

## What this plugin is

`style-agent` is a framework-agnostic CSS authoring plugin for Claude Code. It provides skills for writing, extracting, and organising CSS utilities and classes in any web project — plain CSS, SCSS, Tailwind, or any utility-first workflow.

## Install

```text
/plugin install style-agent@shawn-sandy-agentic-acss-plugins
```

## Commands

| Command | What it does |
|---|---|
| `/css-to-class [name]` | Extract utility classes from an HTML element or class string into a single named CSS class |

## Skill

The plugin ships one skill: `skills/css-to-class/SKILL.md`. Command logic delegates to that file.

## Adding new skills

Follow the same pattern — create `skills/<skill-name>/SKILL.md` with `name:` and `description:` front-matter, add a matching command in `commands/<name>.md` that delegates to it.
