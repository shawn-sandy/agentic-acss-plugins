---
description: Convert an inline style attribute, JSX style object, or <style> block into a named CSS class and append it to the project stylesheet
argument-hint: [name]
allowed-tools: Read, Glob, Grep, Bash, Write, Edit, AskUserQuestion
---

Convert an inline `style` attribute, JSX `style` object, or `<style>` block into a single named CSS class appended to the project stylesheet.

Follow `${CLAUDE_PLUGIN_ROOT}/skills/inline-style-to-class/SKILL.md`.

All behavior — argument handling, input parsing, name rules, stylesheet discovery, class emission, file append, HTML/JSX refactoring, and summary output — is defined in the skill file above.
